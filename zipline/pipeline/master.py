"""
Pipeline datasets for securities master data.

Classes
-------
SecuritiesMaster
    Dataset representing the securities master file.

Notes
-----
Usage Guide:

* Securities master: https://qrok.it/dl/z/pipeline-securities-master
"""
from .data.master import SecuritiesMaster

__all__ = [
    "SecuritiesMaster"
]