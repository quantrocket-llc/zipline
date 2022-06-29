
def update_position_last_sale_prices(positions, get_price, dt):
    """Update the positions' last sale prices.

    Parameters
    ----------
    positions : OrderedDict
        The positions to update.
    get_price : callable[Asset, float]
        The function to retrieve the price for the asset.
    dt : pd.Timestamp
        The dt to set as the last sale date if the price is not nan.
    """
    ...

class PositionStats:
    """Computed values from the current positions.

    Parameters
    ----------
    gross_exposure : float64
        The gross position exposure.
    gross_value : float64
        The gross position value.
    long_exposure : float64
        The exposure of just the long positions.
    long_value : float64
        The value of just the long positions.
    net_exposure : float64
        The net position exposure.
    net_value : float64
        The net position value.
    short_exposure : float64
        The exposure of just the short positions.
    short_value : float64
        The value of just the short positions.
    longs_count : int64
        The number of long positions.
    shorts_count : int64
        The number of short positions.
    position_exposure_array : np.ndarray[float64]
        The exposure of each position in the same order as
        ``position_tracker.positions``.
    position_exposure_series : pd.Series[float64]
        The exposure of each position in the same order as
        ``position_tracker.positions``. The index is the numeric sid of each
        asset.

    Notes
    -----
    ``position_exposure_array`` and ``position_exposure_series`` share the same
    underlying memory. The array interface should be preferred if you are doing
    access each minute for better performance.

    ``position_exposure_array`` and ``position_exposure_series`` may be mutated
    when the position tracker next updates the stats. Do not rely on these
    objects being preserved across accesses to ``stats``. If you need to freeze
    the values, you must take a copy.
    """
    ...

def calculate_position_tracker_stats(positions, stats):
    """Calculate various stats about the current positions.

    Parameters
    ----------
    positions : OrderedDict
        The ordered dictionary of positions.

    Returns
    -------
    position_stats : PositionStats
        The computed statistics.
    """
    ...

def minute_annual_volatility(date_labels,
                             minute_returns,
                             daily_returns):
    """Pre-compute the minute cumulative volatility field.
    """
    ...
