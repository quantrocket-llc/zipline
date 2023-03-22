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
Pipeline terms for working with periodic data (such as quarterly
fundamentals).

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
