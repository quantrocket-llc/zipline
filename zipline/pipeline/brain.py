"""
Pipeline datasets for Brain datasets.

Classes
-------
BSI
    DataSetFamily representing Brain Sentiment Indicator (BSI) data.

BLMCF
    DataSetFamily representing Brain Language Metrics on Company
    Filings (BLMCF) data.

BLMECT
    DataSet representing Brain Language Metrics on Earnings Call
    Transcripts (BLMECT) data.

Notes
-----
Usage Guide:

* Brain Sentiment Indicator: https://qrok.it/dl/z/pipeline-brain-bsi
* Brain Language Metrics on Company Filings: https://qrok.it/dl/z/pipeline-brain-blmcf
* Brain Language Metrics on Earnings Call Transcripts: https://qrok.it/dl/z/pipeline-brain-blmect
"""
from .data.brain import (
    BSI,
    BLMCF,
    BLMECT,
)

__all__ = [
    "BSI",
    "BLMCF",
    "BLMECT"
]