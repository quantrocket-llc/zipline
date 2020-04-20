# Copyright 2020 QuantRocket LLC - All Rights Reserved
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

import pandas as pd
from quantrocket.realtime import get_db_config

class RealtimeDataError(Exception):
    pass

class RealtimeDatabase:

    CODE = None
    FIELDS = {}

    @classmethod
    def get_code(cls):
        if not cls.CODE:
            raise RealtimeDataError(
                "Zipline attempted to access real-time data but no real-time database "
                "has been set, please call zipline_extensions.data.set_realtime_db() "
                "from your Zipline strategy code")
        return cls.CODE

    @classmethod
    def get_db_field(cls, zipline_field):
        try:
            return cls.FIELDS[zipline_field]
        except KeyError:
            raise RealtimeDataError(
                f"Zipline {zipline_field} field is not mapped to any database field in "
                f"{cls.CODE} real-time database, please use zipline_extensions.data.set_realtime_db() "
                "from your Zipline strategy code to define the mapping")

    @classmethod
    def get_fields(cls):
        return cls.FIELDS.copy()

    @classmethod
    def is_set(cls):
        return cls.CODE is not None

def set_realtime_db(code, fields={}):
    """
    Sets the realtime database to use for querying up-to-date minute bars in
    live trading.

    Parameters
    ----------
    code : str, required
        the realtime database code. Must be an aggregate database with
        1-minute bars.

    fields : dict, optional
        dict mapping expected Zipline field names ('close', 'high', 'low', 'open',
        'volume') to realtime database field names

    Returns
    -------
    None

    Examples
    --------
    Set the realtime database and map fields:

    >>> set_realtime_db(
            "usa-stk-tick-1min",
            fields={
                "close": "LastPriceClose",
                "open": "LastPriceOpen",
                "high": "LastPriceHigh",
                "low": "LastPriceLow",
                "volume": "VolumeClose"})
    """

    RealtimeDatabase.CODE = code
    RealtimeDatabase.FIELDS = fields

    config = get_db_config(code)
    bar_size = config["bar_size"]

    if pd.Timedelta(bar_size) != pd.Timedelta("1 min"):
        raise RealtimeDataError(
            f"realtime database must have 1-minute bars but {code} bar_size is {bar_size}")

    expected_zipline_fields = {"close", "low", "high", "open", "volume"}
    if fields:
        unexpected_zipline_fields = set(fields.keys()) - expected_zipline_fields
        if unexpected_zipline_fields:
            raise RealtimeDataError(
                "unexpected Zipline field(s) in realtime field mapping: {0} (expected fields are {1})".format(
                    ", ".join(unexpected_zipline_fields),
                    ", ".join(expected_zipline_fields)))

        unexpected_realtime_fields = set(fields.values()) - set(config["fields"])
        if unexpected_realtime_fields:
            raise RealtimeDataError(
                "unexpected realtime db field(s) in realtime field mapping: {0} (db fields are {1})".format(
                    ", ".join(unexpected_realtime_fields),
                    ", ".join(config["fields"])))
