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
from collections import defaultdict
import pandas as pd
from zipline.pipeline.loaders.base import PipelineLoader
from zipline.lib.adjusted_array import AdjustedArray
from quantrocket.fundamental import (
    get_reuters_financials_reindexed_like,
    get_reuters_estimates_reindexed_like,
    NoFundamentalData
)
from zipline.pipeline.loaders.missing import MISSING_VALUES_BY_DTYPE

class ReutersFinancialsPipelineLoader(implements(PipelineLoader)):

    def __init__(self, zipline_sids_to_real_sids):
        self.zipline_sids_to_real_sids = zipline_sids_to_real_sids

    def load_adjusted_array(self, domain, columns, dates, sids, mask):

        real_sids = [self.zipline_sids_to_real_sids[zipline_sid] for zipline_sid in sids]
        reindex_like = pd.DataFrame(None, index=dates, columns=real_sids)
        reindex_like.index.name = "Date"

        out = {}

        columns_by_interim = defaultdict(list)
        for column in columns:
            interim = column.dataset.extra_coords["interim"]
            columns_by_interim[interim].append(column)

        for interim, columns in columns_by_interim.items():

            coa_codes = list({c.name for c in columns})

            try:
                financials = get_reuters_financials_reindexed_like(
                    reindex_like, coa_codes, fields=["Amount"], interim=interim
                )
            except NoFundamentalData:
                financials = None

            for column in columns:
                missing_value = MISSING_VALUES_BY_DTYPE[column.dtype]
                if financials is not None:
                    financials_for_column = financials.loc[column.name].loc["Amount"]
                else:
                    financials_for_column = reindex_like
                out[column] = AdjustedArray(
                    financials_for_column.astype(column.dtype).fillna(missing_value).values,
                    adjustments={},
                    missing_value=missing_value
                )

        return out

class ReutersEstimatesPipelineLoader(implements(PipelineLoader)):

    def __init__(self, zipline_sids_to_real_sids):
        self.zipline_sids_to_real_sids = zipline_sids_to_real_sids

    def load_adjusted_array(self, domain, columns, dates, sids, mask):

        real_sids = [self.zipline_sids_to_real_sids[zipline_sid] for zipline_sid in sids]
        reindex_like = pd.DataFrame(None, index=dates, columns=real_sids)
        reindex_like.index.name = "Date"

        out = {}

        columns_by_period_type = defaultdict(list)
        for column in columns:
            period_type = column.dataset.extra_coords["period_type"]
            columns_by_period_type[period_type].append(column)

        for period_type, columns in columns_by_period_type.items():

            codes = list({c.name for c in columns})

            fields = list({c.dataset.extra_coords["field"] for c in columns})

            try:
                estimates = get_reuters_estimates_reindexed_like(
                    reindex_like, codes, fields=fields, period_types=[period_type])
            except NoFundamentalData:
                estimates = None

            for column in columns:
                missing_value = MISSING_VALUES_BY_DTYPE[column.dtype]
                field = column.dataset.extra_coords["field"]
                if estimates is not None:
                    estimates_for_column = estimates.loc[column.name].loc[field]
                else:
                    estimates_for_column = reindex_like
                out[column] = AdjustedArray(
                    estimates_for_column.astype(column.dtype).fillna(missing_value).values,
                    adjustments={},
                    missing_value=missing_value
                )

        return out