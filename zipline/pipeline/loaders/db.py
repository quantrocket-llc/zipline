# Copyright 2021 QuantRocket LLC
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

from interface import implements
import pandas as pd
from collections import defaultdict
from zipline.pipeline.loaders.base import PipelineLoader
from zipline.lib.adjusted_array import AdjustedArray
from zipline.pipeline.loaders.missing import MISSING_VALUES_BY_DTYPE
from zipline.pipeline.sentinels import NotSpecified
from zipline.utils.numpy_utils import (
    bool_dtype,
    float64_dtype,
    object_dtype,
    datetime64ns_dtype)
from quantrocket import get_prices_reindexed_like
from quantrocket.exceptions import NoData

class DatabasePipelineLoader(implements(PipelineLoader)):
    """
    Loads data using quantrocket.get_prices_reindexed_like.
    """

    def __init__(self, zipline_sids_to_real_sids, calendar):
        self.zipline_sids_to_real_sids = zipline_sids_to_real_sids
        self.calendar = calendar

    def load_adjusted_array(self, domain, columns, dates, sids, mask):

        real_sids = [self.zipline_sids_to_real_sids[zipline_sid] for zipline_sid in sids]
        reindex_like = pd.DataFrame(None, index=dates, columns=real_sids)
        reindex_like.index.name = "Date"

        out = {}

        columns_by_db = defaultdict(list)
        for column in columns:
            db = column.dataset.CODE
            columns_by_db[db].append(column)

        for db, columns in columns_by_db.items():

            fields = list({c.name for c in columns})

            dataset = columns[0].dataset

            try:
                prices = get_prices_reindexed_like(
                    reindex_like,
                    db,
                    fields=fields,
                    shift=dataset.SHIFT,
                    ffill=dataset.FFILL,
                    lookback_window=dataset.LOOKBACK_WINDOW,
                    timezone=self.calendar.tz.zone,
                    times=dataset.TIMES,
                    agg=dataset.AGG,
                    cont_fut=dataset.CONT_FUT,
                    data_frequency=dataset.DATA_FREQUENCY)
            except NoData:
                prices = None

            for column in columns:

                if column.missing_value is NotSpecified or column.missing_value is None:
                    # Look up missing value by dtype kind
                    # https://numpy.org/doc/stable/reference/generated/numpy.dtype.kind.html

                    # floating point, complex floating point
                    if column.dtype.kind in ("f", "c"):
                        missing_value = MISSING_VALUES_BY_DTYPE[float64_dtype]
                    # boolean
                    elif column.dtype.kind == "b":
                        missing_value = MISSING_VALUES_BY_DTYPE[bool_dtype]
                    # object, string, unicode, void
                    elif column.dtype.kind in ("O", "S", "U", "V"):
                        missing_value = MISSING_VALUES_BY_DTYPE[object_dtype]
                    # datetime, timedelta
                    elif column.dtype.kind in ("M","m"):
                        missing_value = MISSING_VALUES_BY_DTYPE[datetime64ns_dtype]
                    else:
                        # should never get here because int requires missing value
                        raise ValueError(
                            f"you must specify a missing_value for column {column.name}")
                else:
                    missing_value = column.missing_value

                if prices is not None:
                    prices_for_column = prices.loc[column.name]

                    if column.dtype == datetime64ns_dtype:
                        # pd.to_datetime handles NaNs in pandas 0.22 while .astype(column.dtype) doesn't
                        values = prices_for_column.apply(pd.to_datetime).fillna(missing_value).values
                    else:
                        values = prices_for_column.fillna(missing_value).astype(column.dtype).values

                else:
                    values = pd.DataFrame(
                        missing_value,
                        columns=sids,
                        index=dates).values

                out[column] = AdjustedArray(
                    values,
                    adjustments={},
                    missing_value=missing_value
                )

        return out
