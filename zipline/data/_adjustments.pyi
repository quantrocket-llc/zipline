Timestamp_t = ...
DatetimeIndex_t = ...
Int64Index_t = ...

_SID_QUERY_TEMPLATE = ...
SID_QUERIES = ...

ADJ_QUERY_TEMPLATE = ...

EPOCH = ...

def _get_sids_from_table(db,
                         tablename,
                         start_date,
                         end_date):
    """
    Get the unique sids for all adjustments between start_date and end_date
    from table `tablename`.

    Parameters
    ----------
    db : sqlite3.connection
    tablename : str
    start_date : int (seconds since epoch)
    end_date : int (seconds since epoch)

    Returns
    -------
    sids : set
        Set of sets
    """
    ...

def _get_split_sids(db, start_date, end_date): ...

def _get_merger_sids(db, start_date, end_date): ...

def _get_dividend_sids(db, start_date, end_date): ...

def _adjustments(adjustments_db,
                 split_sids,
                 merger_sids,
                 dividends_sids,
                 start_date,
                 end_date,
                 assets):
    ...

def load_adjustments_from_sqlite(adjustments_db,
                                 dates,
                                 assets,
                                 should_include_splits,
                                 should_include_mergers,
                                 should_include_dividends,
                                 adjustment_type):
    """
    Load a dictionary of Adjustment objects from adjustments_db.

    Parameters
    ----------
    adjustments_db : sqlite3.Connection
        Connection to a sqlite3 table in the format written by
        SQLiteAdjustmentWriter.
    dates : pd.DatetimeIndex
        Dates for which adjustments are needed.
    assets : pd.Int64Index
        Assets for which adjustments are needed.
    should_include_splits : bool
        Whether split adjustments should be included.
    should_include_mergers : bool
        Whether merger adjustments should be included.
    should_include_dividends : bool
        Whether dividend adjustments should be included.
    adjustment_type : str
        Whether price adjustments, volume adjustments, or both, should be
        included in the output.

    Returns
    -------
    adjustments : dict[str -> dict[int -> Adjustment]]
        A dictionary containing price and/or volume adjustment mappings from
        index to adjustment objects to apply at that index.
    """
    ...


def _lookup_dt(dt_cache,
               dt,
               fallback):
    ...
