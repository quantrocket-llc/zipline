import functools
import inspect
from operator import methodcaller
import sys

from contextlib import contextmanager
from html import escape as escape_html
from types import MappingProxyType as mappingproxy
from math import ceil

# Help Sphinx autoapi understand these definitions
mappingproxy = mappingproxy
contextmanager = contextmanager
escape_html = escape_html


def exc_clear():
    # exc_clear was removed in Python 3. The except statement automatically
    # clears the exception.
    pass

def consistent_round(val):
    if (val % 1) >= 0.5:
        return ceil(val)
    else:
        return round(val)

update_wrapper = functools.update_wrapper
wraps = functools.wraps

def values_as_list(dictionary):
    """Return the dictionary values as a list without forcing a copy
    in Python 2.
    """
    return list(dictionary.values())

def getargspec(f):
    full_argspec = inspect.getfullargspec(f)
    return inspect.ArgSpec(
        args=full_argspec.args,
        varargs=full_argspec.varargs,
        keywords=full_argspec.varkw,
        defaults=full_argspec.defaults,
    )


unicode = type(u'')

__all__ = [
    'consistent_round',
    'contextmanager',
    'escape_html',
    'exc_clear',
    'mappingproxy',
    'unicode',
    'update_wrapper',
    'values_as_list',
    'wraps',
]
