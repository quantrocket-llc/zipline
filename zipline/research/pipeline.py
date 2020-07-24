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
from zipline.pipeline import Pipeline
from zipline.utils.extensions import load_extensions
from zipline.pipeline.loaders import EquityPricingLoader
from zipline.pipeline.data import EquityPricing
from zipline.pipeline.factors import Returns
from zipline.pipeline.loaders.router import QuantRocketPipelineLoaderRouter
from zipline.pipeline.engine import SimplePipelineEngine
from zipline.research.exceptions import ValidationError
from quantrocket.zipline import get_default_bundle
from quantrocket_trading_calendars import get_calendar


def run_pipeline(pipeline, start_date, end_date=None, bundle=None):
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

    end_date : str (YYYY-MM-DD), optional
        Last date on which the pipeline should run. If end_date is not a trading
        day, the pipeline will end on the first trading day after end_date.
        Defaults to today.

    bundle : str, optional
        the bundle code. If omitted, the default bundle will be used (and must be set).

    Returns
    -------
    result : pd.DataFrame
        A frame of computed results. The result columns correspond to the entries
        of pipeline.columns, which should be a dictionary mapping strings to instances
        of zipline.pipeline.term.Term. For each date between start_date and end_date,
        result will contain a row for each asset that passed pipeline.screen. A screen
        of None indicates that a row should be returned for each asset that existed each
        day.

    Examples
    --------
    Get a pipeline of 1-year returns:

    >>> from zipline.pipeline.factors import Returns
    >>> pipeline = Pipeline(
            columns={
                '1Y': Returns(window_length=252),
            })
    >>> factor = run_pipeline(pipeline, '2018-01-01', '2019-02-01', bundle="usstock-1min")
    """

    if not bundle:
        bundle = get_default_bundle()
        if not bundle:
            raise ValidationError("you must specify a bundle or set a default bundle")
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

    if end_date:
        end_date = pd.Timestamp(end_date, tz="UTC")
    else:
        end_date = pd.Timestamp.now(tz="UTC").normalize()

    first_session = max(bundles.bundles[bundle].start_session, trading_calendar.first_session)
    if start_date < first_session:
        raise ValidationError(
            f"start_date cannot be earlier than {first_session.date().isoformat()} for this bundle")

    # Roll-forward start_date to valid session
    for i in range(100):
        if trading_calendar.is_session(start_date):
            break
        start_date += pd.Timedelta(days=1)
    else:
        raise ValidationError(f"start_date is not in {calendar_name} calendar")

    # Roll-forward end_date to valid session
    for i in range(100):
        if trading_calendar.is_session(end_date):
            break
        end_date += pd.Timedelta(days=1)
    else:
        raise ValidationError("end_date is not in calendar")

    if (
        end_date < start_date):
        raise ValidationError("end_date cannot be earlier than start_date")

    default_pipeline_loader = EquityPricingLoader.without_fx(
        bundle_data.equity_daily_bar_reader,
        bundle_data.adjustment_reader,
    )

    pipeline_loader = QuantRocketPipelineLoaderRouter(
        asset_db_conn=bundle_data.asset_finder.engine,
        calendar=trading_calendar,
        default_loader=default_pipeline_loader,
        default_loader_columns=EquityPricing.columns
    )

    calendar_domain = domain.get_domain_from_calendar(trading_calendar)

    engine = SimplePipelineEngine(
        pipeline_loader,
        bundle_data.asset_finder,
        calendar_domain)

    return engine.run_pipeline(pipeline, start_date, end_date)

def get_forward_returns(factor, periods=None, bundle=None):
    """
    Get forward returns for the dates and assets in ``factor``, calculated
    over the given periods.

    Parameters
    ----------
    factor : pd.Series
        The factor whose dates and assets to use. The Series should have a
        MultiIndex of (date, asset), as returned by ``run_pipeline``.

    periods : int or list of int
        The periods over which to calculate the forward returns.
        Example: [1, 5, 10]. Defaults to [1].

    bundle : str, optional
        the bundle code. If omitted, the default bundle will be used (and must be set).

    Returns
    -------
    result : pd.DataFrame
        A dataframe of computed forward returns containing one column per
        requested period. It is indexed first by date, then by asset.

    Examples
    --------
    Run a pipeline, then get forward returns for the factor:

    >>> factor = run_pipeline(pipeline, '2018-01-01', '2019-02-01', bundle="usstock-1min")
    >>> forward_returns = get_forward_returns(factor, bundle="usstock-1min")
    """

    if not bundle:
        bundle = get_default_bundle()
        if not bundle:
            raise ValidationError("you must specify a bundle or set a default bundle")
        bundle = bundle["default_bundle"]

    if not periods:
        periods = [1]

    if not isinstance(periods, (list, tuple)):
        periods = [periods]

    columns = {}
    for window_length in periods:
        columns[f"{window_length}D"] = Returns(window_length=window_length+1)

    pipeline = Pipeline(columns=columns)
    returns_data = run_pipeline(
        pipeline,
        factor.index.get_level_values(0).min(),
        factor.index.get_level_values(0).max(),
        bundle=bundle)

    for window_length in periods:
        colname = f"{window_length}D"
        returns_data[colname] = returns_data[colname].unstack().shift(-window_length).stack()

    returns_data = returns_data.reindex(index=factor.index)
    returns_data.index.set_names(["date", "asset"], inplace=True)

    return returns_data
