def rankdata_1d_descending(data, method, nan_policy='omit'):
    """
    1D descending version of scipy.stats.rankdata.
    """
    ...

def masked_rankdata_2d(data,
                       mask,
                       missing_value,
                       method,
                       ascending):
    """
    Compute masked rankdata on data on float64, int64, or datetime64 data.
    """
    ...

def rankdata_2d_ordinal(array):
    """
    Equivalent to:

    numpy.apply_over_axis(scipy.stats.rankdata, 1, array, method='ordinal', nan_policy='omit')
    """
    ...

def grouped_masked_is_maximal(data,
                              groupby,
                              mask):
    """Build a mask of the top value for each row in ``data``, grouped by
    ``groupby`` and masked by ``mask``.

    Parameters
    ----------
    data : np.array[int64_t]
        Data on which we should find maximal values for each row.
    groupby : np.array[int64_t]
        Grouping labels for rows of ``data``. We choose one entry in each
        row for each unique grouping key in that row.
    mask : np.array[uint8_t]
        Boolean mask of locations to consider as possible maximal values.
        Locations with a 0 in ``mask`` are ignored.

    Returns
    -------
    maximal_locations : np.array[bool]
        Mask containing True for the maximal non-masked value in each row/group.
    """
    ...
