"""
Pipeline datasets for Brain datasets.

Classes
-------
BSI
    DataSetFamily representing Brain Sentiment Indicator (BSI) data.

BLMCF
    DataSetFamily representing Brain Language Metrics on Company
    Filings (BLMCF) data.

Notes
-----
Usage Guide:

* Brain Sentiment Indicator: https://qrok.it/dl/z/pipeline-brain-bsi
* Brain Language Metrics on Company Filings: https://qrok.it/dl/z/pipeline-brain-blmcf
"""
from .data.brain import (
    BSI,
    BLMCF,
)

__all__ = [
    "BSI",
    "BLMCF",
]