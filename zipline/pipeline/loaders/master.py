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

from interface import implements
import pandas as pd
from zipline.pipeline.loaders.base import PipelineLoader
from zipline.lib.adjusted_array import AdjustedArray
from zipline.pipeline.loaders.missing import MISSING_VALUES_BY_DTYPE
from zipline.utils.numpy_utils import datetime64ns_dtype
from quantrocket.master import get_securities_reindexed_like

class SecuritiesMasterPipelineLoader(implements(PipelineLoader)):

    def __init__(self, zipline_sids_to_real_sids):
        self.zipline_sids_to_real_sids = zipline_sids_to_real_sids

    def load_adjusted_array(self, domain, columns, dates, sids, mask):

        fields = [c.name for c in columns]
        real_sids = [self.zipline_sids_to_real_sids[zipline_sid] for zipline_sid in sids]
        reindex_like = pd.DataFrame(None, index=dates, columns=real_sids)
        reindex_like.index.name = "Date"

        securities = get_securities_reindexed_like(
            reindex_like, fields=fields)

        out = {}

        for column in columns:
            missing_value = MISSING_VALUES_BY_DTYPE[column.dtype]
            if column.dtype == datetime64ns_dtype:
                # pd.to_datetime handles NaNs in pandas 0.22 while .astype(column.dtype) doesn't
                values = securities.loc[column.name].apply(pd.to_datetime).fillna(missing_value).values
            else:
                values = securities.loc[column.name].astype(column.dtype).fillna(missing_value).values

            out[column] = AdjustedArray(
                values,
                adjustments={},
                missing_value=missing_value
            )

        return out
