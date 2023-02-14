"""
filter.py
"""
from typing import overload, TYPE_CHECKING
if TYPE_CHECKING:
    from zipline.pipeline.factors.factor import Factor, BooleanFactor
    from zipline.pipeline.classifiers import Classifier
from itertools import chain
from operator import attrgetter
from numpy import (
    any as np_any,
    float64,
    nan,
    nanpercentile,
    uint8,
)

from zipline.errors import (
    BadPercentileBounds,
    NonExistentAssetInTimeFrame,
    UnsupportedDataType,
)
from zipline.lib.labelarray import LabelArray
from zipline.lib.rank import grouped_masked_is_maximal
from zipline.utils.numpy_utils import is_missing
from zipline.pipeline.dtypes import (
    CLASSIFIER_DTYPES,
    FACTOR_DTYPES,
    FILTER_DTYPES,
)
from zipline.pipeline.expression import (
    BadBinaryOperator,
    FILTER_BINOPS,
    method_name_for_op,
    NumericalExpression,
)
from zipline.pipeline.mixins import (
    CustomTermMixin,
    IfElseMixin,
    LatestMixin,
    PositiveWindowLengthMixin,
    RestrictedDTypeMixin,
    SingleInputMixin,
    StandardOutputs,
)
from zipline.pipeline.term import ComputableTerm, Term
from zipline.utils.input_validation import expect_types
from zipline.utils.numpy_utils import (
    same,
    bool_dtype,
    int64_dtype,
    repeat_first_axis,
)
from quantrocket.master import get_securities

def concat_tuples(*tuples):
    """
    Concatenate a sequence of tuples into one tuple.
    """
    return tuple(chain(*tuples))


def binary_operator(op):
    """
    Factory function for making binary operator methods on a Filter subclass.

    Returns a function "binary_operator" suitable for implementing functions
    like __and__ or __or__.
    """
    # When combining a Filter with a NumericalExpression, we use this
    # attrgetter instance to defer to the commuted interpretation of the
    # NumericalExpression operator.
    commuted_method_getter = attrgetter(method_name_for_op(op, commute=True))

    def binary_operator(self, other):
        if isinstance(self, NumericalExpression):
            self_expr, other_expr, new_inputs = self.build_binary_op(
                op, other,
            )
            return NumExprFilter.create(
                "({left}) {op} ({right})".format(
                    left=self_expr,
                    op=op,
                    right=other_expr,
                ),
                new_inputs,
            )
        elif isinstance(other, NumericalExpression):
            # NumericalExpression overrides numerical ops to correctly handle
            # merging of inputs.  Look up and call the appropriate
            # right-binding operator with ourself as the input.
            return commuted_method_getter(other)(self)
        elif isinstance(other, Term):
            if other.dtype != bool_dtype:
                raise BadBinaryOperator(op, self, other)
            if self is other:
                return NumExprFilter.create(
                    "x_0 {op} x_0".format(op=op),
                    (self,),
                )
            return NumExprFilter.create(
                "x_0 {op} x_1".format(op=op),
                (self, other),
            )
        elif isinstance(other, int):  # Note that this is true for bool as well
            return NumExprFilter.create(
                "x_0 {op} {constant}".format(op=op, constant=int(other)),
                binds=(self,),
            )
        raise BadBinaryOperator(op, self, other)

    binary_operator.__doc__ = "Binary Operator: '%s'" % op
    return binary_operator


def unary_operator(op):
    """
    Factory function for making unary operator methods for Filters.
    """
    valid_ops = {'~'}
    if op not in valid_ops:
        raise ValueError("Invalid unary operator %s." % op)

    def unary_operator(self):
        # This can't be hoisted up a scope because the types returned by
        # unary_op_return_type aren't defined when the top-level function is
        # invoked.
        if isinstance(self, NumericalExpression):
            return NumExprFilter.create(
                "{op}({expr})".format(op=op, expr=self._expr),
                self.inputs,
            )
        else:
            return NumExprFilter.create("{op}x_0".format(op=op), (self,))

    unary_operator.__doc__ = "Unary Operator: '%s'" % op
    return unary_operator


