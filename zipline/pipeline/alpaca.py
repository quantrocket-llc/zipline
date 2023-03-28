
"""
Pipeline dataset for Alpaca easy-to-borrow data.

Classes
-------
ETB
    Dataset representing whether securities are easy-to-borrow through Alpaca.

Notes
-----
Usage Guide:

* Alpaca ETB: https://qrok.it/dl/z/pipeline-alpaca-etb
"""
from .data.alpaca import ETB

__all__ = ['ETB']
