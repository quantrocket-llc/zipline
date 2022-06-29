ADJUSTMENT_KIND_NAMES = ...

_float_adjustment_types = ...
_datetime_adjustment_types = ...
_object_adjustment_types = ...
_int_adjustment_types = ...
_boolean_adjustment_types = ...


def _is_float(value): ...

def _is_datetime(value): ...

def _is_int(value): ...

def _is_obj(value): ...

def _is_bool(value): ...

def choose_adjustment_type(adjustment_kind, value):
    """
    Make an adjustment object of the type appropriate for the given kind and
    value.

    Parameters
    ----------
    adjustment_kind : {ADD, MULTIPLY, OVERWRITE}
        The kind of adjustment to construct.
    value : object
        The value parameter to the adjustment.  Only floating-point values and
        datetime-like values are currently supported
    """
    ...

def make_adjustment_from_indices(first_row,
                                 last_row,
                                 first_column,
                                 last_column,
                                 adjustment_kind,
                                 value):
    """
    Make an Adjustment object from row/column indices into a baseline array.
    """
    ...

def _choose_adjustment_type(adjustment_kind, value): ...

def make_adjustment_from_indices_fused(first_row,
                                       last_row,
                                       first_column,
                                       last_column,
                                       adjustment_kind,
                                       value):
    """
    Make an Adjustment object from row/column indices into a baseline array.
    """
    ...

def make_adjustment_from_labels(dates_index,
                                assets_index,
                                start_date,
                                end_date,
                                asset_id,
                                adjustment_kind,
                                value):
    """
    Make an Adjustment object from date/asset labels into a labelled baseline
    array.
    """
    ...

def get_adjustment_locs(dates_index,
                        assets_index,
                        start_date,
                        end_date,
                        asset_id):
    """
    Compute indices suitable for passing to an Adjustment constructor.

    If the specified dates aren't in dates_index, we return the index of the
    first date **BEFORE** the supplied date.

    Example:

    >>> from pandas import date_range, Int64Index, Timestamp
    >>> dates = date_range('2014-01-01', '2014-01-07')
    >>> assets = Int64Index(range(10))
    >>> get_adjustment_locs(
    ...     dates,
    ...     assets,
    ...     Timestamp('2014-01-03'),
    ...     Timestamp('2014-01-05'),
    ...     3,
    ... )
    (2, 4, 3)
    """
    ...

def _from_assets_and_dates(cls,
                           dates_index,
                           assets_index,
                           start_date,
                           end_date,
                           asset_id,
                           value):
    """
    Helper for constructing an Adjustment instance from coordinates in
    assets/dates indices.

    Example
    -------

    >>> from pandas import date_range, Int64Index, Timestamp
    >>> dates = date_range('2014-01-01', '2014-01-07')
    >>> assets = Int64Index(range(10))
    >>> Float64Multiply.from_assets_and_dates(
    ...     dates,
    ...     assets,
    ...     Timestamp('2014-01-03'),
    ...     Timestamp('2014-01-05'),
    ...     3,
    ...     0.5,
    ... )
    Float64Multiply(first_row=2, last_row=4, first_col=3, last_col=3, value=0.500000)
    """
    ...

class Adjustment:
    """
    Base class for Adjustments.

    Subclasses should inherit and provide a `value` attribute and a `mutate`
    method.
    """
    ...


class Float64Adjustment(Adjustment):
    """
    Base class for adjustments that operate on Float64 data.
    """
    ...

class Float64Multiply(Float64Adjustment):
    """
    An adjustment that multiplies by a float.

    Example
    -------

    >>> import numpy as np
    >>> arr = np.arange(9, dtype=float).reshape(3, 3)
    >>> arr
    array([[ 0.,  1.,  2.],
           [ 3.,  4.,  5.],
           [ 6.,  7.,  8.]])

    >>> adj = Float64Multiply(
    ...     first_row=1,
    ...     last_row=2,
    ...     first_col=1,
    ...     last_col=2,
    ...     value=4.0,
    ... )
    >>> adj.mutate(arr)
    >>> arr
    array([[  0.,   1.,   2.],
           [  3.,  16.,  20.],
           [  6.,  28.,  32.]])
    """

    ...

