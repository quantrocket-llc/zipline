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
from zipline.data.data_portal import DataPortal
from zipline.utils.extensions import load_extensions
from zipline.research.exceptions import ValidationError
from zipline.research._asset import asset_finder_cache
from zipline.finance.asset_restrictions import NoRestrictions
from zipline.protocol import BarData
from quantrocket.zipline import get_default_bundle, get_bundle_config
from trading_calendars import get_calendar

def get_data(
    dt: str,
    bundle: str = None,
    data_frequency: str = None
    ) -> BarData:
    """
    Return a zipline.api.BarData object for the specified bundle (or default bundle)
    as of the specified datetime. This is the same object that is passed
    as the `data` parameter to `handle_data` and other backtest functions.

    Parameters
    ----------
    dt : str (YYYY-MM-DD[ HH:MM:SS]), required
        The datetime (for minute data) or date (for daily data) which the
        data object should be anchored to.

    bundle : str, optional
        the bundle code. If omitted, the default bundle will be used (and
        must be set).

    data_frequency : str, optional
        the data frequency. Possible choices: daily, minute. The default is
        "daily" for daily bundles and "minute" for minute bundles. Minute
        bundles also support "daily".

    Returns
    -------
    data : zipline.api.BarData

    Examples
    --------
    Get the data object for July 7, 2020 at 11 AM for the usstock minute
    bundle:

    >>> data = get_data('2020-07-07 11:00:00', bundle="usstock-1min")    # doctest: +SKIP

    Get the data object for July 7, 2020 for a daily bundle:

    >>> data = get_data('2020-07-07', bundle="xjpx-1d-bundle")           # doctest: +SKIP
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
    if not data_frequency:
        config = get_bundle_config(bundle)
        data_frequency = config["data_frequency"]

    calendar_name = bundles.bundles[bundle].calendar_name
    trading_calendar = get_calendar(calendar_name)

    session_minute = pd.Timestamp(dt, tz=trading_calendar.tz)
    session = session_minute.normalize().tz_localize(None).tz_localize("UTC")

    first_session = max(bundles.bundles[bundle].start_session, trading_calendar.first_session)
    if session < first_session:
        raise ValidationError(
            f"date cannot be earlier than {first_session.date().isoformat()} for this bundle")

    if not trading_calendar.is_session(session):
        raise ValidationError(f"requested date {session.date().isoformat()} is not in {calendar_name} calendar")

    if data_frequency == "minute" and not trading_calendar.is_open_on_minute(session_minute):
        raise ValidationError(f"requested time {session_minute.isoformat()} is not in {calendar_name} calendar")

    if data_frequency == "minute":
        equity_minute_reader = future_minute_reader = bundle_data.equity_minute_bar_reader
    else:
        equity_minute_reader = future_minute_reader = None

    asset_finder = asset_finder_cache.get(bundle, bundle_data.asset_finder)
    asset_finder_cache[bundle] = asset_finder

    data_portal = DataPortal(
        asset_finder,
        trading_calendar=trading_calendar,
        first_trading_day=bundle_data.equity_minute_bar_reader.first_trading_day,
        equity_minute_reader=equity_minute_reader,
        equity_daily_reader=bundle_data.equity_daily_bar_reader,
        future_minute_reader=future_minute_reader,
        future_daily_reader=bundle_data.equity_daily_bar_reader,
        adjustment_reader=bundle_data.adjustment_reader)

    data = BarData(
        data_portal=data_portal,
        simulation_dt_func=lambda: session_minute,
        data_frequency=data_frequency,
        trading_calendar=trading_calendar,
        restrictions=NoRestrictions()
    )

    return data
