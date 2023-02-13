"""
Dataset representing OHLCV data.
"""
from zipline.utils.numpy_utils import float64_dtype, categorical_dtype

from ..domain import US_EQUITIES
from .dataset import Column, DataSet, BoundFloatColumn, BoundObjectColumn


class EquityPricing(DataSet):
    """
    :class:`~zipline.pipeline.data.DataSet` containing daily trading prices and
    volumes.
    """
    open: BoundFloatColumn = Column(float64_dtype, currency_aware=True)
    high: BoundFloatColumn = Column(float64_dtype, currency_aware=True)
    low: BoundFloatColumn = Column(float64_dtype, currency_aware=True)
    close: BoundFloatColumn = Column(float64_dtype, currency_aware=True)
    volume: BoundFloatColumn = Column(float64_dtype)
    currency: BoundObjectColumn = Column(categorical_dtype)


# Backwards compat alias.
USEquityPricing = EquityPricing.specialize(US_EQUITIES)