class Float64Overwrite(Float64Adjustment):
    """
    An adjustment that overwrites with a float.

    Example
    -------

    >>> import numpy as np
    >>> arr = np.arange(9, dtype=float).reshape(3, 3)
    >>> arr
    array([[ 0.,  1.,  2.],
           [ 3.,  4.,  5.],
           [ 6.,  7.,  8.]])

    >>> adj = Float64Overwrite(
    ...     first_row=1,
    ...     last_row=2,
    ...     first_col=1,
    ...     last_col=2,
    ...     value=0.0,
    ... )
    >>> adj.mutate(arr)
    >>> arr
    array([[ 0.,  1.,  2.],
           [ 3.,  0.,  0.],
           [ 6.,  0.,  0.]])
    """
    ...


class ArrayAdjustment(Adjustment):
    """
    Base class for ArrayAdjustments.

    Subclasses should inherit and provide a `values` attribute and a `mutate`
    method.
    """
    ...

class Float641DArrayOverwrite(ArrayAdjustment):
    """
    An adjustment that overwrites subarrays with a value for each subarray.

    Example
    -------

    >>> import numpy as np
    >>> arr = np.arange(25, dtype=float).reshape(5, 5)
    >>> arr
    array([[  0.,   1.,   2.,   3.,   4.],
           [  5.,   6.,   7.,   8.,   9.],
           [ 10.,  11.,  12.,  13.,  14.],
           [ 15.,  16.,  17.,  18.,  19.],
           [ 20.,  21.,  22.,  23.,  24.]])
    >>> adj = Float641DArrayOverwrite(
    ...     row_start=0,
    ...     row_end=3,
    ...     column_start=0,
    ...     column_end=0,
    ...     values=np.array([1, 2, 3, 4]),
    )
    >>> adj.mutate(arr)
    >>> arr
    array([[  1.,   1.,   2.,   3.,   4.],
           [  2.,   6.,   7.,   8.,   9.],
           [ 3.,  11.,  12.,  13.,  14.],
           [ 4.,  16.,  17.,  18.,  19.],
           [ 20.,  21.,  22.,  23.,  24.]])
    """
    ...


class Datetime641DArrayOverwrite(ArrayAdjustment):
    """
    An adjustment that overwrites subarrays with a value for each subarray.

    Example
    -------

    >>> import numpy as np; import pandas as pd
    >>> dts = pd.date_range('2014', freq='D', periods=9, tz='UTC')
    >>> arr = dts.values.reshape(3, 3)
    >>> arr == np.datetime64(0, 'ns')
    array([[False, False, False],
       [False, False, False],
       [False, False, False]], dtype=bool)
    >>> adj = Datetime641DArrayOverwrite(
    ...           first_row=1,
    ...           last_row=2,
    ...           first_col=1,
    ...           last_col=2,
    ...           values=np.array([
    ...               np.datetime64(0, 'ns'),
    ...               np.datetime64(1, 'ns')
    ...           ])
    ...       )
    >>> adj.mutate(arr.view(np.int64))
    >>> arr == np.datetime64(0, 'ns')
    array([[False, False, False],
       [False,  True,  True],
       [False, False, False]], dtype=bool)
    >>> arr == np.datetime64(1, 'ns')
    array([[False, False, False],
       [False, False, False],
       [False,  True,  True]], dtype=bool)
    """
    ...

class Object1DArrayOverwrite(ArrayAdjustment): ...


class Boolean1DArrayOverwrite(ArrayAdjustment): ...

