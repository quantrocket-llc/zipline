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
from typing import Union, Any
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
from zipline.research.exceptions import ValidationError, RequestedEndDateAfterBundleEndDate
from zipline.research._asset import asset_finder_cache
from quantrocket.zipline import get_default_bundle
from trading_calendars import get_calendar


def run_pipeline(
    pipeline: Pipeline,
    start_date: str,
    end_date: str = None,
    bundle: str = None
    ) -> pd.DataFrame:
    """
    Compute values for pipeline from start_date to end_date, using the specified
    bundle or the default bundle.

    This function can be used to run pipelines outside of the context of an algorithm.
    Inside an algorithm, pipelines are run automatically.

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
    >>> pipeline = Pipeline(                                                                  # doctest: +SKIP
            columns={
                '1Y': Returns(window_length=252),
            })
    >>> factor = run_pipeline(pipeline, '2018-01-01', '2019-02-01', bundle="usstock-1min")    # doctest: +SKIP
    """
    return _run_pipeline(
        pipeline,
        start_date=start_date,
        end_date=end_date,
        bundle=bundle)

def _run_pipeline(pipeline, start_date, end_date=None, bundle=None, mask=None):
    """
    Internal function for run_pipeline that adds a mask parameter used by
    get_forward_returns. See run_pipeline.

    Parameters
    ----------
    mask : DataFrame, optional
        boolean DataFrame of dates (index) and assets (columns), indicating which date
        and asset combinations to compute values for. Values will only be computed for
        dates and assets containing True values.
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

    start_date = pd.Timestamp(start_date)

    if start_date.tz:
        start_date = start_date.tz_convert("UTC")
    else:
        start_date = start_date.tz_localize("UTC")

    requested_end_date = end_date
    if end_date:
        end_date = pd.Timestamp(end_date)
    else:
        end_date = pd.Timestamp.now().normalize()

    if end_date.tz:
        end_date = end_date.tz_convert("UTC")
    else:
        end_date = end_date.tz_localize("UTC")

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

    # Check if data is available through the requested end date (this prevents
    # confusing errors that can occur when a user runs a pipeline through a certain
    # end date but hasn't updated their bundle to that end date)
    bundle_end_date = bundle_data.asset_finder.get_bundle_end_date()
    max_end_date = trading_calendar.next_session_label(bundle_end_date)
    if max_end_date < end_date:
        if requested_end_date:
            raise RequestedEndDateAfterBundleEndDate(
                f"end_date ({pd.Timestamp(requested_end_date).date()}) must be no "
                f"later than {max_end_date.date()} because {bundle} bundle contains "
                f"no data after {bundle_end_date.date()} (Because pipeline data is "
                f"lagged, {bundle_end_date.date()} data will appear in the pipeline "
                f"output for {max_end_date.date()}.)")
        else:
            # if the user didn't specify an end date, just silently use the max end date
            end_date = max_end_date

    default_pipeline_loader = EquityPricingLoader.without_fx(
        bundle_data.equity_daily_bar_reader,
        bundle_data.adjustment_reader,
    )
    asset_finder = asset_finder_cache.get(bundle, bundle_data.asset_finder)
    asset_finder_cache[bundle] = asset_finder

    pipeline_loader = QuantRocketPipelineLoaderRouter(
        asset_db_conn=asset_finder.engine,
        calendar=trading_calendar,
        default_loader=default_pipeline_loader,
        default_loader_columns=EquityPricing.columns
    )

    calendar_domain = domain.get_domain_from_calendar(trading_calendar)

    kwargs = {}

    if mask is not None:
        mask.columns = [asset.sid for asset in mask.columns]

        def populate_initial_workspace(
            initial_workspace,
            root_mask_term,
            execution_plan,
            dates,
            assets):

            mask_values = mask.reindex(index=dates, columns=assets).fillna(
                False).values

            initial_workspace[root_mask_term] = mask_values
            return initial_workspace

        kwargs["populate_initial_workspace"] = populate_initial_workspace

    engine = SimplePipelineEngine(
        pipeline_loader,
        asset_finder,
        calendar_domain,
        **kwargs)

    return engine.run_pipeline(pipeline, start_date, end_date)

def get_forward_returns(
    factor: Union['pd.Series[Any]', 'pd.DataFrame'],
    periods: Union[int, list[int]] = None,
    bundle: str = None
    ) -> pd.DataFrame:
    """
    Get forward returns for the dates and assets in the input ``factor``
    (typically the output of `run_pipeline`), calculated over the given
    periods.

    Parameters
    ----------
    factor : pd.Series or pd.DataFrame
        The factor whose dates and assets to use. The Series or DataFrame
        should have a MultiIndex of (date, asset), as returned by ``run_pipeline``.

    periods : int or list of int
        The period(s) over which to calculate the forward returns.
        Example: [1, 5, 21]. Defaults to [1].

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

    >>> factor = run_pipeline(pipeline, '2018-01-01', '2019-02-01', bundle="usstock-1min")    # doctest: +SKIP
    >>> forward_returns = get_forward_returns(factor, bundle="usstock-1min")                  # doctest: +SKIP
    """

    if not bundle:
        bundle = get_default_bundle()
        if not bundle:
            raise ValidationError("you must specify a bundle or set a default bundle")
        bundle = bundle["default_bundle"]

    if factor.index.empty:
        raise ValidationError(
            "cannot compute forward returns because the factor you provided is empty")

    if not periods:
        periods = [1]

    if not isinstance(periods, (list, tuple)):
        periods = [periods]

    columns = {}
    for window_length in periods:
        columns[f"{window_length}D"] = Returns(window_length=window_length+1)

    pipeline = Pipeline(columns=columns)

    start_date = factor.index.get_level_values("date").min()
    orig_end_date = factor.index.get_level_values("date").max()

    # For end_date, request enough cushion to calculate forward returns
    index_cushion = pd.date_range(
        start=factor.index.levels[0].max(),
        periods=max(periods) + 5,
        freq=factor.index.levels[0].freq)

    end_date = index_cushion.max()

    # factor might be a Series or a DataFrame, normalize to a DataFrame
    if isinstance(factor, pd.Series):
        factor = factor.to_frame()

    # a pipeline is allowed to have no columns, but we need a col
    # to unstack
    if factor.columns.empty:
        factor = factor.copy()
        factor["col"] = 1

    mask = factor.iloc[:, 0].unstack()
    mask = pd.DataFrame(
        True,
        index=mask.index.union(index_cushion),
        columns=mask.columns)

    try:
        returns_data = _run_pipeline(
            pipeline,
            start_date,
            end_date,
            bundle=bundle,
            mask=mask)
    except RequestedEndDateAfterBundleEndDate as e:
        # Improve the error message, since the error may have been caused
        # by having to extend the index to compute forward returns
        e.args = (e.args[0] + (
            f" The end_date {end_date.date()} resulted from extending "
            f"the requested pipeline end date of {orig_end_date.date()} to compute "
            f"{max(periods)}D forward returns. You may need to end the pipeline "
            f"earlier or shorten the forward returns computation."),)
        raise e

    for window_length in periods:
        colname = f"{window_length}D"
        returns_data[colname] = returns_data[colname].unstack().shift(-window_length).stack(dropna=False)

    returns_data = returns_data.reindex(index=factor.index)
    returns_data.index.set_names(["date", "asset"], inplace=True)

    return returns_data
