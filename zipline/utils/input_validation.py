# Copyright 2015 Quantopian, Inc.
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
from datetime import tzinfo
from functools import partial
from operator import attrgetter

from numpy import dtype
import pandas as pd
from pytz import timezone
from six import iteritems, string_types

from zipline.utils.compat import wraps
from zipline.utils.preprocess import preprocess


_qualified_name = attrgetter('__qualname__')


def verify_indices_all_unique(obj):
    """
    Check that all axes of a pandas object are unique.

    Parameters
    ----------
    obj : pd.Series / pd.DataFrame
        The object to validate.

    Returns
    -------
    obj : pd.Series / pd.DataFrame
        The validated object, unchanged.

    Raises
    ------
    ValueError
        If any axis has duplicate entries.
    """
    axis_names = [
        ('index',),                            # Series
        ('index', 'columns'),                  # DataFrame
    ][obj.ndim - 1]  # ndim = 1 should go to entry 0,

    for axis_name, index in zip(axis_names, obj.axes):
        if index.is_unique:
            continue

        raise ValueError(
            "Duplicate entries in {type}.{axis}: {dupes}.".format(
                type=type(obj).__name__,
                axis=axis_name,
                dupes=sorted(index[index.duplicated()]),
            )
        )
    return obj


def optionally(preprocessor):
    """Modify a preprocessor to explicitly allow `None`.

    Parameters
    ----------
    preprocessor : callable[callable, str, any -> any]
        A preprocessor to delegate to when `arg is not None`.

    Returns
    -------
    optional_preprocessor : callable[callable, str, any -> any]
        A preprocessor that delegates to `preprocessor` when `arg is not None`.

    Examples
    --------
    >>> def preprocessor(func, argname, arg):
    ...     if not isinstance(arg, int):
    ...         raise TypeError('arg must be int')
    ...     return arg
    ...
    >>> @preprocess(a=optionally(preprocessor))
    ... def f(a):
    ...     return a
    ...
    >>> f(1)  # call with int
    1
    >>> # START: delete in future
    >>> import pytest
    >>> pytest.xfail("This test fails in doctest as of 2023-09-29 due to a "
    ...              "library exception in formatting the traceback. Try to "
    ...              "remove this xfail in a future version.")
    >>> # END: delete in future
    >>> f('a')  # call with not int
    Traceback (most recent call last):
       ...
    TypeError: arg must be int
    >>> f(None) is None  # call with explicit None
    True
    """
    @wraps(preprocessor)
    def wrapper(func, argname, arg):
        return arg if arg is None else preprocessor(func, argname, arg)

    return wrapper


def ensure_upper_case(func, argname, arg):
    if isinstance(arg, string_types):
        return arg.upper()
    else:
        raise TypeError(
            "{0}() expected argument '{1}' to"
            " be a string, but got {2} instead.".format(
                func.__name__,
                argname,
                arg,
            ),
        )


def ensure_dtype(func, argname, arg):
    """
    Argument preprocessor that converts the input into a numpy dtype.

    Examples
    --------
    >>> import numpy as np
    >>> from zipline.utils.preprocess import preprocess
    >>> @preprocess(dtype=ensure_dtype)
    ... def foo(dtype):
    ...     return dtype
    ...
    >>> foo(float)
    dtype('float64')
    """
    try:
        return dtype(arg)
    except TypeError:
        raise TypeError(
            "{func}() couldn't convert argument "
            "{argname}={arg!r} to a numpy dtype.".format(
                func=_qualified_name(func),
                argname=argname,
                arg=arg,
            ),
        )


def ensure_timezone(func, argname, arg):
    """Argument preprocessor that converts the input into a tzinfo object.

    Examples
    --------
    >>> from zipline.utils.preprocess import preprocess
    >>> @preprocess(tz=ensure_timezone)
    ... def foo(tz):
    ...     return tz
    >>> foo('utc')
    <UTC>
    """
    if isinstance(arg, tzinfo):
        return arg
    if isinstance(arg, string_types):
        return timezone(arg)

    raise TypeError(
        "{func}() couldn't convert argument "
        "{argname}={arg!r} to a timezone.".format(
            func=_qualified_name(func),
            argname=argname,
            arg=arg,
        ),
    )


def ensure_timestamp(func, argname, arg):
    """Argument preprocessor that converts the input into a pandas Timestamp
    object.

    Examples
    --------
    >>> from zipline.utils.preprocess import preprocess
    >>> @preprocess(ts=ensure_timestamp)
    ... def foo(ts):
    ...     return ts
    >>> foo('2014-01-01')
    Timestamp('2014-01-01 00:00:00')
    """
    try:
        return pd.Timestamp(arg)
    except ValueError as e:
        raise TypeError(
            "{func}() couldn't convert argument "
            "{argname}={arg!r} to a pandas Timestamp.\n"
            "Original error was: {t}: {e}".format(
                func=_qualified_name(func),
                argname=argname,
                arg=arg,
                t=_qualified_name(type(e)),
                e=e,
            ),
        )


def coerce(from_, to, **to_kwargs):
    """
    A preprocessing decorator that coerces inputs of a given type by passing
    them to a callable.

    Parameters
    ----------
    from : type or tuple or types
        Inputs types on which to call ``to``.
    to : function
        Coercion function to call on inputs.
    **to_kwargs
        Additional keywords to forward to every call to ``to``.

    Examples
    --------
    >>> @preprocess(x=coerce(float, int), y=coerce(float, int))
    ... def floordiff(x, y):
    ...     return x - y
    ...
    >>> floordiff(3.2, 2.5)
    1

    >>> @preprocess(x=coerce(str, int, base=2), y=coerce(str, int, base=2))
    ... def add_binary_strings(x, y):
    ...     return bin(x + y)[2:]
    ...
    >>> add_binary_strings('101', '001')
    '110'
    """
    def preprocessor(func, argname, arg):
        if isinstance(arg, from_):
            return to(arg, **to_kwargs)
        return arg
    return preprocessor


def coerce_types(**kwargs):
    """
    Preprocessing decorator that applies type coercions.

    Parameters
    ----------
    **kwargs : dict[str -> (type, callable)]
         Keyword arguments mapping function parameter names to pairs of
         (from_type, to_type).

    Examples
    --------
    >>> @coerce_types(x=(float, int), y=(int, str))
    ... def func(x, y):
    ...     return (x, y)
    ...
    >>> func(1.0, 3)
    (1, '3')
    """
    def _coerce(types):
        return coerce(*types)

    return preprocess(**valmap(_coerce, kwargs))


class error_keywords(object):

    def __init__(self, *args, **kwargs):
        self.messages = kwargs

    def __call__(self, func):
        @wraps(func)
        def assert_keywords_and_call(*args, **kwargs):
            for field, message in iteritems(self.messages):
                if field in kwargs:
                    raise TypeError(message)
            return func(*args, **kwargs)
        return assert_keywords_and_call


coerce_string = partial(coerce, string_types)


def validate_keys(dict_, expected, funcname):
    """Validate that a dictionary has an expected set of keys.
    """
    expected = set(expected)
    received = set(dict_)

    missing = expected - received
    if missing:
        raise ValueError(
            "Missing keys in {}:\n"
            "Expected Keys: {}\n"
            "Received Keys: {}".format(
                funcname,
                sorted(expected),
                sorted(received),
            )
        )

    unexpected = received - expected
    if unexpected:
        raise ValueError(
            "Unexpected keys in {}:\n"
            "Expected Keys: {}\n"
            "Received Keys: {}".format(
                funcname,
                sorted(expected),
                sorted(received),
            )
        )
