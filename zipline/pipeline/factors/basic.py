"""Simple common factors.
"""
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from zipline.pipeline.data.dataset import BoundColumn
    from zipline.pipeline.filters import Filter

from numpy import (
    arange,
    average,
    clip,
    copyto,
    exp,
    fmax,
    full,
    isnan,
    log,
    NINF,
    sqrt,
    sum as np_sum,
    unique,
)

from zipline.pipeline.data import EquityPricing
from zipline.utils.math_utils import (
    nanargmax,
    nanmax,
    nanmean,
    nanstd,
    nansum,
)
from zipline.utils.numpy_utils import (
    float64_dtype,
    ignore_nanwarnings,
)

from .factor import CustomFactor
from ..mixins import SingleInputMixin


class Returns(CustomFactor):
    """
    Factor that calculates the percent change in close price over the given window_length.

    **Default Inputs**: EquityPricing.close

    Parameters
    ----------
    inputs : BoundColumn
        The expression for which to compute returns. Default is EquityPricing.close.

    window_length : int > 0
        Length of the lookback window over which to compute returns.

    exclude_window_length : int >= 0, optional
        Optional number of most recent observations to exclude from the
        returns calculation. Default is 0, meaning don't exclude any
        observations.


    mask : zipline.pipeline.Filter, optional
        A Filter representing assets to consider when computing results.
        If supplied, we ignore asset/date pairs where ``mask`` produces
        ``False``.

    Examples
    --------
    Calculate returns over the past year, excluding the most recent month:

    >>> returns = Returns(window_length=252, exclude_window_length=21)
    """
    inputs = [EquityPricing.close]
    window_safe = True

    params = {'exclude_window_length': 0}

    if TYPE_CHECKING:
        def __init__(
            self,
            inputs: 'BoundColumn' = EquityPricing.close,
            window_length: int = None,
            exclude_window_length: int=0,
            mask: 'Filter' = None):
            pass

    def _validate(self):
        super(Returns, self)._validate()
        if self.window_length < 2:
            raise ValueError(
                "'Returns' expected a window length of at least 2, but was "
                "given {window_length}. For daily returns, use a window "
                "length of 2.".format(window_length=self.window_length)
            )
        if self.params["exclude_window_length"] >= self.window_length:
            raise ValueError(
                "window_length must be greater than exclude_window_length (got "
                "window_length={window_length}, exclude_window_length="
                "{exclude_window_length})".format(
                    window_length=self.window_length,
                    exclude_window_length=self.params["exclude_window_length"])
            )

    def compute(self, today, assets, out, close, exclude_window_length):
        out[:] = (close[-1 - exclude_window_length] - close[0]) / close[0]

class Shift(SingleInputMixin, CustomFactor):
    """
    Factor that returns the input shifted forward the specified number of periods.

    **Default Inputs:** None

    **Default Window Length:** None

    Parameters
    ----------
    inputs : BoundColumn
        The expression to shift.

    window_length : int >= 2
        Length of the lookback window over which to shift. A window length of 2
        means that the output will be the input shifted forward by 1 period.

    mask : zipline.pipeline.Filter, optional
        A Filter representing assets to consider when computing results.
        If supplied, we ignore asset/date pairs where ``mask`` produces
        ``False``.

    See Also
    --------
    zipline.pipeline.Factor.shift
    """
    window_safe = True

    if TYPE_CHECKING:
        def __init__(
            self,
            inputs: 'BoundColumn',
            window_length: int,
            mask: 'Filter' = None):
            pass

    def _validate(self):
        super()._validate()
        if self.window_length < 2:
            raise ValueError(
                "'Shift' expected a window length"
                "of at least 2, but was given {window_length}. "
                "To shift one period, use a window "
                "length of 2.".format(window_length=self.window_length)
            )

    def compute(self, today, assets, out, values):
        out[:] = values[0]

