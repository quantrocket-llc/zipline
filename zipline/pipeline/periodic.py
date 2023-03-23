# Copyright 2023 QuantRocket LLC - All Rights Reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Pipeline factors and filters for working with periodic data, defined as data
that doesn't change daily but changes at less frequent intervals, such as quarterly
or annual fundamentals. Specifically, these factors and filters are compatible
with any Pipeline DataSet that has a `period_offset` coordinate.

Functions
---------
PeriodicAverage
    Return a Factor that computes the average of a column or factor over a
    specified number of periods.

PeriodicHigh
    Return a Factor that computes the high of a column or factor over a
    specified number of periods.

PeriodicLow
    Return a Factor that computes the low of a column or factor over a
    specified number of periods.

PeriodicPercentChange
    Return a Factor that computes the percent change of a column or factor over a
    specified number of periods.

PeriodicCAGR
    Return a Factor that computes the compound annual growth rate (CAGR)
    of a column or factor over a specified number of periods.

AllPeriodsIncreasing
    Return a Filter that computes whether a column or factor increases
    from the previous period over each of a specified number of periods.

AllPeriodsDecreasing
    Return a Filter that computes whether a column or factor decreases
    over each of a specified number of periods.

CountPeriodsAbove
    Return a Factor that computes how many times a column or factor is above a certain
    value over a specified number of periods.

CountPeriodsBelow
    Return a Factor that computes how many times a column or factor is below a certain
    value over a specified number of periods.

AllPeriodsAbove
    Return a Filter that computes whether a column or factor is above a certain
    value over each of a specified number of periods.

AllPeriodsBelow
    Return a Filter that computes whether a column or factor is below a certain
    value over each of a specified number of periods.

AllPeriodsPresent
    Return a Filter that computes whether a column or factor is present in the
    data over each of a specified number of periods.