class Filter(RestrictedDTypeMixin, ComputableTerm):
    """
    Pipeline expression computing a boolean output.

    Filters are most commonly useful for describing sets of assets to include
    or exclude for some particular purpose. Many Pipeline API functions accept
    a ``mask`` argument, which can be supplied a Filter indicating that only
    values passing the Filter should be considered when performing the
    requested computation. For example, :meth:`zipline.pipeline.Factor.top`
    accepts a mask indicating that ranks should be computed only on assets that
    passed the specified Filter.

    The most common way to construct a Filter is via one of the comparison
    operators (``<``, ``<=``, ``!=``, ``eq``, ``>``, ``>=``) of
    :class:`~zipline.pipeline.Factor`. For example, a natural way to construct
    a Filter for stocks with a 10-day VWAP less than $20.0 is to first
    construct a Factor computing 10-day VWAP and compare it to the scalar value
    20.0::

        >>> from zipline.pipeline.factors import VWAP
        >>> vwap_10 = VWAP(window_length=10)
        >>> vwaps_under_20 = (vwap_10 <= 20)

    Filters can also be constructed via comparisons between two Factors.  For
    example, to construct a Filter producing True for asset/date pairs where
    the asset's 10-day VWAP was greater than it's 30-day VWAP::

        >>> short_vwap = VWAP(window_length=10)
        >>> long_vwap = VWAP(window_length=30)
        >>> higher_short_vwap = (short_vwap > long_vwap)

    Filters can be combined via the ``&`` (and) and ``|`` (or) operators.

    ``&``-ing together two filters produces a new Filter that produces True if
    **both** of the inputs produced True.

    ``|``-ing together two filters produces a new Filter that produces True if
    **either** of its inputs produced True.

    The ``~`` operator can be used to invert a Filter, swapping all True values
    with Falses and vice-versa.

    Filters may be set as the ``screen`` attribute of a Pipeline, indicating
    asset/date pairs for which the filter produces False should be excluded
    from the Pipeline's output.  This is useful both for reducing noise in the
    output of a Pipeline and for reducing memory consumption of Pipeline
    results.
    """
    # Filters are window-safe by default, since a yes/no decision means the
    # same thing from all temporal perspectives.
    window_safe = True

    # Used by RestrictedDTypeMixin
    ALLOWED_DTYPES = FILTER_DTYPES
    dtype = bool_dtype

    clsdict = locals()
    clsdict.update(
        {
            method_name_for_op(op): binary_operator(op)
            for op in FILTER_BINOPS
        }
    )
    clsdict.update(
        {
            method_name_for_op(op, commute=True): binary_operator(op)
            for op in FILTER_BINOPS
        }
    )

    __invert__ = unary_operator('~')

    def _validate(self):
        # Run superclass validation first so that we handle `dtype not passed`
        # before this.
        retval = super(Filter, self)._validate()
        if self.dtype != bool_dtype:
            raise UnsupportedDataType(
                typename=type(self).__name__,
                dtype=self.dtype
            )
        return retval

    @classmethod
    def _principal_computable_term_type(cls):
        return Filter

    # as of 2023-02-09, pyright and pylance always assume that if_else
    # returns a Factor, even when Classifiers are passed, despite the
    # dual @overload decorators. As use of Factor is more common, this
    # issue isn't important enough to spend time resolving at present.
    @overload
    def if_else(
        self,
        if_true: 'Factor',
        if_false: 'Factor'
        ) -> 'Factor':...

    @overload
    def if_else(
        self,
        if_true: 'Classifier',
        if_false: 'Classifier'
        ) -> 'Classifier':...

    @expect_types(if_true=ComputableTerm, if_false=ComputableTerm)
    def if_else(self, if_true, if_false):
        """
        Create a term that selects values from one of two choices.

        Parameters
        ----------
        if_true : zipline.pipeline.term.ComputableTerm
            Expression whose values should be used at locations where this
            filter outputs True.
        if_false : zipline.pipeline.term.ComputableTerm
            Expression whose values should be used at locations where this
            filter outputs False.

        Returns
        -------
        merged : zipline.pipeline.term.ComputableTerm
           A term that computes by taking values from either ``if_true`` or
           ``if_false``, depending on the values produced by ``self``.

           The returned term draws from``if_true`` at locations where ``self``
           produces True, and it draws from ``if_false`` at locations where
           ``self`` produces False.

        Example
        -------

        Let ``f`` be a Factor that produces the following output::

                         AAPL   MSFT    MCD     BK
            2017-03-13    1.0    2.0    3.0    4.0
            2017-03-14    5.0    6.0    7.0    8.0

        Let ``g`` be another Factor that produces the following output::

                         AAPL   MSFT    MCD     BK
            2017-03-13   10.0   20.0   30.0   40.0
            2017-03-14   50.0   60.0   70.0   80.0

        Finally, let ``condition`` be a Filter that produces the following
        output::

                         AAPL   MSFT    MCD     BK
            2017-03-13   True  False   True  False
            2017-03-14   True   True  False  False

        Then, the expression ``condition.if_else(f, g)`` produces the following
        output::

                         AAPL   MSFT    MCD     BK
            2017-03-13    1.0   20.0    3.0   40.0
            2017-03-14    5.0    6.0   70.0   80.0

        See Also
        --------
        numpy.where
        Factor.fillna
        """
        true_type = if_true._principal_computable_term_type()
        false_type = if_false._principal_computable_term_type()

        if true_type is not false_type:
            raise TypeError(
                "Mismatched types in if_else(): if_true={}, but if_false={}"
                .format(true_type.__name__, false_type.__name__)
            )

        if if_true.dtype != if_false.dtype:
            raise TypeError(
                "Mismatched dtypes in if_else(): "
                "if_true.dtype = {}, if_false.dtype = {}"
                .format(if_true.dtype, if_false.dtype)
            )

        if if_true.outputs != if_false.outputs:
            raise ValueError(
                "Mismatched outputs in if_else(): "
                "if_true.outputs = {}, if_false.outputs = {}"
                .format(if_true.outputs, if_false.outputs),
            )

        if not same(if_true.missing_value, if_false.missing_value):
            raise ValueError(
                "Mismatched missing values in if_else(): "
                "if_true.missing_value = {!r}, if_false.missing_value = {!r}"
                .format(if_true.missing_value, if_false.missing_value)
            )

        return_type = type(if_true)._with_mixin(IfElseMixin)

        return return_type(
            condition=self,
            if_true=if_true,
            if_false=if_false,
        )

    def as_factor(self) -> 'BooleanFactor':
        """
        Create a Factor that returns 1s for True and 0s for False.

        Returns
        -------
        factor : Factor
            Factor returning 1s for True and 0s for False.

        Examples
        --------
        A common use for `as_factor` is to combine multiple boolean conditions
        into scores. First, create two Filters that compute whether price and
        volume are above certain levels:

        >>> from zipline.pipeline.data import EquityPricing
        >>> price = EquityPricing.close.latest
        >>> volume = EquityPricing.volume.latest
        >>> price_is_high = price > 100
        >>> volume_is_high = volume > 1e6

        Next, convert the boolean Filters to 1s and 0s and combine them into
        a score with a possible range of 0 to 2:

        >>> score = price_is_high.as_factor() + volume_is_high.as_factor()
        """
        # avoid circular import
        from zipline.pipeline.factors.factor import BooleanFactor
        return BooleanFactor(
            filter=self
        )

    def all(self, window_length: int, mask: 'Filter' = None) -> 'Filter':
        """
        Create a new Filter that returns True for assets that
        produce True for `window_length` consecutive days.

        Parameters
        ----------
        window_length : int
            the number of consecutive days over which assets
            must return True

        mask : zipline.pipeline.Filter, optional
           A Filter representing assets to consider when computing results.
           If supplied, we ignore asset/date pairs where ``mask`` produces
           ``False``.

        Returns
        -------
        filter : Filter
            Filter returning True for assets that produce True for
            `window_length` consecutive days.

        Examples
        --------
        Start with a Filter for assets with nonzero volume:

        >>> from zipline.pipeline.data import EquityPricing
        >>> has_volume = EquityPricing.volume.latest > 0

        Create a new Filter for assets with nonzero volume for
        200 consecutive days:

        >>> consistently_has_volume = has_volume.all(200)
        """
        # avoid circular import
        from zipline.pipeline.filters.smoothing import All
        return All(
            [self],
            window_length=window_length,
            mask=mask
        )

    def any(self, window_length: int, mask: 'Filter' = None) -> 'Filter':
        """
        Create a new Filter that returns True for assets that
        produce True for at least one day in the last `window_length`
        days.

        Parameters
        ----------
        window_length : int
            the number of days over which assets must return True
            on at least one day

        Returns
        -------
        filter : Filter
            Filter returning True for assets that produce True for
            at least one day in the last `window_length` days.

        mask : zipline.pipeline.Filter, optional
           A Filter representing assets to consider when computing results.
           If supplied, we ignore asset/date pairs where ``mask`` produces
           ``False``.

        Examples
        --------
        Start with a Filter for assets with returns greater
        than 10%:

        >>> from zipline.pipeline.factors import DailyReturns
        >>> has_big_gain = DailyReturns() > 0.10

        Create a new Filter for assets with a big gain on
        any of the last 5 days:

        >>> has_recent_big_gain = has_big_gain.any(5)
        """
        # avoid circular import
        from zipline.pipeline.filters.smoothing import Any
        return Any(
            [self],
            window_length=window_length,
            mask=mask
        )

    def at_least_n(
        self,
        N: int,
        window_length: int,
        mask: 'Filter' = None
        ) -> 'Filter':
        """
        Create a new Filter that returns True for assets that
        produce True for at least `N` days in the last `window_length`
        days.

        Parameters
        ----------
        N : int
            the minimum number of days on which assets must return
            True

        window_length : int
            the number of days over which assets must return True
            on at least N days

        mask : zipline.pipeline.Filter, optional
           A Filter representing assets to consider when computing results.
           If supplied, we ignore asset/date pairs where ``mask`` produces
           ``False``.

        Returns
        -------
        filter : Filter
            Filter returning True for assets that produce True for
            at least `N` days in the last `window_length` days.

        Examples
        --------
        Start with a Filter for assets with returns greater
        than 10%:

        >>> from zipline.pipeline.factors import DailyReturns
        >>> has_big_gain = DailyReturns() > 0.10

        Create a new Filter for assets with a big gain on
        at least 2 of the last 5 days:

        >>> has_multiple_big_gains = has_big_gain.at_least_n(2, window_length=5)
        """
        # avoid circular import
        from zipline.pipeline.filters.smoothing import AtLeastN
        return AtLeastN(
            [self],
            window_length=window_length,
            N=N,
            mask=mask
        )