class PercentChange(SingleInputMixin, CustomFactor):
    """
    Factor that calculates the percent change over the given window_length.

    **Default Inputs:** None

    **Default Window Length:** None

    Parameters
    ----------
    inputs : BoundColumn
        The expression for which to compute percent change.

    window_length : int > 0
        Length of the lookback window over which to compute percent change.

    mask : zipline.pipeline.Filter, optional
        A Filter representing assets to consider when computing results.
        If supplied, we ignore asset/date pairs where ``mask`` produces
        ``False``.

    Examples
    --------
    Calculate 5-day percent change of opening price:

    >>> percent_change = PercentChange(inputs=EquityPricing.open, window_length=5)

    Notes
    -----
    Percent change is calculated as ``(new - old) / abs(old)``.
    """
    window_safe = True

    if TYPE_CHECKING:
        def __init__(
            self,
            inputs: 'BoundColumn',
            window_length: int,
            mask: 'Filter' = None):
            pass

    def _validate(self):
        super(PercentChange, self)._validate()
        if self.window_length < 2:
            raise ValueError(
                "'PercentChange' expected a window length"
                "of at least 2, but was given {window_length}. "
                "For daily percent change, use a window "
                "length of 2.".format(window_length=self.window_length)
            )

    def compute(self, today, assets, out, values):
        out[:] = (values[-1] - values[0]) / abs(values[0])


class DailyReturns(Returns):
    """
    Factor that calculates daily percent change in close price.

    **Default Inputs**: [EquityPricing.close]

    Parameters
    ----------
    inputs : BoundColumn
        The expression for which to compute daily returns.
        Default is EquityPricing.close.

    mask : zipline.pipeline.Filter, optional
        A Filter representing assets to consider when computing results.
        If supplied, we ignore asset/date pairs where ``mask`` produces
        ``False``.

    Examples
    --------
    Calculate daily returns:

    >>> daily_returns = DailyReturns()
    """
    inputs = [EquityPricing.close]
    window_safe = True
    window_length = 2

    if TYPE_CHECKING:
        def __init__(
                self,
                inputs: 'BoundColumn' = EquityPricing.close,
                mask: 'Filter' = None):
            pass

class OvernightReturns(CustomFactor):
    """
    Factor that calculates percent change from the previous close price
    to the open price.

    Parameters
    ----------
    mask : zipline.pipeline.Filter, optional
        A Filter representing assets to consider when computing results.
        If supplied, we ignore asset/date pairs where ``mask`` produces
        ``False``.

    Examples
    --------
    Calculate overnight returns:

    >>> overnight_returns = OvernightReturns()
    """
    inputs = [EquityPricing.close, EquityPricing.open]
    window_safe = True
    window_length = 2

    if TYPE_CHECKING:
        def __init__(
                self,
                mask: 'Filter' = None):
            pass

    def compute(self, today, assets, out, close, open):
        out[:] = (open[-1] - close[0]) / close[0]

class IntradayReturns(CustomFactor):
    """
    Factor that calculates percent change from the open price to the close price.

    Parameters
    ----------
    mask : zipline.pipeline.Filter, optional
        A Filter representing assets to consider when computing results.
        If supplied, we ignore asset/date pairs where ``mask`` produces
        ``False``.

    Examples
    --------
    Calculate intraday (open-to-close) returns:

    >>> intraday_returns = IntradayReturns()
    """
    inputs = [EquityPricing.open, EquityPricing.close]
    window_safe = True
    window_length = 1

    if TYPE_CHECKING:
        def __init__(
                self,
                mask: 'Filter' = None):
            pass

    def compute(self, today, assets, out, open, close):
        out[:] = (close[-1] - open[-1]) / open[-1]

class SimpleMovingAverage(SingleInputMixin, CustomFactor):
    """
    Factor that calculates average value of an arbitrary column.

    **Default Inputs**: None

    **Default Window Length**: None

    Parameters
    ----------
    inputs : BoundColumn
        The expression for which to compute the moving average.

    window_length : int > 0
        Length of the lookback window over which to compute the moving average.

    mask : zipline.pipeline.Filter, optional
        A Filter representing assets to consider when computing results.
        If supplied, we ignore asset/date pairs where ``mask`` produces
        ``False``.

    Examples
    --------
    Calculate a 200-day simple moving average of daily close price:

    >>> sma_200 = SimpleMovingAverage(inputs=EquityPricing.close, window_length=200)
    """
    if TYPE_CHECKING:
        def __init__(
            self,
            inputs: 'BoundColumn',
            window_length: int,
            mask: 'Filter' = None):
            pass

    # numpy's nan functions throw warnings when passed an array containing only
    # nans, but they still returns the desired value (nan), so we ignore the
    # warning.
    ctx = ignore_nanwarnings()

    def compute(self, today, assets, out, data):
        out[:] = nanmean(data, axis=0)


