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
from quantrocket.fundamental import (
    get_reuters_financials_reindexed_like,
    get_reuters_estimates_reindexed_like
)
from zipline.pipeline.loaders.missing import MISSING_VALUES_BY_DTYPE

class ReutersFinancialsPipelineLoader(implements(PipelineLoader)):

    def __init__(self, zipline_sids_to_real_sids):
        self.zipline_sids_to_real_sids = zipline_sids_to_real_sids

    def load_adjusted_array(self, domain, columns, dates, sids, mask):

        coa_codes = [c.name for c in columns]
        real_sids = [self.zipline_sids_to_real_sids[zipline_sid] for zipline_sid in sids]
        reindex_like = pd.DataFrame(None, index=dates, columns=real_sids)
        reindex_like.index.name = "Date"

        interim = columns[0].dataset.extra_coords["interim"]

        financials = get_reuters_financials_reindexed_like(
            reindex_like, coa_codes, fields=["Amount"], interim=interim
        )

        out = {}

        for column in columns:
            missing_value = MISSING_VALUES_BY_DTYPE[column.dtype]
            out[column] = AdjustedArray(
                financials.loc[column.name].astype(column.dtype).fillna(missing_value).values,
                adjustments={},
                missing_value=missing_value
            )

        return out

class ReutersEstimatesPipelineLoader(implements(PipelineLoader)):

    def __init__(self, zipline_sids_to_real_sids):
        self.zipline_sids_to_real_sids = zipline_sids_to_real_sids

    def load_adjusted_array(self, domain, columns, dates, sids, mask):

        codes = [c.name for c in columns]
        real_sids = [self.zipline_sids_to_real_sids[zipline_sid] for zipline_sid in sids]
        reindex_like = pd.DataFrame(None, index=dates, columns=real_sids)
        reindex_like.index.name = "Date"

        field = columns[0].dataset.extra_coords["field"]
        period_type = columns[0].dataset.extra_coords["period_type"]

        estimates = get_reuters_estimates_reindexed_like(
            reindex_like, codes, fields=[field], period_types=[period_type])

        out = {}

        for column in columns:
            missing_value = MISSING_VALUES_BY_DTYPE[column.dtype]
            out[column] = AdjustedArray(
                estimates.loc[column.name].astype(column.dtype).fillna(missing_value).values,
                adjustments={},
                missing_value=missing_value
            )

        return out