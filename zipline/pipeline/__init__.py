"""
An API for filtering and performing computations on large universes
of securities.

Modules
-------
factors
    Pipeline terms that compute numerical output.

filters
    Pipeline terms that compute boolean output.

classifiers
    Pipeline terms that compute categorical output.

periodic
    Pipeline factors and filters for working with periodic data, defined as data
    that doesn't change daily but changes at less frequent intervals, such as quarterly
    or annual fundamentals. Specifically, these factors and filters are compatible
    with any Pipeline DataSet that has a `period_offset` coordinate.


sharadar
    Pipeline datasets for Sharadar US Fundamentals, Institutional Holdings,
    and S&P 500 constituents.

master
    Pipeline datasets for securities master data.

ibkr
    Pipeline datasets for Interactive Brokers shortable shares and borrow
    fees.

db
    Pipeline datasets for data stored in QuantRocket databases queryable with
    `quantrocket.get_prices`.

alpaca
    Pipeline dataset for Alpaca easy-to-borrow data.

Classes
-------
Pipeline
    A Pipeline object representing a collection of named expressions to be
    compiled and executed.

EquityPricing
    A Pipeline `DataSet` containing daily trading prices and volumes for the
    assets in a bundle.

Constant
    Pipeline term that returns a constant value.
"""
from __future__ import print_function

from .classifiers import Classifier, CustomClassifier
from .domain import Domain
from .factors import Factor, CustomFactor
from .filters import Filter, CustomFilter
from .constant import Constant
from .term import Term, LoadableTerm, ComputableTerm
from .graph import ExecutionPlan, TermGraph
# NOTE: this needs to come after the import of `graph`, or else we get circular
# dependencies.
from .engine import SimplePipelineEngine
from .pipeline import Pipeline
from . import factors, filters, classifiers
from . import alpaca
from . import db
from . import ibkr
from . import master
from . import periodic
from . import sharadar
from .data import EquityPricing

__all__ = (
    'Constant',
    'EquityPricing',
    'Pipeline',
    'classifiers',
    'factors',
    'filters',
    'alpaca',
    'db',
    'ibkr',
    'master',
    'periodic',
    'sharadar',
)