class WeightedAverageValue(CustomFactor):
    """
    Helper for VWAP-like computations.

    **Default Inputs:** None

    **Default Window Length:** None
    """
    def compute(self, today, assets, out, base, weight):
        out[:] = nansum(base * weight, axis=0) / nansum(weight, axis=0)


class VWAP(WeightedAverageValue):
    """
    Factor that calculates volume-weighted average price.

    **Default Inputs:** [EquityPricing.close, EquityPricing.volume]

    **Default Window Length:** None

    Parameters
    ----------
    window_length : int > 0
        Length of the lookback window over which to compute VWAP.

    mask : zipline.pipeline.Filter, optional
        A Filter representing assets to consider when computing results.
        If supplied, we ignore asset/date pairs where ``mask`` produces
        ``False``.

    Examples
    --------
    Calculate a 5-day VWAP:

    >>> vwap = VWAP(window_length=5)
    """
    if TYPE_CHECKING:
        def __init__(
            self,
            window_length: int,
            mask: 'Filter' = None):
            pass

    inputs = (EquityPricing.close, EquityPricing.volume)


class MaxDrawdown(SingleInputMixin, CustomFactor):
    """
    Factor that calculates maximum drawdown.

    **Default Inputs:** None

    **Default Window Length:** None

    Parameters
    ----------
    inputs : BoundColumn
        The expression for which to compute max drawdown.

    window_length : int > 0
        Length of the lookback window over which to compute max drawdown.

    mask : zipline.pipeline.Filter, optional
        A Filter representing assets to consider when computing results.
        If supplied, we ignore asset/date pairs where ``mask`` produces
        ``False``.

    Examples
    --------
    Calculate max drawdown over a rolling 200-day lookback window:

    >>> max_drawdown = MaxDrawdown(inputs=EquityPricing.close, window_length=200)
    """
    ctx = ignore_nanwarnings()

    if TYPE_CHECKING:
        def __init__(
            self,
            inputs: 'BoundColumn',
            window_length: int,
            mask: 'Filter' = None):
            pass

    def compute(self, today, assets, out, data):
        drawdowns = fmax.accumulate(data, axis=0) - data
        drawdowns[isnan(drawdowns)] = NINF
        drawdown_ends = nanargmax(drawdowns, axis=0)

        # TODO: Accelerate this loop in Cython or Numba.
        for i, end in enumerate(drawdown_ends):
            peak = nanmax(data[:end + 1, i])
            out[i] = (peak - data[end, i]) / data[end, i]


class AverageDollarVolume(CustomFactor):
    """
    Factor that calculates average daily dollar volume.

    **Default Inputs:** [EquityPricing.close, EquityPricing.volume]

    **Default Window Length:** None

    Parameters
    ----------
    window_length : int > 0
        Length of the lookback window over which to compute average dollar volume.

    mask : zipline.pipeline.Filter, optional
        A Filter representing assets to consider when computing results.
        If supplied, we ignore asset/date pairs where ``mask`` produces
        ``False``.

    Examples
    --------
    Calculate 30-day average dollar volume:

    >>> avg_dollar_volume = AverageDollarVolume(window_length=30)
    """
    inputs = [EquityPricing.close, EquityPricing.volume]

    if TYPE_CHECKING:
        def __init__(self, window_length: int, mask: 'Filter' = None):
            pass

    def compute(self, today, assets, out, close, volume):
        out[:] = nansum(close * volume, axis=0) / len(close)


def exponential_weights(length, decay_rate):
    """
    Build a weight vector for an exponentially-weighted statistic.

    The resulting ndarray is of the form::

        [decay_rate ** length, ..., decay_rate ** 2, decay_rate]

    Parameters
    ----------
    length : int
        The length of the desired weight vector.
    decay_rate : float
        The rate at which entries in the weight vector increase or decrease.

    Returns
    -------
    weights : ndarray[float64]
    """
    return full(length, decay_rate, float64_dtype) ** arange(length + 1, 1, -1)