class NumExprFilter(NumericalExpression, Filter):
    """
    A Filter computed from a numexpr expression.
    """

    @classmethod
    def create(cls, expr, binds):
        """
        Helper for creating new NumExprFactors.

        This is just a wrapper around NumericalExpression.__new__ that always
        forwards `bool` as the dtype, since Filters can only be of boolean
        dtype.
        """
        return cls(expr=expr, binds=binds, dtype=bool_dtype)

    def _compute(self, arrays, dates, assets, mask):
        """
        Compute our result with numexpr, then re-apply `mask`.
        """
        return super(NumExprFilter, self)._compute(
            arrays,
            dates,
            assets,
            mask,
        ) & mask


class NullFilter(SingleInputMixin, Filter):
    """
    A Filter indicating whether input values are missing from an input.

    Parameters
    ----------
    factor : zipline.pipeline.Term
        The factor to compare against its missing_value.
    """
    window_length = 0

    def __new__(cls, term):
        return super(NullFilter, cls).__new__(
            cls,
            inputs=(term,),
        )

    def _compute(self, arrays, dates, assets, mask):
        data = arrays[0]
        if isinstance(data, LabelArray):
            return data.is_missing()
        return is_missing(arrays[0], self.inputs[0].missing_value)


class NotNullFilter(SingleInputMixin, Filter):
    """
    A Filter indicating whether input values are **not** missing from an input.

    Parameters
    ----------
    factor : zipline.pipeline.Term
        The factor to compare against its missing_value.
    """
    window_length = 0

    def __new__(cls, term):
        return super(NotNullFilter, cls).__new__(
            cls,
            inputs=(term,),
        )

    def _compute(self, arrays, dates, assets, mask):
        data = arrays[0]
        if isinstance(data, LabelArray):
            return ~data.is_missing()
        return ~is_missing(arrays[0], self.inputs[0].missing_value)


