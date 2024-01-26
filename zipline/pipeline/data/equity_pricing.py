"""
Dataset representing OHLCV data.
"""
from typing import TYPE_CHECKING
from zipline.utils.numpy_utils import float64_dtype, categorical_dtype

from ..domain import US_EQUITIES
from .dataset import Column, DataSet

if TYPE_CHECKING:
    from .dataset import BoundFloatColumn, BoundObjectColumn


class EquityPricing(DataSet):
    """
    :class:`~zipline.pipeline.data.DataSet` containing daily trading prices and
    volumes.

    Attributes
    ----------
    open : float64
        The opening price of the asset for the day.

    high : float64
        The highest trade price of the asset for the day.

    low : float64
        The lowest trade price of the asset for the day.

    close : float64
        The closing price of the asset for the day.

    volume : float64
        The volume of shares traded for the asset for the day.

    Notes
    -----
    Usage Guide:

    * Pipeline data concepts: https://qrok.it/dl/z/pipeline-data-concepts

    Examples
    --------
    Get a Pipeline factor that returns the closing price:

    >>> from zipline.pipeline import EquityPricing
    >>> close_price = EquityPricing.close.latest
    """
    open: 'BoundFloatColumn' = Column(float64_dtype, currency_aware=True)
    high: 'BoundFloatColumn' = Column(float64_dtype, currency_aware=True)
    low: 'BoundFloatColumn' = Column(float64_dtype, currency_aware=True)
    close: 'BoundFloatColumn' = Column(float64_dtype, currency_aware=True)
    volume: 'BoundFloatColumn' = Column(float64_dtype)
    currency: 'BoundObjectColumn' = Column(categorical_dtype)


# Backwards compat alias.
USEquityPricing = EquityPricing.specialize(US_EQUITIES)