class _ExponentialWeightedFactor(SingleInputMixin, CustomFactor):
    """
    Base class for factors implementing exponential-weighted operations.

    **Default Inputs:** None

    **Default Window Length:** None

    Parameters
    ----------
    inputs : length-1 list or tuple of BoundColumn
        The expression over which to compute the average.
    window_length : int > 0
        Length of the lookback window over which to compute the average.
    decay_rate : float, 0 < decay_rate <= 1
        Weighting factor by which to discount past observations.

        When calculating historical averages, rows are multiplied by the
        sequence::

            decay_rate, decay_rate ** 2, decay_rate ** 3, ...

    Methods
    -------
    weights
    from_span
    from_halflife
    from_center_of_mass
    """
    params = ('decay_rate',)

    @classmethod
    def from_span(cls, inputs, window_length, span, **kwargs):
        """
        Convenience constructor for passing `decay_rate` in terms of `span`.

        Forwards `decay_rate` as `1 - (2.0 / (1 + span))`.  This provides the
        behavior equivalent to passing `span` to pandas.ewma.

        Examples
        --------
        .. code-block:: python

            # Equivalent to:
            # my_ewma = EWMA(
            #    inputs=[EquityPricing.close],
            #    window_length=30,
            #    decay_rate=(1 - (2.0 / (1 + 15.0))),
            # )
            my_ewma = EWMA.from_span(
                inputs=[EquityPricing.close],
                window_length=30,
                span=15,
            )

        Notes
        -----
        This classmethod is provided by both
        :class:`ExponentialWeightedMovingAverage` and
        :class:`ExponentialWeightedMovingStdDev`.
        """
        if span <= 1:
            raise ValueError(
                "`span` must be a positive number. %s was passed." % span
            )

        decay_rate = (1.0 - (2.0 / (1.0 + span)))
        assert 0.0 < decay_rate <= 1.0

        return cls(
            inputs=inputs,
            window_length=window_length,
            decay_rate=decay_rate,
            **kwargs
        )

    @classmethod
    def from_halflife(cls, inputs, window_length, halflife, **kwargs):
        """
        Convenience constructor for passing ``decay_rate`` in terms of half
        life.

        Forwards ``decay_rate`` as ``exp(log(.5) / halflife)``.  This provides
        the behavior equivalent to passing `halflife` to pandas.ewma.

        Examples
        --------
        .. code-block:: python

            # Equivalent to:
            # my_ewma = EWMA(
            #    inputs=[EquityPricing.close],
            #    window_length=30,
            #    decay_rate=np.exp(np.log(0.5) / 15),
            # )
            my_ewma = EWMA.from_halflife(
                inputs=[EquityPricing.close],
                window_length=30,
                halflife=15,
            )

        Notes
        -----
        This classmethod is provided by both
        :class:`ExponentialWeightedMovingAverage` and
        :class:`ExponentialWeightedMovingStdDev`.
        """
        if halflife <= 0:
            raise ValueError(
                "`span` must be a positive number. %s was passed." % halflife
            )
        decay_rate = exp(log(.5) / halflife)
        assert 0.0 < decay_rate <= 1.0

        return cls(
            inputs=inputs,
            window_length=window_length,
            decay_rate=decay_rate,
            **kwargs
        )

    @classmethod
    def from_center_of_mass(cls,
                            inputs,
                            window_length,
                            center_of_mass,
                            **kwargs):
        """
        Convenience constructor for passing `decay_rate` in terms of center of
        mass.

        Forwards `decay_rate` as `1 - (1 / 1 + center_of_mass)`.  This provides
        behavior equivalent to passing `center_of_mass` to pandas.ewma.

        Examples
        --------
        .. code-block:: python

            # Equivalent to:
            # my_ewma = EWMA(
            #    inputs=[EquityPricing.close],
            #    window_length=30,
            #    decay_rate=(1 - (1 / 15.0)),
            # )
            my_ewma = EWMA.from_center_of_mass(
                inputs=[EquityPricing.close],
                window_length=30,
                center_of_mass=15,
            )

        Notes
        -----
        This classmethod is provided by both
        :class:`ExponentialWeightedMovingAverage` and
        :class:`ExponentialWeightedMovingStdDev`.
        """
        return cls(
            inputs=inputs,
            window_length=window_length,
            decay_rate=(1.0 - (1.0 / (1.0 + center_of_mass))),
            **kwargs
        )


