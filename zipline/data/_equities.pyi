carray_t = ...
ctable_t = ...
Timestamp_t = ...
DatetimeIndex_t = ...
Int64Index_t = ...

def _compute_row_slices(asset_starts_absolute,
                        asset_ends_absolute,
                        asset_starts_calendar,
                        query_start,
                        query_end,
                        requested_assets):
    """
    Core indexing functionality for loading raw data from bcolz.

    For each asset in requested assets, computes three values:

    1.) The index in the raw bcolz data of first row to load.
    2.) The index in the raw bcolz data of the last row to load.
    3.) The index in the dates of our query corresponding to the first row for
        each asset. This is non-zero iff the asset's lifetime begins partway
        through the requested query dates.

    Values for unknown sids will be populated with a value of -1.

    Parameters
    ----------
    asset_starts_absolute : dict
        Dictionary containing the index of the first row of each asset in the
        bcolz file from which we will query.
    asset_ends_absolute : dict
        Dictionary containing the index of the last row of each asset in the
        bcolz file from which we will query.
    asset_starts_calendar : dict
        Dictionary containing the index of in our calendar corresponding to the
        start date of each asset
    query_start : intp
        Start index in our calendar of the dates for which we're querying.
    query_end : intp
        End index in our calendar of the dates for which we're querying.
    requested_assets : pandas.Index[int]
        The assets for which we want to load data.

    Returns
    -------
    first_rows, last_rows, offsets : 3-tuple of ndarrays
    """
    ...


def _read_bcolz_data(table,
                     shape,
                     columns,
                     first_rows,
                     last_rows,
                     offsets,
                     read_all):
    """
    Load raw bcolz data for the given columns and indices.

    Parameters
    ----------
    table : bcolz.ctable
        The table from which to read.
    shape : tuple (length 2)
        The shape of the expected output arrays.
    columns : list[str]
        List of column names to read.

    first_rows : ndarray[intp]
    last_rows : ndarray[intp]
    offsets : ndarray[intp
        Arrays in the format returned by _compute_row_slices.
    read_all : bool
        Whether to read_all sid data at once, or to read a silce from the
        carray for each sid.

    Returns
    -------
    results : list of ndarray
        A 2D array of shape `shape` for each column in `columns`.
    """
    ...