class PercentileFilter(SingleInputMixin, Filter):
    """
    A Filter representing assets falling between percentile bounds of a Factor.

    Parameters
    ----------
    factor : zipline.pipeline.factor.Factor
        The factor over which to compute percentile bounds.
    min_percentile : float [0.0, 1.0]
        The minimum percentile rank of an asset that will pass the filter.
    max_percentile : float [0.0, 1.0]
        The maxiumum percentile rank of an asset that will pass the filter.
    """
    window_length = 0

    def __new__(cls, factor, min_percentile, max_percentile, mask):
        return super(PercentileFilter, cls).__new__(
            cls,
            inputs=(factor,),
            mask=mask,
            min_percentile=min_percentile,
            max_percentile=max_percentile,
        )

    def _init(self, min_percentile, max_percentile, *args, **kwargs):
        self._min_percentile = min_percentile
        self._max_percentile = max_percentile
        return super(PercentileFilter, self)._init(*args, **kwargs)

    @classmethod
    def _static_identity(cls, min_percentile, max_percentile, *args, **kwargs):
        return (
            super(PercentileFilter, cls)._static_identity(*args, **kwargs),
            min_percentile,
            max_percentile,
        )

    def _validate(self):
        """
        Ensure that our percentile bounds are well-formed.
        """
        if not 0.0 <= self._min_percentile < self._max_percentile <= 100.0:
            raise BadPercentileBounds(
                min_percentile=self._min_percentile,
                max_percentile=self._max_percentile,
                upper_bound=100.0
            )
        return super(PercentileFilter, self)._validate()

    def _compute(self, arrays, dates, assets, mask):
        """
        For each row in the input, compute a mask of all values falling between
        the given percentiles.
        """
        # TODO: Review whether there's a better way of handling small numbers
        # of columns.
        data = arrays[0].copy().astype(float64)
        data[~mask] = nan

        # FIXME: np.nanpercentile **should** support computing multiple bounds
        # at once, but there's a bug in the logic for multiple bounds in numpy
        # 1.9.2.  It will be fixed in 1.10.
        # c.f. https://github.com/numpy/numpy/pull/5981
        lower_bounds = nanpercentile(
            data,
            self._min_percentile,
            axis=1,
            keepdims=True,
        )
        upper_bounds = nanpercentile(
            data,
            self._max_percentile,
            axis=1,
            keepdims=True,
        )
        return (lower_bounds <= data) & (data <= upper_bounds)

    def graph_repr(self):
        # Graphviz interprets `\l` as "divide label into lines, left-justified"
        return "{}:\\l  min: {}, max: {}\\l".format(
            type(self).__name__,
            self._min_percentile,
            self._max_percentile,
        )


