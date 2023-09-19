import inspect
from functools import partial

import pandas as pd
from exchange_calendars import ExchangeCalendar
from exchange_calendars import clear_calendars
from exchange_calendars import get_calendar as ec_get_calendar  # get_calendar,
from exchange_calendars import (
    get_calendar_names,
    register_calendar,
    register_calendar_alias,
)
from exchange_calendars.calendar_utils import global_calendar_dispatcher

# from exchange_calendars.errors import InvalidCalendarName
from exchange_calendars.utils.pandas_utils import days_at_time  # noqa: reexport

ExchangeCalendar = ExchangeCalendar # noqa: reexport for Sphinx
register_calendar_alias = register_calendar_alias # noqa: reexport for Sphinx

# https://stackoverflow.com/questions/56753846/python-wrapping-function-with-signature
def wrap_with_signature(signature):
    def wrapper(func):
        func.__signature__ = signature
        return func

    return wrapper


@wrap_with_signature(inspect.signature(ec_get_calendar))
def get_calendar(name, *args, **kwargs):
    if name in ["us_futures", "CMES", "XNYS", "NYSE"] and "start" not in kwargs:
        # backward compat: trading_calendars defaulted to starting
        # at 1990-01-01; this is mainly for the benefit of the test suite
        kwargs["start"] = pd.Timestamp("1990-01-01")
    return ec_get_calendar(name, *args, side="right", **kwargs)


# get_calendar = compose(partial(get_calendar, side="right"), "XNYS")
# NOTE Sessions are now timezone-naive (previously UTC).
# Schedule columns now have timezone set as UTC
# (whilst the times have always been defined in terms of UTC,
# previously the dtype was timezone-naive).