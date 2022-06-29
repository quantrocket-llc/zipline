def log2(d): ...

def smallest_uint_that_can_hold(maxval):
    """Choose the smallest numpy unsigned int dtype that can hold ``maxval``.
    """
    ...

def unsigned_integral(): ...

class _NoneFirstSortKey:
    """Box to sort ``None`` to the front of the categories list.
    """
    ...

def factorize_strings_known_impl(values,
                                 nvalues,
                                 categories,
                                 missing_value,
                                 sort,
                                 codes):
    ...

def factorize_strings_known_categories(values,
                                       categories,
                                       missing_value,
                                       sort):
    """
    Factorize an array whose categories are already known.

    Any entries not in the specified categories will be given the code for
    `missing_value`.
    """
    ...

def factorize_strings_impl(values,
                           missing_value,
                           sort,
                           codes):
    ...

_int_sizes = ...


def factorize_strings(values,
                      missing_value,
                      sort):
    """
    Factorize an array of (possibly duplicated) labels into an array of indices
    into a unique array of labels.

    This is ~30% faster than pandas.factorize, at the cost of not having
    special treatment for NaN, which we don't care about because we only
    support arrays of strings.

    (Though it's faster even if you throw in the nan checks that pandas does,
    because we're using dict and list instead of PyObjectHashTable and
    ObjectVector.  Python's builtin data structures are **really**
    well-optimized.)
    """
    ...
