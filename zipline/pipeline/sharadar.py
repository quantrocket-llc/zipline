"""
Pipeline datasets and factors for Sharadar fundamental data.

Classes
-------
Fundamentals
    DataSetFamily representing Sharadar fundamentals.

Institutions
    DataSetFamily representing Sharadar institutional ownership.

SP500
    Dataset representing membership in the S&P 500.

PiotroskiFScore
    Return a Factor that computes the Piotroski F-Score using Sharadar fundamentals.
    The Piotroski F-Score evaluates a firm's financial health.

AltmanZScore
    Return a Factor that computes the Altman Z-Score using Sharadar fundamentals.
    The Altman Z-Score measures the likelihood of future bankruptcy.

InterestCoverageRatio
    Return a Factor that computes the Interest Coverage Ratio (ICR) using Sharadar
    fundamentals. The Interest Coverage Ratio measures a company's ability to service
    its debt.

Notes
-----
Usage Guide:

* Sharadar fundamentals: https://qrok.it/dl/z/pipeline-sharadar-fundamentals
* Sharadar institutions: https://qrok.it/dl/z/pipeline-sharadar-institutions
* Sharadar S&P 500: https://qrok.it/dl/z/pipeline-sharadar-sp500
"""
from .factors.sharadar import(
    PiotroskiFScore,
    AltmanZScore,
    InterestCoverageRatio
)
from .data.sharadar import (
    Fundamentals,
    Institutions,
    SP500
)

__all__ = [
    'PiotroskiFScore',
    'AltmanZScore',
    'InterestCoverageRatio',
    'Fundamentals',
    'Institutions',
    'SP500',
]