"""
from typing import Union, Callable
import inspect
from zipline.pipeline.factors import Factor, Latest
from zipline.pipeline.filters import Filter
from zipline.pipeline.data.dataset import BoundColumn

ColumnOrCallable = Union[
    BoundColumn, Callable[[int, Filter], Factor]]

__all__ = [
    "PeriodicAverage",
    "PeriodicHigh",
    "PeriodicLow",
    "PeriodicPercentChange",
    "PeriodicCAGR",
    "AllPeriodsIncreasing",
    "AllPeriodsDecreasing",
    "CountPeriodsAbove",
    "CountPeriodsBelow",
    "AllPeriodsAbove",
    "AllPeriodsBelow",
    "AllPeriodsPresent",
]

def _unpack_column_or_callable(column_or_callable, **kwargs):
    """
    Validates column_or_callable and unpacks its period_offset and
    kwargs/coordinates. Returns a tuple of (is_column, period_offset,
    extra_coords).
    """

    if isinstance(column_or_callable, BoundColumn):
        is_column = True
    elif callable(column_or_callable):
        is_column = False
    else:
        msg = f"expected a BoundColumn or callable but got {column_or_callable}"
        if type(column_or_callable).__name__ == 'Latest':
            msg += f". Hint: pass the column itself instead of column.latest."
        raise ValueError(msg)

    if is_column:
        if (
            not hasattr(column_or_callable.dataset, "extra_coords")
            or "period_offset" not in column_or_callable.dataset.extra_coords
            ):
            raise ValueError(
                f"Column must belong to a DataSet with a period_offset coordinate but got: {column_or_callable}")

        extra_coords = column_or_callable.dataset.extra_coords.copy()
        period_offset = extra_coords.pop("period_offset")
    else:
        sig = inspect.signature(column_or_callable)
        if "period_offset" not in sig.parameters:
            raise ValueError(
                f"{column_or_callable.__name__} must have a period_offset parameter"
            )
        if "mask" not in sig.parameters:
            raise ValueError(
                f"{column_or_callable.__name__} must have a mask parameter"
            )
        period_offset = 0
        extra_coords = kwargs

    return is_column, period_offset, extra_coords

def _get_range(window_length, step):
    if window_length < 2:
        raise ValueError("window_length must be 2 or greater")

    if step >= window_length:
        raise ValueError("window_length must be greater than step")

    return range(1 + step - 1, window_length, step)

def PeriodicAverage(
    column_or_callable: ColumnOrCallable,
    window_length: int,
    step: int = 1,
    mask: Filter = None,
    **kwargs
    ) -> Factor:
    """
    Return a Factor that computes the average of a column or factor over a
    specified number of periods.

    Parameters
    ----------
    column_or_callable : BoundColumn or callable, required
        the dataset column to compute the average for. The column must
        belong to a Dataset that includes a period_offset coordinate.
        Alternatively, can be a function or other callable that accepts a
        period_offset and mask argument and returns a Factor.

    window_length : int, required
        the number of periods to use to calculate the average. Must be >=2.

    step : int, optional
        optional step for incrementing through window_length. This can be used
        to only sample certain periods in the computation. Default is 1,
        meaning use every period in window_length.

    mask : zipline.pipeline.Filter, optional
        optional Filter to limit the computation to a subset of stocks.

    **kwargs
        optional kwargs to pass to column_or_callable if it is a callable

    Returns
    -------
    zipline.pipeline.Factor
        a Factor that computes the average

    Examples
    --------
    Create a Factor that computes the average dividend per share over the last
    4 years, using annual financials::

        from zipline.pipeline.sharadar import Fundamentals
        from zipline.pipeline.periodic import PeriodicAverage

        dps = Fundamentals.slice('ARY').DPS
        avg_dps = PeriodicAverage(dps, window_length=4)

    Instead of passing a BoundColumn, we can also pass a function that returns
    a Factor. This is useful if we want to compute the average of a Factor that
    is not a column in a Dataset. For example, the Sharadar data does not include
    a column for operating margin, but it can easily be calculated by dividing
    operating income (`OPINC`) by revenue (`REVENUE`). First, create a function to
    calculate operating margin. The function should accept a `period_offset` and
    `mask` argument::

        from zipline.pipeline.factors import Latest

        def operating_margin(period_offset=0, mask=None):
            fundamentals = Fundamentals.slice("ARY", period_offset)
            return Latest(fundamentals.OPINC, mask=mask) / Latest(fundamentals.REVENUE, mask=mask)

    Then, pass the function to `PeriodicAverage`::

        avg_op_margin = PeriodicAverage(operating_margin, window_length=4)
    """

    is_column, period_offset, extra_coords = _unpack_column_or_callable(
        column_or_callable, **kwargs)

    if is_column:
        expr = Latest(column_or_callable, mask=mask)
    else:
        expr = Latest(column_or_callable(period_offset=0), mask=mask)

    offsets = list(_get_range(window_length, step))
    for i in offsets:
        if is_column:
            previous_dataset = column_or_callable.dataset.dataset_family.slice(
                period_offset=period_offset-i,
                **extra_coords)
            previous_column = getattr(previous_dataset, column_or_callable.name)
            expr += Latest(previous_column, mask=mask)
        else:
            previous = column_or_callable(period_offset=-i, mask=mask, **kwargs)
            expr += previous

    expr = expr / (len(offsets) + 1)

    return expr

def PeriodicHigh(
    column_or_callable: ColumnOrCallable,
    window_length: int,
    step: int = 1,
    mask: Filter = None,
    **kwargs
    ) -> Factor:
    """
    Return a Factor that computes the high of a column or factor over a
    specified number of periods.

    Parameters
    ----------
    column_or_callable : BoundColumn or callable, required
        the dataset column to compute the high for. The column must
        belong to a Dataset that includes a period_offset coordinate.
        Alternatively, can be a function or other callable that accepts a
        period_offset and mask argument and returns a Factor.

    window_length : int, required
        the number of periods to use to calculate the high. Must be >=2.

    step : int, optional
        optional step for incrementing through window_length. This can be used
        to only sample certain periods in the computation. Default is 1,
        meaning use every period in window_length.

    mask : zipline.pipeline.Filter, optional
        optional Filter to limit the computation to a subset of stocks.

    **kwargs
        optional kwargs to pass to column_or_callable if it is a callable

    Returns
    -------
    zipline.pipeline.Factor
        a Factor that computes the high

    Examples
    --------
    Create a Factor that computes the highest EPS over the last 4 quarters, using
    trailing-twelve-month financials::

        from zipline.pipeline.sharadar import Fundamentals
        from zipline.pipeline.periodic import PeriodicHigh

        eps = Fundamentals.slice('ART').EPS
        highest_eps = PeriodicHigh(eps, window_length=4)

    Instead of passing a BoundColumn, we can also pass a function that returns
    a Factor. This is useful if we want to compute the high of a Factor that
    is not a column in a Dataset. For example, the Sharadar data does not include
    a column for operating margin, but it can easily be calculated by dividing
    operating income (`OPINC`) by revenue (`REVENUE`). First, create a function to
    calculate operating margin. The function should accept a `period_offset` and
    `mask` argument::

        from zipline.pipeline.factors import Latest

        def operating_margin(period_offset=0, mask=None):
            fundamentals = Fundamentals.slice("ART", period_offset)
            return Latest(fundamentals.OPINC, mask=mask) / Latest(fundamentals.REVENUE, mask=mask)

    Then, pass the function to `PeriodicHigh`::

        highest_op_margin = PeriodicHigh(operating_margin, window_length=4)
    """
    return _high_or_low(
        column_or_callable, window_length=window_length, step=step,
        high=True, mask=mask, **kwargs)

def PeriodicLow(
    column_or_callable: ColumnOrCallable,
    window_length: int,
    step: int = 1,
    mask: Filter = None,
    **kwargs
    ) -> Factor:
    """
    Return a Factor that computes the low of a column or factor over a
    specified number of periods.

    Parameters
    ----------
    column_or_callable : BoundColumn or callable, required
        the dataset column to compute the low for. The column must
        belong to a Dataset that includes a period_offset coordinate.
        Alternatively, can be a function or other callable that accepts a
        period_offset and mask argument and returns a Factor.

    window_length : int, required
        the number of periods to use to calculate the low. Must be >=2.

    step : int, optional
        optional step for incrementing through window_length. This can be used
        to only sample certain periods in the computation. Default is 1,
        meaning use every period in window_length.

    mask : zipline.pipeline.Filter, optional
        optional Filter to limit the computation to a subset of stocks.

    **kwargs
        optional kwargs to pass to column_or_callable if it is a callable

    Returns
    -------
    zipline.pipeline.Factor
        a Factor that computes the low

    Examples
    --------
    Create a Factor that computes the lowest EPS over the last 4 quarters, using
    trailing-twelve-month financials::

        from zipline.pipeline.sharadar import Fundamentals
        from zipline.pipeline.periodic import PeriodicLow

        eps = Fundamentals.slice('ART').EPS
        lowest_eps = PeriodicLow(eps, window_length=4)

    Instead of passing a BoundColumn, we can also pass a function that returns
    a Factor. This is useful if we want to compute the low of a Factor that
    is not a column in a Dataset. For example, the Sharadar data does not include
    a column for operating margin, but it can easily be calculated by dividing
    operating income (`OPINC`) by revenue (`REVENUE`). First, create a function to
    calculate operating margin. The function should accept a `period_offset` and
    `mask` argument::

        from zipline.pipeline.factors import Latest

        def operating_margin(period_offset=0, mask=None):
            fundamentals = Fundamentals.slice("ART", period_offset)
            return Latest(fundamentals.OPINC, mask=mask) / Latest(fundamentals.REVENUE, mask=mask)

    Then, pass the function to `PeriodicLow`::

        lowest_op_margin = PeriodicLow(operating_margin, window_length=4)
    """
    return _high_or_low(
        column_or_callable, window_length=window_length, step=step,
        high=False, mask=mask, **kwargs)

def _high_or_low(
    column_or_callable, window_length, step, high, mask=None, **kwargs):

    is_column, period_offset, extra_coords = _unpack_column_or_callable(
        column_or_callable, **kwargs)

    all_terms = []

    if is_column:
        term = Latest(column_or_callable, mask=mask)
    else:
        term = Latest(column_or_callable(period_offset=0), mask=mask)

    all_terms.append(term)

    for i in _get_range(window_length, step):
        if is_column:
            previous_dataset = column_or_callable.dataset.dataset_family.slice(
                period_offset=period_offset-i,
                **extra_coords)
            previous_column = getattr(previous_dataset, column_or_callable.name)
            term = Latest(previous_column, mask=mask)
        else:
            term = column_or_callable(period_offset=-i, mask=mask, **kwargs)

        all_terms.append(term)


        # high can be calculated bitwise as:
        #   (a > b) × a + (b > a) × b
        # how it works:
        # Case 1: When a is greater 
        #   (a > b) × a + (b > a) × b = 1 × a + 0 × b = a 
        # Case 2: When b is greater 
        #   (a > b) × a + (b > a) × b = 0 × a + 1 × b = b
        # hat tip: https://www.techiedelight.com/find-maximum-number-without-using-conditional-statement-ternary-operator/
        #
        # For more than two terms, it looks like this:
        #    (a > b & a > c) × a + (b > a & b > c) × b + (c > a & c > b) × c

    expr = None

    for term in all_terms:

        other_terms = all_terms.copy()
        other_terms.remove(term)

        _expr = None

        for other_term in other_terms:

            if high:
                _subexpr = term > other_term
            else:
                _subexpr = term < other_term

            if _expr is None:
                _expr = _subexpr
            else:
                _expr &= _subexpr

        _expr = _expr.as_factor() * term

        if expr is None:
            expr = _expr
        else:
            expr += _expr

    return expr

def PeriodicPercentChange(
    column_or_callable: ColumnOrCallable,
    window_length: int,
    mask: Filter = None,
    **kwargs
    ) -> Factor:
    """
    Return a Factor that computes the percent change of a column or factor over a
    specified number of periods.

    Parameters
    ----------
    column_or_callable : BoundColumn or callable, required
        the dataset column to compute the percent change for. The column must
        belong to a Dataset that includes a period_offset coordinate.
        Alternatively, can be a function or other callable that accepts a
        period_offset and mask argument and returns a Factor.

    window_length : int, required
        the number of periods to use to calculate the percent change. Must be >=2.

    mask : zipline.pipeline.Filter, optional
        optional Filter to limit the computation to a subset of stocks.

    **kwargs
        optional kwargs to pass to column_or_callable if it is a callable

    Returns
    -------
    zipline.pipeline.Factor
        a Factor that computes the percent change

    Examples
    --------
    Create a Factor that computes the percent change in dividend yield over the
    last 16 quarters, using trailing-twelve-month financials::

        from zipline.pipeline.sharadar import Fundamentals
        from zipline.pipeline.periodic import PeriodicPercentChange

        divyield = Fundamentals.slice('ART').DIVYIELD
        divyield_pct_change = PeriodicPercentChange(divyield, window_length=16)

    Instead of passing a BoundColumn, we can also pass a function that returns
    a Factor. This is useful if we want to compute the percent change of a Factor that
    is not a column in a Dataset. For example, the Sharadar data does not include
    a column for operating margin, but it can easily be calculated by dividing
    operating income (`OPINC`) by revenue (`REVENUE`). First, create a function to
    calculate operating margin. The function should accept a `period_offset` and
    `mask` argument::

        from zipline.pipeline.factors import Latest

        def operating_margin(period_offset=0, mask=None):
            fundamentals = Fundamentals.slice("ART", period_offset)
            return Latest(fundamentals.OPINC, mask=mask) / Latest(fundamentals.REVENUE, mask=mask)

    Then, pass the function to `PeriodicPercentChange`::

        op_margin_pct_change = PeriodicPercentChange(operating_margin, window_length=16)
    """

    is_column, period_offset, extra_coords = _unpack_column_or_callable(
        column_or_callable, **kwargs)

    previous_period_offset = period_offset - (window_length - 1)

    if is_column:
        current = Latest(column_or_callable, mask=mask)
        previous_dataset = column_or_callable.dataset.dataset_family.slice(
            period_offset=previous_period_offset,
                **extra_coords)
        previous = getattr(previous_dataset, column_or_callable.name)
        previous = Latest(previous, mask=mask)
    else:
        current = column_or_callable(
            period_offset=0, mask=mask, **kwargs)
        previous = column_or_callable(
            period_offset=previous_period_offset, mask=mask, **kwargs)

    return (current - previous) / previous.abs()

def PeriodicCAGR(
    column_or_callable: ColumnOrCallable,
    window_length: int,
    periods_per_year: int = None,
    mask: Filter = None,
    **kwargs
    ) -> Factor:
    """
    Return a Factor that computes the compound annual growth rate (CAGR)
    of a column or factor over a specified number of periods.

    Parameters
    ----------
    column_or_callable : BoundColumn or callable, required
        the dataset column to compute the CAGR for. The column must
        belong to a Dataset that includes a period_offset coordinate.
        Alternatively, can be a function or other callable that accepts a
        period_offset and mask argument and returns a Factor.

    window_length : int, required
        the number of periods to use to calculate the CAGR. Must be >=2.

    periods_per_year : int, optional
        the number of periods per year. If omitted and column_or_callable
        is a BoundColumn with a `dimension` coordinate, the periods per year
        will be inferred from that; otherwise it must be specified.

    mask : zipline.pipeline.Filter, optional
        optional Filter to limit the computation to a subset of stocks.

    **kwargs
        optional kwargs to pass to column_or_callable if it is a callable

    Returns
    -------
    zipline.pipeline.Factor
        a Factor that computes the CAGR

    Examples
    --------
    Create a Factor that computes the compound annual growth rate (CAGR) in
    dividend per share over the last 16 quarters, using trailing-twelve-month
    financials::

        from zipline.pipeline.sharadar import Fundamentals
        from zipline.pipeline.periodic import PeriodicCAGR

        dps = Fundamentals.slice('ART').DPS
        dps_growth = PeriodicCAGR(dps, window_length=16)

    Instead of passing a BoundColumn, we can also pass a function that returns
    a Factor. This is useful if we want to compute the CAGR of a Factor that
    is not a column in a Dataset. For example, the Sharadar data does not include
    a column for operating margin, but it can easily be calculated by dividing
    operating income (`OPINC`) by revenue (`REVENUE`). First, create a function to
    calculate operating margin. The function should accept a `period_offset` and
    `mask` argument::

        from zipline.pipeline.factors import Latest

        def operating_margin(period_offset=0, mask=None):
            fundamentals = Fundamentals.slice("ART", period_offset)
            return Latest(fundamentals.OPINC, mask=mask) / Latest(fundamentals.REVENUE, mask=mask)

    Then, pass the function to `PeriodicCAGR`::

        op_margin_growth = PeriodicCAGR(operating_margin, window_length=16)
    """

    is_column, period_offset, extra_coords = _unpack_column_or_callable(
        column_or_callable, **kwargs)

    if not periods_per_year:
        if is_column and "dimension" in extra_coords:
            dimension = extra_coords["dimension"]
            if dimension.endswith("Y"):
                periods_per_year = 1
            elif dimension.endswith("Q") or dimension.endswith("T"):
                periods_per_year = 4

    if not periods_per_year:
        raise ValueError(
            "periods_per_year cannot be inferred and must be specified")

    if periods_per_year > window_length:
        raise ValueError(
            f"window_length ({window_length}) must be greater than "
            f"periods_per_year ({periods_per_year})")

    previous_period_offset = period_offset - (window_length - 1)

    if is_column:
        current = Latest(column_or_callable, mask=mask)
        previous_dataset = column_or_callable.dataset.dataset_family.slice(
            period_offset=previous_period_offset,
                **extra_coords)
        previous = getattr(previous_dataset, column_or_callable.name)
        previous = Latest(previous, mask=mask)
    else:
        current = column_or_callable(
            period_offset=0, mask=mask, **kwargs)
        previous = column_or_callable(
            period_offset=previous_period_offset, mask=mask, **kwargs)

    years = window_length / periods_per_year

    # Ignore if previous is not positive
    previous = previous.where(previous > 0)

    return (current/previous)**(1/years) - 1

def AllPeriodsIncreasing(
    column_or_callable: ColumnOrCallable,
    window_length: int,
    step: int = 1,
    allow_equal: bool = False,
    mask: Filter = None,
    **kwargs
    ) -> Filter:
    """
    Return a Filter that computes whether a column or factor increases
    from the previous period over each of a specified number of periods.

    Parameters
    ----------
    column_or_callable : BoundColumn or callable, required
        the dataset column to check for increasing values. The column must
        belong to a Dataset that includes a period_offset coordinate.
        Alternatively, can be a function or other callable that accepts a
        period_offset and mask argument and returns a Factor.

    window_length : int, required
        the number of periods over which to check for increasing values.
        Must be >=2.

    step : int, optional
        optional step for incrementing through window_length. This can be used
        to only sample certain periods in the computation. Default is 1,
        meaning use every period in window_length.

    allow_equal : bool
        if True, allow values to be the same or higher than the previous period.
        If False, only allow values to be higher than the previous period.
        Default False.

    mask : zipline.pipeline.Filter, optional
        optional Filter to limit the computation to a subset of stocks.

    **kwargs
        optional kwargs to pass to column_or_callable if it is a callable

    Returns
    -------
    zipline.pipeline.Filter
        a Filter indicating whether the input factor increases over time

    Examples
    --------
    Create a Filter that returns True if revenue increased versus the prior
    year for each of the last 4 years, using annual financials::

        from zipline.pipeline.sharadar import Fundamentals
        from zipline.pipeline.periodic import AllPeriodsIncreasing

        revenue = Fundamentals.slice('ARY').REVENUE
        has_consistent_sales_growth = AllPeriodsIncreasing(revenue, window_length=4)

    Instead of passing a BoundColumn, we can also pass a function that returns
    a Factor. This is useful if we want to apply the filter to a Factor that
    is not a column in a Dataset. For example, the Sharadar data does not include
    a column for operating margin, but it can easily be calculated by dividing
    operating income (`OPINC`) by revenue (`REVENUE`). First, create a function to
    calculate operating margin. The function should accept a `period_offset` and
    `mask` argument::

        from zipline.pipeline.factors import Latest

        def operating_margin(period_offset=0, mask=None):
            fundamentals = Fundamentals.slice("ARY", period_offset)
            return Latest(fundamentals.OPINC, mask=mask) / Latest(fundamentals.REVENUE, mask=mask)

    Then, pass the function to `AllPeriodsIncreasing`::

        has_consistent_op_margin_growth = AllPeriodsIncreasing(operating_margin, window_length=4)
    """
    return _increasing_or_decreasing(
        column_or_callable, window_length=window_length, step=step,
        increasing=True, allow_equal=allow_equal, mask=mask, **kwargs)

def AllPeriodsDecreasing(
    column_or_callable: ColumnOrCallable,
    window_length: int,
    step: int = 1,
    allow_equal: bool = False,
    mask: Filter = None,
    **kwargs
    ) -> Filter:
    """
    Return a Filter that computes whether a column or factor decreases
    over each of a specified number of periods.

    Parameters
    ----------
    column_or_callable : BoundColumn or callable, required
        the dataset column to check for decreasing values. The column must
        belong to a Dataset that includes a period_offset coordinate.
        Alternatively, can be a function or other callable that accepts a
        period_offset and mask argument and returns a Factor.

    window_length : int, required
        the number of periods over which to check for decreasing values.
        Must be >=2.

    step : int, optional
        optional step for incrementing through window_length. This can be used
        to only sample certain periods in the computation. Default is 1,
        meaning use every period in window_length.

    allow_equal : bool
        if True, allow values to be the same or lower than the previous period.
        If False, only allow values to be lower than the previous period.
        Default False.

    mask : zipline.pipeline.Filter, optional
        optional Filter to limit the computation to a subset of stocks.

    **kwargs
        optional kwargs to pass to column_or_callable if it is a callable

    Returns
    -------
    zipline.pipeline.Filter
        a Filter indicating whether the input factor decreases over time

    Examples
    --------
    Create a Filter that returns True if debt decreased versus the prior
    year for each of the last 4 years, using annual financials::

        from zipline.pipeline.sharadar import Fundamentals
        from zipline.pipeline.periodic import AllPeriodsDecreasing

        debt = Fundamentals.slice('ARY').DEBT
        has_declining_debt = AllPeriodsDecreasing(debt, window_length=4)

    Instead of passing a BoundColumn, we can also pass a function that returns
    a Factor. This is useful if we want to apply the filter to a Factor that
    is not a column in a Dataset. For example, the Sharadar data does not include
    a column for operating margin, but it can easily be calculated by dividing
    operating income (`OPINC`) by revenue (`REVENUE`). First, create a function to
    calculate operating margin. The function should accept a `period_offset` and
    `mask` argument::

        from zipline.pipeline.factors import Latest

        def operating_margin(period_offset=0, mask=None):
            fundamentals = Fundamentals.slice("ARY", period_offset)
            return Latest(fundamentals.OPINC, mask=mask) / Latest(fundamentals.REVENUE, mask=mask)

    Then, pass the function to `AllPeriodsDecreasing`::

        has_declining_op_margin = AllPeriodsDecreasing(operating_margin, window_length=4)
    """
    return _increasing_or_decreasing(
        column_or_callable, window_length=window_length, step=step,
        increasing=False, allow_equal=allow_equal, mask=mask, **kwargs)

def _increasing_or_decreasing(
    column_or_callable, window_length, step, increasing, allow_equal, mask=None, **kwargs):

    is_column, period_offset, extra_coords = _unpack_column_or_callable(
        column_or_callable, **kwargs)

    expr = None

    if is_column:
        later_term = Latest(column_or_callable, mask=mask)
    else:
        later_term = Latest(column_or_callable(period_offset=0), mask=mask)

    for i in _get_range(window_length, step):
        if is_column:
            previous_dataset = column_or_callable.dataset.dataset_family.slice(
                period_offset=period_offset-i,
                **extra_coords)
            previous_column = getattr(previous_dataset, column_or_callable.name)
            term = Latest(previous_column, mask=mask)
        else:
            term = column_or_callable(period_offset=-i, mask=mask, **kwargs)

        if increasing:
            _expr = (later_term >= term) if allow_equal else (later_term > term)
        else:
            _expr = (later_term <= term) if allow_equal else (later_term < term)

        if expr is None:
            expr = _expr
        else:
            expr &= _expr

        later_term = term

    return expr

def CountPeriodsAbove(
    column_or_callable: ColumnOrCallable,
    value: Union[int, float],
    window_length: int,
    step: int = 1,
    allow_equal: bool = False,
    mask: Filter = None,
    **kwargs
    ) -> Factor:
    """
    Return a Factor that computes how many times a column or factor is above a certain
    value over a specified number of periods.

    Parameters
    ----------
    column_or_callable : BoundColumn or callable, required
        the dataset column to check. The column must
        belong to a Dataset that includes a period_offset coordinate.
        Alternatively, can be a function or other callable that accepts a
        period_offset and mask argument and returns a Factor.

    value : int or float, required
        the value that the factor must be above

    window_length : int, required
        the number of periods over which the factor must be above the value.

    step : int, optional
        optional step for incrementing through window_length. This can be used
        to only sample certain periods in the computation. Default is 1,
        meaning use every period in window_length.

    allow_equal : bool
        if True, count periods that are above or equal to the value. If False,
        only count periods that are above the value. Default False.

    mask : zipline.pipeline.Filter, optional
        optional Filter to limit the computation to a subset of stocks.

    **kwargs
        optional kwargs to pass to column_or_callable if it is a callable

    Returns
    -------
    zipline.pipeline.Factor
        a Factor counting how many times the input factor is above the value over
        the window_length

    Examples
    --------
    Create a Factor that computes the number of quarters with positive EBIT out
    of the last 8 quarters, using trailing-twelve-month financials::

        from zipline.pipeline.sharadar import Fundamentals
        from zipline.pipeline.periodic import CountPeriodsAbove

        ebit = Fundamentals.slice('ART').EBIT
        positive_ebit_count = CountPeriodsAbove(ebit, 0, window_length=8)

    Instead of passing a BoundColumn, we can also pass a function that returns
    a Factor. This is useful if we want to apply the count to a Factor that
    is not a column in a Dataset. For example, the Sharadar data does not include
    a column for operating margin, but it can easily be calculated by dividing
    operating income (`OPINC`) by revenue (`REVENUE`). First, create a function to
    calculate operating margin. The function should accept a `period_offset` and
    `mask` argument::

        from zipline.pipeline.factors import Latest

        def operating_margin(period_offset=0, mask=None):
            fundamentals = Fundamentals.slice("ART", period_offset)
            return Latest(fundamentals.OPINC, mask=mask) / Latest(fundamentals.REVENUE, mask=mask)

    Then, pass the function to `CountPeriodsAbove`. Here, we count periods with
    operating margin greater than 15%::

        good_op_margin_count = CountPeriodsAbove(operating_margin, 0.15, window_length=8)
    """
    return _count_above_or_below_or_equal(
        column_or_callable, window_length=window_length, step=step, value=value,
        allow_above=True, allow_below=False, allow_equal=allow_equal, mask=mask,
        **kwargs)

def CountPeriodsBelow(
    column_or_callable: ColumnOrCallable,
    value: Union[int, float],
    window_length: int,
    step: int = 1,
    allow_equal: bool = False,
    mask: Filter = None,
    **kwargs
    ) -> Factor:
    """
    Return a Factor that computes how many times a column or factor is below a certain
    value over a specified number of periods.

    Parameters
    ----------
    column_or_callable : BoundColumn or callable, required
        the dataset column to check. The column must
        belong to a Dataset that includes a period_offset coordinate.
        Alternatively, can be a function or other callable that accepts a
        period_offset and mask argument and returns a Factor.

    value : int or float, required
        the value that the factor must be below

    window_length : int, required
        the number of periods over which the factor must be below the value.

    step : int, optional
        optional step for incrementing through window_length. This can be used
        to only sample certain periods in the computation. Default is 1,
        meaning use every period in window_length.

    allow_equal : bool
        if True, count periods that are below or equal to the value. If False,
        only count periods that are below the value. Default False.

    mask : zipline.pipeline.Filter, optional
        optional Filter to limit the computation to a subset of stocks.

    **kwargs
        optional kwargs to pass to column_or_callable if it is a callable

    Returns
    -------
    zipline.pipeline.Factor
        a Factor counting how many times the input factor is below the value over
        the window_length

    Examples
    --------
    Create a Factor that computes the number of quarters with negative EBIT out
    of the last 8 quarters, using trailing-twelve-month financials::

        from zipline.pipeline.sharadar import Fundamentals
        from zipline.pipeline.periodic import CountPeriodsBelow

        ebit = Fundamentals.slice('ART').EBIT
        negative_ebit_count = CountPeriodsBelow(ebit, 0, window_length=8)

    Instead of passing a BoundColumn, we can also pass a function that returns
    a Factor. This is useful if we want to apply the count to a Factor that
    is not a column in a Dataset. For example, the Sharadar data does not include
    a column for operating margin, but it can easily be calculated by dividing
    operating income (`OPINC`) by revenue (`REVENUE`). First, create a function to
    calculate operating margin. The function should accept a `period_offset` and
    `mask` argument::

        from zipline.pipeline.factors import Latest

        def operating_margin(period_offset=0, mask=None):
            fundamentals = Fundamentals.slice("ART", period_offset)
            return Latest(fundamentals.OPINC, mask=mask) / Latest(fundamentals.REVENUE, mask=mask)

    Then, pass the function to `CountPeriodsBelow`. Here, we count periods with
    operating margin lower than 5%::

        low_op_margin_count = CountPeriodsBelow(operating_margin, 0.05, window_length=8)
    """
    return _count_above_or_below_or_equal(
        column_or_callable, window_length=window_length, step=step, value=value,
        allow_above=False, allow_below=True, allow_equal=allow_equal, mask=mask,
        **kwargs)

def AllPeriodsAbove(
    column_or_callable: ColumnOrCallable,
    value: Union[int, float],
    window_length: int,
    step: int = 1,
    allow_equal: bool = False,
    mask: Filter = None,
    **kwargs
    ) -> Filter:
    """
    Return a Filter that computes whether a column or factor is above a certain
    value over each of a specified number of periods.

    Parameters
    ----------
    column_or_callable : BoundColumn or callable, required
        the dataset column to check. The column must
        belong to a Dataset that includes a period_offset coordinate.
        Alternatively, can be a function or other callable that accepts a
        period_offset and mask argument and returns a Factor.

    value : int or float, required
        the value that the factor must be above

    window_length : int, required
        the number of periods over which the factor must be above the value.

    step : int, optional
        optional step for incrementing through window_length. This can be used
        to only sample certain periods in the computation. Default is 1,
        meaning use every period in window_length.

    allow_equal : bool
        if True, allow factors to be above or equal to the value. If False,
        only allow factors to be above the value. Default False.

    mask : zipline.pipeline.Filter, optional
        optional Filter to limit the computation to a subset of stocks.

    **kwargs
        optional kwargs to pass to column_or_callable if it is a callable

    Returns
    -------
    zipline.pipeline.Filter
        a Filter indicating whether the input factor is above the value over
        the full window_length

    Examples
    --------
    Create a Filter that returns True if dividend per share was positive for
    each of the last 5 years, using annual financials::

        from zipline.pipeline.sharadar import Fundamentals
        from zipline.pipeline.periodic import AllPeriodsAbove

        dps = Fundamentals.slice('ARY').DPS
        consistently_has_dividends = AllPeriodsAbove(dps, 0, window_length=5)

    Instead of passing a BoundColumn, we can also pass a function that returns
    a Factor. This is useful if we want to apply the filter to a Factor that
    is not a column in a Dataset. For example, the Sharadar data does not include
    a column for operating margin, but it can easily be calculated by dividing
    operating income (`OPINC`) by revenue (`REVENUE`). First, create a function to
    calculate operating margin. The function should accept a `period_offset` and
    `mask` argument::

        from zipline.pipeline.factors import Latest

        def operating_margin(period_offset=0, mask=None):
            fundamentals = Fundamentals.slice("ARY", period_offset)
            return Latest(fundamentals.OPINC, mask=mask) / Latest(fundamentals.REVENUE, mask=mask)

    Then, pass the function to `AllPeriodsAbove`. Here, we look for companies with
    operating margin consistently above 15%::

        consistent_high_op_margin = AllPeriodsAbove(operating_margin, 0.15, window_length=5)
    """
    count = _count_above_or_below_or_equal(
        column_or_callable, window_length=window_length, step=step, value=value,
        allow_above=True, allow_below=False, allow_equal=allow_equal, mask=mask,
        **kwargs)
    return count.eq(len(count.inputs))

def AllPeriodsBelow(
    column_or_callable: ColumnOrCallable,
    value: Union[int, float],
    window_length: int,
    step: int=1,
    allow_equal: bool = False,
    mask: Filter = None,
    **kwargs
    ) -> Filter:
    """
    Return a Filter that computes whether a column or factor is below a certain
    value over each of a specified number of periods.

    Parameters
    ----------
    column_or_callable : BoundColumn or callable, required
        the dataset column to check. The column must
        belong to a Dataset that includes a period_offset coordinate.
        Alternatively, can be a function or other callable that accepts a
        period_offset and mask argument and returns a Factor.

    value : int or float, required
        the value that the factor must be below

    window_length : int, required
        the number of periods over which the factor must be below the value.

    step : int, optional
        optional step for incrementing through window_length. This can be used
        to only sample certain periods in the computation. Default is 1,
        meaning use every period in window_length.

    allow_equal : bool
        if True, count periods that are below or equal to the value. If False,
        only count periods that are below the value. Default False.

    mask : zipline.pipeline.Filter, optional
        optional Filter to limit the computation to a subset of stocks.

    **kwargs
        optional kwargs to pass to column_or_callable if it is a callable

    Returns
    -------
    zipline.pipeline.Filter
        a Filter indicating whether the input factor is below the value over
        the full window_length

    Examples
    --------
    Create a Filter that returns True if return on assets was below 5% for
    each of the last 5 years, using annual financials::

        from zipline.pipeline.sharadar import Fundamentals
        from zipline.pipeline.periodic import AllPeriodsBelow

        roa = Fundamentals.slice('ARY').ROA
        roa_below_5 = AllPeriodsBelow(roa, 0.05, window_length=5)

    Instead of passing a BoundColumn, we can also pass a function that returns
    a Factor. This is useful if we want to apply the filter to a Factor that
    is not a column in a Dataset. For example, the Sharadar data does not include
    a column for operating margin, but it can easily be calculated by dividing
    operating income (`OPINC`) by revenue (`REVENUE`). First, create a function to
    calculate operating margin. The function should accept a `period_offset` and
    `mask` argument::

        from zipline.pipeline.factors import Latest

        def operating_margin(period_offset=0, mask=None):
            fundamentals = Fundamentals.slice("ARY", period_offset)
            return Latest(fundamentals.OPINC, mask=mask) / Latest(fundamentals.REVENUE, mask=mask)

    Then, pass the function to `AllPeriodsBelow`. Here, we look for companies with
    operating margin consistently below 5%::

        consistent_low_op_margin = AllPeriodsBelow(operating_margin, 0.05, window_length=5)
    """
    count = _count_above_or_below_or_equal(
        column_or_callable, window_length=window_length, step=step, value=value,
        allow_above=False, allow_below=True, allow_equal=allow_equal, mask=mask,
        **kwargs)
    return count.eq(len(count.inputs))

def _count_above_or_below_or_equal(
    column_or_callable, window_length, step, value, allow_above, allow_below, allow_equal,
    mask=None, **kwargs):

    is_column, period_offset, extra_coords = _unpack_column_or_callable(
        column_or_callable, **kwargs)

    all_terms = []

    if is_column:
        all_terms.append(Latest(column_or_callable, mask=mask))
    else:
        all_terms.append(Latest(column_or_callable(period_offset=0), mask=mask))

    for i in _get_range(window_length, step):
        if is_column:
            previous_dataset = column_or_callable.dataset.dataset_family.slice(
                period_offset=period_offset-i,
                **extra_coords)
            previous_column = getattr(previous_dataset, column_or_callable.name)
            all_terms.append(Latest(previous_column, mask=mask))
        else:
            all_terms.append(column_or_callable(period_offset=-i, mask=mask, **kwargs))

    expr = None
    for term in all_terms:
        if allow_above:
            _expr = (term >= value) if allow_equal else (term > value)
        elif allow_below:
            _expr = (term <= value) if allow_equal else (term < value)
        else:
            _expr = (term.eq(value))

        # boolean to int
        _expr = _expr.as_factor()

        if expr is None:
            expr = _expr
        else:
            expr += _expr

    return expr

def AllPeriodsPresent(
    column_or_callable: ColumnOrCallable,
    window_length: int,
    step: int = 1,
    mask: Filter = None,
    **kwargs
    ) -> Filter:
    """
    Return a Filter that computes whether a column or factor is present in the
    data over each of a specified number of periods.

    Parameters
    ----------
    column_or_callable : BoundColumn or callable, required
        the dataset column to check. The column must
        belong to a Dataset that includes a period_offset coordinate.
        Alternatively, can be a function or other callable that accepts a
        period_offset and mask argument and returns a Factor.

    window_length : int, required
        the number of periods over which the factor must be present.

    step : int, optional
        optional step for incrementing through window_length. This can be used
        to only sample certain periods in the computation. Default is 1,
        meaning use every period in window_length.

    mask : zipline.pipeline.Filter, optional
        optional Filter to limit the computation to a subset of stocks.

    **kwargs
        optional kwargs to pass to column_or_callable if it is a callable

    Returns
    -------
    zipline.pipeline.Filter
        a Filter indicating whether the input factor is present over the
        full window_length

    Examples
    --------
    Create a Filter that returns True if the MARKETCAP field is populated
    for each of the last 5 years, using annual financials::

        from zipline.pipeline.sharadar import Fundamentals
        from zipline.pipeline.periodic import AllPeriodsPresent

        marketcap = Fundamentals.slice('ARY').MARKETCAP
        has_5y_history = AllPeriodsPresent(marketcap, window_length=5)
    """
    is_column, period_offset, extra_coords = _unpack_column_or_callable(
        column_or_callable, **kwargs)

    all_terms = []

    if is_column:
        all_terms.append(Latest(column_or_callable, mask=mask))
    else:
        all_terms.append(Latest(column_or_callable(period_offset=0), mask=mask))

    for i in _get_range(window_length, step):
        if is_column:
            previous_dataset = column_or_callable.dataset.dataset_family.slice(
                period_offset=period_offset-i,
                **extra_coords)
            previous_column = getattr(previous_dataset, column_or_callable.name)
            all_terms.append(Latest(previous_column, mask=mask))
        else:
            all_terms.append(column_or_callable(period_offset=-i, mask=mask, **kwargs))

    expr = None
    for term in all_terms:
        _expr = term.notnull()

        if expr is None:
            expr = _expr
        else:
            expr &= _expr

    return expr