class CustomFilter(PositiveWindowLengthMixin, CustomTermMixin, Filter):
    """
    Base class for user-defined Filters.

    Parameters
    ----------
    inputs : iterable, optional
        An iterable of `BoundColumn` instances (e.g. USEquityPricing.close),
        describing the data to load and pass to ``self.compute``.  If this
        argument is passed to the CustomFilter constructor, we look for a
        class-level attribute named ``inputs``.
    window_length : int, optional
        Number of rows to pass for each input.  If this argument is not passed
        to the CustomFilter constructor, we look for a class-level attribute
        named `window_length`.

    Notes
    -----
    Users implementing their own Filters should subclass CustomFilter and
    implement a method named ``compute`` with the following signature:

    .. code-block:: python

        def compute(self, today, assets, out, *inputs):
           ...

    On each simulation date, ``compute`` will be called with the current date,
    an array of sids, an output array, and an input array for each expression
    passed as inputs to the CustomFilter constructor.

    The specific types of the values passed to ``compute`` are as follows::

        today : np.datetime64[ns]
            Row label for the last row of all arrays passed as `inputs`.
        assets : np.array[int64, ndim=1]
            Column labels for `out` and`inputs`.
        out : np.array[bool, ndim=1]
            Output array of the same shape as `assets`.  `compute` should write
            its desired return values into `out`.
        *inputs : tuple of np.array
            Raw data arrays corresponding to the values of `self.inputs`.

    See the documentation for
    :class:`~zipline.pipeline.CustomFactor` for more details on
    implementing a custom ``compute`` method.

    See Also
    --------
    zipline.pipeline.CustomFactor
    """
    def _validate(self):
        try:
            super(CustomFilter, self)._validate()
        except UnsupportedDataType:
            if self.dtype in CLASSIFIER_DTYPES:
                raise UnsupportedDataType(
                    typename=type(self).__name__,
                    dtype=self.dtype,
                    hint='Did you mean to create a CustomClassifier?',
                )
            elif self.dtype in FACTOR_DTYPES:
                raise UnsupportedDataType(
                    typename=type(self).__name__,
                    dtype=self.dtype,
                    hint='Did you mean to create a CustomFactor?',
                )
            raise


