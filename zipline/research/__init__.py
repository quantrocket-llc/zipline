"""
Zipline research API.

The functions in this module are most often used in a Jupyter notebook, outside
of the context of a Zipline algorithm. For the Zipline algorithm API, see the
`zipline.api` module.

Functions
---------
run_pipeline
    Execute a pipeline.

get_forward_returns
    Get forward returns for the dates and assets in an input factor (typically
    the output of `run_pipeline`).

get_data
    Return a `zipline.api.BarData` object for a specified bundle and datetime.

sid
    Return a `zipline.assets.Asset` object for a specified sid.

continuous_future
    Return a `zipline.assets.ContinuousFuture` object for a specified root symbol.

Notes
-----
Usage Guide:

* Research API: https://qrok.it/dl/z/zipline-research
"""
from zipline.research.pipeline import run_pipeline, get_forward_returns
from zipline.research.bardata import get_data
from zipline.research.sid import sid
from zipline.research.continuous_future import continuous_future

__all__ = [
    'run_pipeline',
    'get_forward_returns',
    'get_data',
    'sid',
    'continuous_future',
]