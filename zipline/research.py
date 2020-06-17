#
# Copyright 2020 QuantRocket LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import pandas as pd
from zipline.data import bundles
import zipline.pipeline.domain as domain
from zipline.utils.extensions import load_extensions
from zipline.pipeline.loaders import EquityPricingLoader
from zipline.pipeline.data import USEquityPricing
from zipline.pipeline.loaders.router import QuantRocketPipelineLoaderRouter
from zipline.pipeline.engine import SimplePipelineEngine
from zipline.algorithm import _DEFAULT_DOMAINS
from quantrocket.zipline import get_default_bundle
from quantrocket_trading_calendars import get_calendar

def run_pipeline(pipeline, start_date, end_date, bundle=None, chunksize=525):
    """
    Compute values for pipeline from start_date to end_date, using the specified
    bundle or the default bundle.

    Parameters
    ----------
    pipeline : Pipeline, required
        The pipeline to run.

    start_date : str (YYYY-MM-DD), required
        First date on which the pipeline should run. If start_date is not a trading
        day, the pipeline will start on the first trading day after start_date.

    end_date : str (YYYY-MM-DD), required
        Last date on which the pipeline should run. If end_date is not a trading
        day, the pipeline will end on the first trading day after end_date.

    bundle : str, optional
        the bundle code. If omitted, the default bundle will be used.

    chunksize : int, optional
        The number of days to execute at a time. Using smaller chunks will result
        in less memory usage, but may also take longer, particularly for pipelines
        that compute factors with long lookback windows. Default is 525.

    Returns
    -------
    result : pd.DataFrame
        A frame of computed results. The result columns correspond to the entries
        of pipeline.columns, which should be a dictionary mapping strings to instances
        of zipline.pipeline.term.Term. For each date between start_date and end_date,
        result will contain a row for each asset that passed pipeline.screen. A screen
        of None indicates that a row should be returned for each asset that existed each
        day.
    """

    if not bundle:
        bundle = get_default_bundle()
        if not bundle:
            raise ValueError("you must specify a bundle or set a default bundle")
        bundle = bundle["default_bundle"]

    load_extensions(code=bundle)

    bundle_data = bundles.load(
        bundle,
        os.environ,
        pd.Timestamp.utcnow(),
    )

    calendar_name = bundles.bundles[bundle].calendar_name
    trading_calendar = get_calendar(calendar_name)

    start_date = pd.Timestamp(start_date, tz="UTC")
    end_date = pd.Timestamp(end_date, tz="UTC")

    if start_date < trading_calendar.first_session:
        raise ValueError(
            f"start_date cannot be earlier than {trading_calendar.first_session.date().isoformat()} for this calendar")

    # Roll-forward start_date to valid session
    for i in range(100):
        if trading_calendar.is_session(start_date):
            break
        start_date += pd.Timedelta(days=1)
    else:
        raise ValueError("start_date is not in calendar")

    # Roll-forward end_date to valid session
    for i in range(100):
        if trading_calendar.is_session(end_date):
            break
        end_date += pd.Timedelta(days=1)
    else:
        raise ValueError("end_date is not in calendar")

    if (
        end_date < start_date):
        raise ValueError("end_date cannot be earlier than start_date")

    default_pipeline_loader = EquityPricingLoader.without_fx(
        bundle_data.equity_daily_bar_reader,
        bundle_data.adjustment_reader,
    )

    pipeline_loader = QuantRocketPipelineLoaderRouter(
        asset_db_conn=bundle_data.asset_finder.engine,
        calendar=trading_calendar,
        default_loader=default_pipeline_loader,
        default_loader_columns=USEquityPricing.columns
    )

    calendar_domain = _DEFAULT_DOMAINS.get(calendar_name, domain.GENERIC)

    engine = SimplePipelineEngine(
        pipeline_loader,
        bundle.asset_finder,
        calendar_domain)

    return engine.run_chunked_pipeline(
        pipeline,
        start_date,
        end_date,
        chunksize)
