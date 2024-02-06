"""
Helpers for downsampling code.
"""
from operator import attrgetter
from typing import Literal

from zipline.utils.numpy_utils import changed_locations

_dt_to_period = {
    'year_start': attrgetter('year'),
    'quarter_start': attrgetter('quarter'),
    'month_start': attrgetter('month'),
    'week_start': attrgetter('week'),
}


def select_sampling_indices(dates, frequency: Literal['year_start', 'quarter_start', 'month_start', 'week_start']):
    """
    Choose entries from ``dates`` to use for downsampling at ``frequency``.

    Parameters
    ----------
    dates : pd.DatetimeIndex
        Dates from which to select sample choices.
    frequency : {'year_start', 'quarter_start', 'month_start', 'week_start'}
        A string indicating desired sampling dates:

        * 'year_start'    -> first trading day of each year
        * 'quarter_start' -> first trading day of January, April, July, October
        * 'month_start'   -> first trading day of each month
        * 'week_start'    -> first trading_day of each week

    Returns
    -------
    indices : np.array[int64]
        An array condtaining indices of dates on which samples should be taken.

        The resulting index will always include 0 as a sample index, and it
        will include the first date of each subsequent year/quarter/month/week,
        as determined by ``frequency``.

    Notes
    -----
    This function assumes that ``dates`` does not have large gaps.

    In particular, it assumes that the maximum distance between any two entries
    in ``dates`` is never greater than a year, which we rely on because we use
    ``np.diff(dates.<frequency>)`` to find dates where the sampling
    period has changed.
    """
    if frequency == "week_start":
        # dates.week is deprecated, uses dates.isocalendar().week
        dates = dates.isocalendar()

    return changed_locations(
        _dt_to_period[frequency](dates),
        include_first=True
    )