class ExponentialWeightedMovingAverage(_ExponentialWeightedFactor):
    """
    Factor that calculates exponentially-weighted moving average.

    **Default Inputs:** None

    **Default Window Length:** None

    Parameters
    ----------
    inputs : BoundColumn
        The expression over which to compute the average.

    window_length : int > 0
        Length of the lookback window over which to compute the average.

    decay_rate : float, 0 < decay_rate <= 1
        Weighting factor by which to discount past observations. Lower values
        will discount past observations more rapidly, while higher values will
        discount past observations more slowly.

        When calculating historical averages, rows are multiplied by the
        sequence::

            decay_rate, decay_rate ** 2, decay_rate ** 3, ...

    mask : zipline.pipeline.Filter, optional
        A Filter representing assets to consider when computing results.
        If supplied, we ignore asset/date pairs where ``mask`` produces
        ``False``.

    Examples
    --------
    Calculate the 30-day EWMA of `EquityPricing.close` with a decay rate of 0.9.

    >>> ewma = ExponentialWeightedMovingAverage(inputs=EquityPricing.close, window_length=30, decay_rate=0.9)

    Notes
    -----
    - This class can also be imported under the name ``EWMA``.

    See Also
    --------
    :meth:`pandas.DataFrame.ewm`
    """
    if TYPE_CHECKING:
        def __init__(self,
                     inputs: BoundColumn,
                     window_length: int,
                     decay_rate: float,
                     mask: 'Filter' = None):
            pass

    def compute(self, today, assets, out, data, decay_rate):
        out[:] = average(
            data,
            axis=0,
            weights=exponential_weights(len(data), decay_rate),
        )


class ExponentialWeightedMovingStdDev(_ExponentialWeightedFactor):
    """
    Factor that calculates exponentially-weighted moving standard deviation.

    **Default Inputs:** None

    **Default Window Length:** None

    Parameters
    ----------
    inputs : BoundColumn
        The expression over which to compute the average.

    window_length : int > 0
        Length of the lookback window over which to compute the average.

    decay_rate : float, 0 < decay_rate <= 1
        Weighting factor by which to discount past observations. Lower values
        will discount past observations more rapidly, while higher values will
        discount past observations more slowly.

        When calculating historical averages, rows are multiplied by the
        sequence::

            decay_rate, decay_rate ** 2, decay_rate ** 3, ...

    mask : zipline.pipeline.Filter, optional
        A Filter representing assets to consider when computing results.
        If supplied, we ignore asset/date pairs where ``mask`` produces
        ``False``.

    --------
    Calculate the 30-day EWMSTD of `EquityPricing.close` with a decay rate of 0.9.

    >>> ewmstd = ExponentialWeightedMovingStdDev(inputs=EquityPricing.close, window_length=30, decay_rate=0.9)

    Notes
    -----
    - This class can also be imported under the name ``EWMSTD``.

    See Also
    --------
    :func:`pandas.DataFrame.ewm`
    """
    if TYPE_CHECKING:
        def __init__(self,
                     inputs: BoundColumn,
                     window_length: int,
                     decay_rate: float,
                     mask: 'Filter' = None):
            pass

    def compute(self, today, assets, out, data, decay_rate):
        weights = exponential_weights(len(data), decay_rate)

        mean = average(data, axis=0, weights=weights)
        variance = average((data - mean) ** 2, axis=0, weights=weights)

        squared_weight_sum = (np_sum(weights) ** 2)
        bias_correction = (
            squared_weight_sum / (squared_weight_sum - np_sum(weights ** 2))
        )
        out[:] = sqrt(variance * bias_correction)


