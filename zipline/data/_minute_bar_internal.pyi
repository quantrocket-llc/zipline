def int_min(a, b): ...

def minute_value(market_opens,
                 pos,
                 minutes_per_day):
    """
    Finds the value of the minute represented by `pos` in the given array of
    market opens.

    Parameters
    ----------
    market_opens: numpy array of ints
        Market opens, in minute epoch values.

    pos: int
        The index of the desired minute.

    minutes_per_day: int
        The number of minutes per day (e.g. 390 for NYSE).

    Returns
    -------
    int: The minute epoch value of the desired minute.
    """
    ...

def find_position_of_minute(market_opens,
                            market_closes,
                            minute_val,
                            minutes_per_day,
                            forward_fill):
    """
    Finds the position of a given minute in the given array of market opens.
    If not a market minute, adjusts to the last market minute.

    Parameters
    ----------
    market_opens: numpy array of ints
        Market opens, in minute epoch values.

    market_closes: numpy array of ints
        Market closes, in minute epoch values.

    minute_val: int
        The desired minute, as a minute epoch.

    minutes_per_day: int
        The number of minutes per day (e.g. 390 for NYSE).

    forward_fill: bool
        Whether to use the previous market minute if the given minute does
        not fall within an open/close pair.

    Returns
    -------
    int: The position of the given minute in the market opens array.

    Raises
    ------
    ValueError
        If the given minute is not between a single open/close pair AND
        forward_fill is False.  For example, if minute_val is 17:00 Eastern
        for a given day whose normal hours are 9:30 to 16:00, and we are not
        forward filling, ValueError is raised.
    """
    ...

def find_last_traded_position_internal(
        market_opens,
        market_closes,
        end_minute,
        start_minute,
        volumes,
        minutes_per_day):
    """
    Finds the position of the last traded minute for the given volumes array.

    Parameters
    ----------
    market_opens: numpy array of ints
        Market opens, in minute epoch values.

    market_closes: numpy array of ints
        Market closes, in minute epoch values.

    end_minute: int
        The minute from which to start looking backwards, as a minute epoch.

    start_minute: int
        The asset's start date, as a minute epoch.  Acts as the bottom limit of
        how far we can look backwards.

    volumes: bcolz carray
        The volume history for the given asset.

    minutes_per_day: int
        The number of minutes per day (e.g. 390 for NYSE).

    Returns
    -------
    int: The position of the last traded minute, starting from `minute_val`
    """
    ...
