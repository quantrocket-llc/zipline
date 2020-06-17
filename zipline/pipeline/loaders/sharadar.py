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
    get_sharadar_fundamentals_reindexed_like,
    get_sharadar_institutions_reindexed_like,
    get_sharadar_sp500_reindexed_like,
)
from zipline.pipeline.loaders.missing import MISSING_VALUES_BY_DTYPE

class SharadarFundamentalsPipelineLoader(implements(PipelineLoader)):

    def __init__(self, zipline_sids_to_real_sids, dimension):
        self.zipline_sids_to_real_sids = zipline_sids_to_real_sids
        self.dimension = dimension

    def load_adjusted_array(self, domain, columns, dates, sids, mask):

        fields = [c.name for c in columns]
        real_sids = [self.zipline_sids_to_real_sids[zipline_sid] for zipline_sid in sids]
        reindex_like = pd.DataFrame(None, index=dates, columns=real_sids)
        reindex_like.index.name = "Date"

        fundamentals = get_sharadar_fundamentals_reindexed_like(
            reindex_like, fields=fields, dimension=self.dimension)

        out = {}

        for column in columns:
            out[column] = AdjustedArray(
                fundamentals.loc[column.name].astype(column.dtype).values,
                adjustments={},
                missing_value=MISSING_VALUES_BY_DTYPE[column.dtype]
            )

        return out

class SharadarInstitutionsPipelineLoader(implements(PipelineLoader)):

    def __init__(self, zipline_sids_to_real_sids):
        self.zipline_sids_to_real_sids = zipline_sids_to_real_sids

    def load_adjusted_array(self, domain, columns, dates, sids, mask):

        fields = [c.name for c in columns]
        real_sids = [self.zipline_sids_to_real_sids[zipline_sid] for zipline_sid in sids]
        reindex_like = pd.DataFrame(None, index=dates, columns=real_sids)
        reindex_like.index.name = "Date"

        institutions = get_sharadar_institutions_reindexed_like(
            reindex_like, fields=fields)

        out = {}

        for column in columns:
            out[column] = AdjustedArray(
                institutions.loc[column.name].astype(column.dtype).values,
                adjustments={},
                missing_value=MISSING_VALUES_BY_DTYPE[column.dtype]
            )

        return out

class SharadarSP500PipelineLoader(implements(PipelineLoader)):

    def __init__(self, zipline_sids_to_real_sids):
        self.zipline_sids_to_real_sids = zipline_sids_to_real_sids

    def load_adjusted_array(self, domain, columns, dates, sids, mask):

        real_sids = [self.zipline_sids_to_real_sids[zipline_sid] for zipline_sid in sids]
        reindex_like = pd.DataFrame(None, index=dates, columns=real_sids)
        reindex_like.index.name = "Date"

        in_sp500 = get_sharadar_sp500_reindexed_like(reindex_like)

        # This dataset has only one column
        column = columns[0]

        return {column: AdjustedArray(
            in_sp500.astype(column.dtype).values,
            adjustments={},
            missing_value=MISSING_VALUES_BY_DTYPE[column.dtype]
        )}