class ArrayPredicate(SingleInputMixin, Filter):
    """
    A filter applying a function from (ndarray, *args) -> ndarray[bool].

    Parameters
    ----------
    term : zipline.pipeline.Term
        Term producing the array over which the predicate will be computed.
    op : function(ndarray, *args) -> ndarray[bool]
        Function to apply to the result of `term`.
    opargs : tuple[hashable]
        Additional argument to apply to ``op``.
    """
    params = ('op', 'opargs')
    window_length = 0

    @expect_types(term=Term, opargs=tuple)
    def __new__(cls, term, op, opargs):
        hash(opargs)  # fail fast if opargs isn't hashable.
        return super(ArrayPredicate, cls).__new__(
            ArrayPredicate,
            op=op,
            opargs=opargs,
            inputs=(term,),
            mask=term.mask,
        )

    def _compute(self, arrays, dates, assets, mask):
        params = self.params
        data = arrays[0]
        return params['op'](data, *params['opargs']) & mask

    def graph_repr(self):
        # Graphviz interprets `\l` as "divide label into lines, left-justified"
        return "{}:\\l  op: {}.{}()".format(
            type(self).__name__,
            self.params['op'].__module__,
            self.params['op'].__name__,
        )


class Latest(LatestMixin, CustomFilter):
    """
    Filter producing the most recently-known value of `inputs[0]` on each day.
    """
    pass


class SingleAsset(Filter):
    """
    A Filter that computes to True only for the given asset.
    """
    inputs = []
    window_length = 1

    def __new__(cls, asset):
        return super(SingleAsset, cls).__new__(cls, asset=asset)

    def _init(self, asset, *args, **kwargs):
        self._asset = asset
        return super(SingleAsset, self)._init(*args, **kwargs)

    @classmethod
    def _static_identity(cls, asset, *args, **kwargs):
        return (
            super(SingleAsset, cls)._static_identity(*args, **kwargs), asset,
        )

    def _compute(self, arrays, dates, assets, mask):
        is_my_asset = (assets == self._asset.sid)
        out = repeat_first_axis(is_my_asset, len(mask))
        # Raise an exception if `self._asset` does not exist for the entirety
        # of the timeframe over which we are computing.
        if (is_my_asset.sum() != 1) or ((out & mask).sum() != len(mask)):
            raise NonExistentAssetInTimeFrame(
                asset=self._asset, start_date=dates[0], end_date=dates[-1],
            )
        return out

    def graph_repr(self):
        # Graphviz interprets `\l` as "divide label into lines, left-justified"
        return "SingleAsset:\\l  asset: {!r}\\l".format(self._asset)

class StaticAssets(Filter):
    """
    A Filter that computes True for a specific set of predetermined assets.

    Parameters
    ----------
    assets : iterable[Asset]
        An iterable of assets for which to filter.
    """
    inputs = ()
    window_length = 0
    params = ('sids',)

    def __new__(cls, assets):
        sids = frozenset(asset.sid for asset in assets)
        return super(StaticAssets, cls).__new__(cls, sids=sids)

    def _compute(self, arrays, dates, sids, mask):
        my_columns = sids.isin(self.params['sids'])
        return repeat_first_axis(my_columns, len(mask)) & mask