class Float64Add(Float64Adjustment):
    """
    An adjustment that adds a float.

    Example
    -------

    >>> import numpy as np
    >>> arr = np.arange(9, dtype=float).reshape(3, 3)
    >>> arr
    array([[ 0.,  1.,  2.],
           [ 3.,  4.,  5.],
           [ 6.,  7.,  8.]])

    >>> adj = Float64Add(
    ...     first_row=1,
    ...     last_row=2,
    ...     first_col=1,
    ...     last_col=2,
    ...     value=1.0,
    ... )
    >>> adj.mutate(arr)
    >>> arr
    array([[ 0.,  1.,  2.],
           [ 3.,  5.,  6.],
           [ 6.,  8.,  9.]])
    """
    ...

class _Int64Adjustment(Adjustment):
    """
    Base class for adjustments that operate on integral data.

    This is private because we never actually operate on integers as data, but
    we use integer arrays to represent datetime and timedelta data.
    """
    ...

class Int64Overwrite(_Int64Adjustment):
    """
    An adjustment that overwrites with an int.

    Example
    -------

    >>> import numpy as np
    >>> arr = np.arange(9, dtype=int).reshape(3, 3)
    >>> arr
    array([[ 0,  1,  2],
           [ 3,  4,  5],
           [ 6,  7,  8]])

    >>> adj = Int64Overwrite(
    ...     first_row=1,
    ...     last_row=2,
    ...     first_col=1,
    ...     last_col=2,
    ...     value=0,
    ... )
    >>> adj.mutate(arr)
    >>> arr
    array([[ 0,  1,  2],
           [ 3,  0,  0],
           [ 6,  0,  0]])
    """

    ...

def datetime_to_int(datetimelike):
    """
    Coerce a datetime-like object to the int format used by AdjustedArrays of
    Datetime64 type.
    """
    ...


class Datetime64Adjustment(_Int64Adjustment):
    """
    Base class for adjustments that operate on Datetime64 data.

    Notes
    -----
    Numpy stores datetime64 values in arrays of type int64.  There's no
    straightforward way to work with statically-typed datetime64 data, so
    instead we work with int64 values everywhere, and we do validation/coercion
    at API boundaries.
    """
    ...

class Datetime64Overwrite(Datetime64Adjustment):
    """
    An adjustment that overwrites with a datetime.

    This operates on int64 data which should be interpreted as nanoseconds
    since the epoch.

    Example
    -------

    >>> import numpy as np; import pandas as pd
    >>> dts = pd.date_range('2014', freq='D', periods=9, tz='UTC')
    >>> arr = dts.values.reshape(3, 3)
    >>> arr == np.datetime64(0, 'ns')
    array([[False, False, False],
           [False, False, False],
           [False, False, False]], dtype=bool)
    >>> adj = Datetime64Overwrite(
    ...     first_row=1,
    ...     last_row=2,
    ...     first_col=1,
    ...     last_col=2,
    ...     value=np.datetime64(0, 'ns'),
    ... )
    >>> adj.mutate(arr.view(np.int64))
    >>> arr == np.datetime64(0, 'ns')
    array([[False, False, False],
           [False,  True,  True],
           [False,  True,  True]], dtype=bool)
    """
    ...


class _ObjectAdjustment(Adjustment):
    """
    Base class for adjustments that operate on arbitrary objects.

    We use only this for categorical data, where our data buffer is an array of
    indices into an array of unique Python string objects.
    """
    ...


class ObjectOverwrite(_ObjectAdjustment):

    ...


class BooleanAdjustment(Adjustment):
    """
    Base class for adjustments that operate on boolean data.

    Notes
    -----
    Numpy stores boolean values in arrays of type uint8.  There's no
    straightforward way to work with statically-typed boolean data, so
    instead we work with uint8 values everywhere, and we do validation/coercion
    at API boundaries.
    """
    ...

class BooleanOverwrite(BooleanAdjustment):
    """
    An adjustment that overwrites with a boolean.

    This operates on uint8 data.
    """
    ...
