"""
Pipeline terms that compute boolean output.

Classes
-------
SingleAsset
    A Filter that computes to True only for a given asset.

StaticAssets
    A Filter that computes True for a specific set of predetermined assets.

StaticSids
    A Filter that computes True for a specific set of predetermined sids.

StaticUniverse
    A Filter that computes True for assets that are members of a specific
    universe defined in the securities master database.

Latest
    Filter producing the most recently-known value of the input term on each day.

Filter
    Base class for Pipeline expressions computing a boolean output.

CustomFilter
    Base class for user-defined Filters.

Notes
-----
Usage Guide:

* Pipeline computations: https://qrok.it/dl/z/pipeline-computations
"""
from .filter import (
    AllPresent,
    ArrayPredicate,
    CustomFilter,
    Filter,
    Latest,
    MaximumFilter,
    NotNullFilter,
    NullFilter,
    NumExprFilter,
    PercentileFilter,
    SingleAsset,
    StaticAssets,
    StaticSids,
    StaticUniverse
)
from .smoothing import All, Any, AtLeastN

__all__ = [
    'CustomFilter',
    'Filter',
    'Latest',
    'SingleAsset',
    'StaticAssets',
    'StaticSids',
    "StaticUniverse",
]