class StaticSids(Filter):
    """
    A filter limiting to specific sids.

    Parameters
    ----------
    sids : iterable[str]
        an iterable of sids for which to filter.

    Examples
    --------
    Limit to AAPL and AMZN:

    >>> from zipline.pipeline.filters import StaticSids
    >>> pipe = Pipeline(screen=StaticSids(["FIBBG000B9XRY4", "FIBBG000BVPV84"]))              # doctest: +SKIP
    """
    inputs = None
    window_length = 1
    params = ("sids",)

    def __new__(cls, sids):
        # avoid circular import
        from zipline.pipeline.data.master import SecuritiesMaster
        inputs = [SecuritiesMaster.Sid]
        sids = frozenset(sids)
        return super(StaticSids, cls).__new__(cls, inputs=inputs, sids=sids)

    def _compute(self, arrays, dates, sids, mask):
        real_sids = next(arrays[0])[-1]
        my_columns = real_sids.isin(self.params['sids'])
        return repeat_first_axis(my_columns, len(mask)) & mask

class StaticUniverse(StaticSids):
    """
    A filter limiting to assets that are members of a universe defined
    in the securities master database.

    Parameters
    ----------
    code : str, required
        the universe code

    Examples
    --------
    Limit to a universe of energy stocks:

    >>> from zipline.pipeline.filters import StaticUniverse
    >>> pipe = Pipeline(screen=StaticUniverse("energy-stk"))              # doctest: +SKIP
    """

    def __new__(cls, code):
        securities = get_securities(universes=code, fields="Sid")
        sids = securities.index.tolist()
        return super(StaticUniverse, cls).__new__(cls, sids)

class AllPresent(CustomFilter, SingleInputMixin, StandardOutputs):
    """Pipeline filter indicating input term has data for a given window.

    This filter is normally used by calling the `.all_present()` method on
    a BoundColumn, Factor, or Classifier.
    """
    def _validate(self):

        if isinstance(self.inputs[0], Filter):
            raise TypeError(
                "Input to filter `AllPresent` cannot be a Filter."
            )

        return super(AllPresent, self)._validate()

    def compute(self, today, assets, out, value):
        if isinstance(value, LabelArray):
            out[:] = ~np_any(value.is_missing(), axis=0)
        else:
            out[:] = ~np_any(
                is_missing(value, self.inputs[0].missing_value),
                axis=0,
            )


class MaximumFilter(Filter, StandardOutputs):
    """Pipeline filter that selects the top asset, possibly grouped and masked.
    """
    window_length = 0

    def __new__(cls, factor, groupby, mask):
        if groupby is None:
            from zipline.pipeline.classifiers import Everything
            groupby = Everything()

        return super(MaximumFilter, cls).__new__(
            cls,
            inputs=(factor, groupby),
            mask=mask,
        )

    def _compute(self, arrays, dates, assets, mask):
        # XXX: We're doing a lot of unncessary work here if `groupby` isn't
        # specified.
        data = arrays[0]
        group_labels, null_label = self.inputs[1]._to_integral(arrays[1])
        effective_mask = (
            mask
            & (group_labels != null_label)
            & ~is_missing(data, self.inputs[0].missing_value)
        ).view(uint8)

        return grouped_masked_is_maximal(
            # Unconditionally view the data as int64.
            # This is safe because casting from float64 to int64 is an
            # order-preserving operation.
            data.view(int64_dtype),
            # PERF: Consider supporting different sizes of group labels.
            group_labels.astype(int64_dtype),
            effective_mask,
        )

    def __repr__(self):
        return "Maximum({}, groupby={}, mask={})".format(
            self.inputs[0].recursive_repr(),
            self.inputs[1].recursive_repr(),
            self.mask.recursive_repr(),
        )

    def graph_repr(self):
        # Graphviz interprets `\l` as "divide label into lines, left-justified"
        return "Maximum:\\l  groupby: {}\\l  mask: {}\\l".format(
            self.inputs[1].recursive_repr(),
            self.mask.recursive_repr(),
        )
