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
    get_sharadar_fundamentals_reindexed_like,
    get_sharadar_institutions_reindexed_like,
    get_sharadar_sp500_reindexed_like,
    NoFundamentalData
)
from zipline.utils.numpy_utils import datetime64ns_dtype
from zipline.pipeline.loaders.missing import MISSING_VALUES_BY_DTYPE

class SharadarFundamentalsPipelineLoader(implements(PipelineLoader)):

    def __init__(self, zipline_sids_to_real_sids):
        self.zipline_sids_to_real_sids = zipline_sids_to_real_sids

    def load_adjusted_array(self, domain, columns, dates, sids, mask):

        real_sids = [self.zipline_sids_to_real_sids[zipline_sid] for zipline_sid in sids]
        reindex_like = pd.DataFrame(None, index=dates, columns=real_sids)
        reindex_like.index.name = "Date"

        out = {}

        columns_by_dimension = defaultdict(list)
        for column in columns:
            dimension = column.dataset.extra_coords["dimension"]
            columns_by_dimension[dimension].append(column)

        for dimension, columns in columns_by_dimension.items():

            fields = list({c.name for c in columns})

            try:
                fundamentals = get_sharadar_fundamentals_reindexed_like(
                    reindex_like, fields=fields, dimension=dimension)
            except NoFundamentalData:
                fundamentals = None

            for column in columns:
                missing_value = MISSING_VALUES_BY_DTYPE[column.dtype]
                if fundamentals is not None:
                    fundamentals_for_column = fundamentals.loc[column.name]
                    if column.dtype == datetime64ns_dtype:
                        # pd.to_datetime handles NaNs in pandas 0.22 while .astype(column.dtype) doesn't
                        values = fundamentals_for_column.apply(pd.to_datetime).fillna(missing_value).values
                    else:
                        values = fundamentals_for_column.astype(column.dtype).fillna(missing_value).values

                else:
                    values = pd.DataFrame(
                        missing_value,
                        columns=reindex_like.columns,
                        index=reindex_like.index).values

                out[column] = AdjustedArray(
                    values,
                    adjustments={},
                    missing_value=missing_value
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

        try:
            institutions = get_sharadar_institutions_reindexed_like(
                reindex_like, fields=fields)
        except NoFundamentalData:
            institutions = reindex_like

        out = {}

        for column in columns:
            missing_value = MISSING_VALUES_BY_DTYPE[column.dtype]
            out[column] = AdjustedArray(
                institutions.loc[column.name].astype(column.dtype).fillna(missing_value).values,
                adjustments={},
                missing_value=missing_value
            )

        return out

class SharadarSP500PipelineLoader(implements(PipelineLoader)):

    def __init__(self, zipline_sids_to_real_sids):
        self.zipline_sids_to_real_sids = zipline_sids_to_real_sids

    def load_adjusted_array(self, domain, columns, dates, sids, mask):

        real_sids = [self.zipline_sids_to_real_sids[zipline_sid] for zipline_sid in sids]
        reindex_like = pd.DataFrame(False, index=dates, columns=real_sids)
        reindex_like.index.name = "Date"

        try:
            in_sp500 = get_sharadar_sp500_reindexed_like(reindex_like)
        except NoFundamentalData:
            in_sp500 = reindex_like

        # This dataset has only one column
        column = columns[0]

        missing_value = MISSING_VALUES_BY_DTYPE[column.dtype]

        return {column: AdjustedArray(
            in_sp500.astype(column.dtype).fillna(missing_value).values,
            adjustments={},
            missing_value=missing_value
        )}