class LinearWeightedMovingAverage(SingleInputMixin, CustomFactor):
    """
    Factor that calculates weighted average value of an arbitrary column.

    **Default Inputs**: None

    **Default Window Length**: None

    Parameters
    ----------
    inputs : BoundColumn
        The expression for which to compute the average.

    window_length : int > 0
        Length of the lookback window over which to compute the average.

    mask : zipline.pipeline.Filter, optional
        A Filter representing assets to consider when computing results.
        If supplied, we ignore asset/date pairs where ``mask`` produces
        ``False``.

    Examples
    --------
    Calculate a 60-day linearly weighted moving average of `EquityPricing.close`:

    >>> lwma = LinearWeightedMovingAverage(inputs=EquityPricing.close, window_length=60)
    """
    # numpy's nan functions throw warnings when passed an array containing only
    # nans, but they still returns the desired value (nan), so we ignore the
    # warning.
    ctx = ignore_nanwarnings()

    if TYPE_CHECKING:
        def __init__(self,
                     inputs: BoundColumn,
                     window_length: int,
                     mask: 'Filter' = None):
            pass

    def compute(self, today, assets, out, data):
        ndays = data.shape[0]

        # Initialize weights array
        weights = arange(1, ndays + 1, dtype=float64_dtype).reshape(ndays, 1)

        # Compute normalizer
        normalizer = (ndays * (ndays + 1)) / 2

        # Weight the data
        weighted_data = data * weights

        # Compute weighted averages
        out[:] = nansum(weighted_data, axis=0) / normalizer


class AnnualizedVolatility(CustomFactor):
    """
    Factor that calculates annualized volatility, the degree of variation
    of a series over time as measured by the standard deviation of daily
    returns. https://en.wikipedia.org/wiki/Volatility_(finance)

    **Default Inputs:** [Returns(window_length=2)]

    Parameters
    ----------
    annualization_factor : float, optional
        The number of time units per year. Defaults is 252, the number of NYSE
        trading days in a normal year.

    mask : zipline.pipeline.Filter, optional
        A Filter representing assets to consider when computing results.
        If supplied, we ignore asset/date pairs where ``mask`` produces
        ``False``.

    Examples
    --------

    Calculate annualized volatility:

    >>> annual_vol = AnnualizedVolatility()
    """
    inputs = [Returns(window_length=2)]
    params = {'annualization_factor': 252.0}
    window_length = 252

    if TYPE_CHECKING:
        def __init__(self,
                     annualization_factor: float = 252,
                     mask: 'Filter' = None):
            pass

    def compute(self, today, assets, out, returns, annualization_factor):
        out[:] = nanstd(returns, axis=0) * (annualization_factor ** .5)


class PeerCount(SingleInputMixin, CustomFactor):
    """
    Factor that calculates peer count of distinct categories in a given
    classifier.  This factor is returned by the classifier instance method
    peer_count()

    **Default Inputs:** None

    **Default Window Length:** 1
    """
    window_length = 1

    def _validate(self):
        super(PeerCount, self)._validate()
        if self.window_length != 1:
            raise ValueError(
                "'PeerCount' expected a window length of 1, but was given"
                "{window_length}.".format(window_length=self.window_length)
            )

    def compute(self, today, assets, out, classifier_values):
        # Convert classifier array to group label int array
        group_labels, null_label = self.inputs[0]._to_integral(
            classifier_values[0]
        )
        _, inverse, counts = unique(  # Get counts, idx of unique groups
            group_labels,
            return_counts=True,
            return_inverse=True,
        )
        copyto(out, counts[inverse], where=(group_labels != null_label))


# Convenience aliases
EWMA = ExponentialWeightedMovingAverage
EWMSTD = ExponentialWeightedMovingStdDev


class Clip(CustomFactor):
    """
    Factor that clips (limits) the values in a factor.

    Given an interval, values outside the interval are clipped to the interval
    edges. For example, if an interval of ``[0, 1]`` is specified, values
    smaller than 0 become 0, and values larger than 1 become 1.

    **Default Window Length:** 1

    Parameters
    ----------
    min_bound : float
        The minimum value to use.
    max_bound : float
        The maximum value to use.

    Notes
    -----
    To only clip values on one side, ``-np.inf` and ``np.inf`` may be passed.
    For example, to only clip the maximum value but not clip a minimum value:

    .. code-block:: python

       Clip(inputs=[factor], min_bound=-np.inf, max_bound=user_provided_max)

    See Also
    --------
    numpy.clip
    """
    window_length = 1
    params = ('min_bound', 'max_bound')

    def compute(self, today, assets, out, values, min_bound, max_bound):
        clip(values[-1], min_bound, max_bound, out=out)
