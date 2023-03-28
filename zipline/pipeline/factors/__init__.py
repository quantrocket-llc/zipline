"""
Pipeline terms that compute numerical output.

Classes
-------
AnnualizedVolatility
    Factor that calculates annualized volatility.

Aroon
    Factor that calculates Aroon technical indicator.

AverageDollarVolume
    Factor that calculates average daily dollar volume.

BollingerBands
    Factor that calculates Bollinger Bands

CustomFactor
    Base class for user-defined Factors.

DailyReturns
    Factors that calculates daily percent change in close price.

ExponentialWeightedMovingAverage
    Factor that calculates exponentially-weighted moving average.

ExponentialWeightedMovingStdDev
    Factor that calculates exponentially-weighted moving standard deviation.

Factor
    Base class for Pipeline expressions computing a numerical output.

FastStochasticOscillator
    Factor that calculates Fast Stochastic Oscillator Indicator.

IchimokuKinkoHyo
    Factor that calculates the various metrics for the Ichimoku Kinko Hyo
    (Ichimoku Cloud).

Latest
    Factor producing the most recently-known value of the input term on each
    day.

LinearWeightedMovingAverage
    Factor that calculates weighted average value of an arbitrary column.

MaxDrawdown
    Factor that calculates maximum drawdown.

MovingAverageConvergenceDivergenceSignal
    Factor that calculates Moving Average Convergence/Divergence (MACD)
    Signal line.

PercentChange
     Factor that calculates the percent change over a given window_length.

RateOfChangePercentage
    Factor that calculates Rate of change Percentage (ROC), a technical
    indicator that measures the percentage change in price from one period
    to the next.

Returns
    Factor that calculates the percent change in close price over a given window_length.

RollingLinearRegressionOfReturns
    Factor that performs an ordinary least-squares regression predicting the
    returns of all other assets on the given asset.

RollingPearsonOfReturns
    Factor that calculates the Pearson product-moment correlation coefficient of
    the returns of the given asset with the returns of all other assets.

RollingSpearmanOfReturns
    Factor that calculates the Spearman rank correlation coefficient of the returns
    of the given asset with the returns of all other assets.

RSI
    Factor that calculates Relative Strength Index.

SimpleBeta
    Factor producing the slope of a regression line between each asset's daily
    returns to the daily returns of a single "target" asset.

SimpleMovingAverage
    Factor that calculates average value of an arbitrary column.

TrueRange
    Factor that calculates True Range.

VWAP
    Factor that calculates volume-weighted average price.

Notes
-----
Usage Guide:

* Pipeline computations: https://qrok.it/dl/z/pipeline-computations
"""
from .factor import (
    CustomFactor,
    Factor,
    Latest,
    RecarrayField,
)
from .basic import (
    AnnualizedVolatility,
    AverageDollarVolume,
    DailyReturns,
    EWMA,
    ExponentialWeightedMovingAverage,
    ExponentialWeightedMovingStdDev,
    EWMSTD,
    LinearWeightedMovingAverage,
    MaxDrawdown,
    PeerCount,
    PercentChange,
    Returns,
    SimpleMovingAverage,
    VWAP,
    WeightedAverageValue,
)
from .events import (
    BusinessDaysSincePreviousEvent,
    BusinessDaysUntilNextEvent,
)
from .statistical import (
    RollingLinearRegressionOfReturns,
    RollingPearsonOfReturns,
    RollingSpearmanOfReturns,
    SimpleBeta,
)
from .technical import (
    Aroon,
    BollingerBands,
    FastStochasticOscillator,
    IchimokuKinkoHyo,
    MACDSignal,
    MovingAverageConvergenceDivergenceSignal,
    RateOfChangePercentage,
    RSI,
    TrueRange,
)

__all__ = [
    'AnnualizedVolatility',
    'Aroon',
    'AverageDollarVolume',
    'BollingerBands',
    'CustomFactor',
    'DailyReturns',
    'ExponentialWeightedMovingAverage',
    'ExponentialWeightedMovingStdDev',
    'Factor',
    'FastStochasticOscillator',
    'IchimokuKinkoHyo',
    'Latest',
    'LinearWeightedMovingAverage',
    'MACDSignal',
    'MaxDrawdown',
    'MovingAverageConvergenceDivergenceSignal',
    'PercentChange',
    'RateOfChangePercentage',
    'Returns',
    'RollingLinearRegressionOfReturns',
    'RollingPearsonOfReturns',
    'RollingSpearmanOfReturns',
    'RSI',
    'SimpleBeta',
    'SimpleMovingAverage',
    'TrueRange',
    'VWAP',
]
