"""
Pipeline terms that compute categorical output.

Classes
-------
Latest
    A classifier producing the latest value of an input term on each day.

Classifier
    Base class for Pipeline expressions computing a categorical output.

CustomClassifier
    Base class for user-defined Classifiers.
"""
from .classifier import (
    Classifier,
    CustomClassifier,
    Quantiles,
    Everything,
    Latest,
)

__all__ = [
    'Classifier',
    'CustomClassifier',
    'Latest',
]
