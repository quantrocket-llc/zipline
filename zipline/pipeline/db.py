"""
Pipeline datasets for data stored in QuantRocket databases (that is, any
database queryable with `quantrocket.get_prices`).

Classes
-------
Database
    A Pipeline DataSet representing a database queryable with
    `quantrocket.get_prices`.

Column
    A Pipeline column representing a single field of a database
    queryable with `quantrocket.get_prices`.
"""
from .data.db import Database, Column

__all__ = ['Database', 'Column']