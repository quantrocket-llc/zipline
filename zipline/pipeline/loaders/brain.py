#
# Copyright 2024 QuantRocket LLC
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
    get_brain_bsi_reindexed_like,
    get_brain_blmcf_reindexed_like,
    get_brain_blmect_reindexed_like,
    NoFundamentalData
)
from zipline.utils.numpy_utils import datetime64ns_dtype
from zipline.pipeline.loaders.missing import MISSING_VALUES_BY_DTYPE

class BSIPipelineLoader(implements(PipelineLoader)):

    def __init__(self, zipline_sids_to_real_sids):
        self.zipline_sids_to_real_sids = zipline_sids_to_real_sids

    def load_adjusted_array(self, domain, columns, dates, sids, mask):

        real_sids = [self.zipline_sids_to_real_sids[zipline_sid] for zipline_sid in sids]
        reindex_like = pd.DataFrame(None, index=dates, columns=real_sids)
        reindex_like.index.name = "Date"

        out = {}

        # group columns by N to make different calls to get_brain_bsi_reindexed_like
        # for each column group
        column_groups = defaultdict(list)
        for column in columns:
            N = column.dataset.extra_coords["N"]
            column_groups[N].append(column)

        for N, columns in column_groups.items():

            fields = list({c.name for c in columns})

            try:
                metrics = get_brain_bsi_reindexed_like(
                    reindex_like, N=N, fields=fields)
            except NoFundamentalData:
                metrics = None

            for column in columns:
                missing_value = MISSING_VALUES_BY_DTYPE[column.dtype]
                if metrics is not None:
                    metrics_for_column = metrics.loc[column.name]
                    values = metrics_for_column.astype(column.dtype).fillna(missing_value).values

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

class BLMCFPipelineLoader(implements(PipelineLoader)):

    def __init__(self, zipline_sids_to_real_sids):
        self.zipline_sids_to_real_sids = zipline_sids_to_real_sids

    def load_adjusted_array(self, domain, columns, dates, sids, mask):

        real_sids = [self.zipline_sids_to_real_sids[zipline_sid] for zipline_sid in sids]
        reindex_like = pd.DataFrame(None, index=dates, columns=real_sids)
        reindex_like.index.name = "Date"

        out = {}

        # group columns by report_category and dtype to make different calls to
        # get_brain_blmcf_reindexed_like for each column group
        column_groups = defaultdict(list)
        for column in columns:
            report_category = column.dataset.extra_coords["report_category"]
            dtype = column.dtype
            column_groups[(report_category, dtype)].append(column)

        for (report_category, _), columns in column_groups.items():

            fields = list({c.name for c in columns})

            try:
                metrics = get_brain_blmcf_reindexed_like(
                    reindex_like, report_category=report_category, fields=fields)
            except NoFundamentalData:
                metrics = None

            for column in columns:
                missing_value = MISSING_VALUES_BY_DTYPE[column.dtype]
                if metrics is not None:
                    metrics_for_column = metrics.loc[column.name]
                    if column.dtype == datetime64ns_dtype:
                        # pd.to_datetime handles NaNs in pandas 0.22 while .astype(column.dtype) doesn't
                        values = metrics_for_column.apply(pd.to_datetime).fillna(missing_value).values
                    else:
                        values = metrics_for_column.astype(column.dtype).fillna(missing_value).values

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

class BLMECTPipelineLoader(implements(PipelineLoader)):

    def __init__(self, zipline_sids_to_real_sids):
        self.zipline_sids_to_real_sids = zipline_sids_to_real_sids

    def load_adjusted_array(self, domain, columns, dates, sids, mask):

        real_sids = [self.zipline_sids_to_real_sids[zipline_sid] for zipline_sid in sids]
        reindex_like = pd.DataFrame(None, index=dates, columns=real_sids)
        reindex_like.index.name = "Date"

        out = {}

        # group columns by dtype to make different calls to get_brain_blmect_reindexed_like
        # for each column group
        column_groups = defaultdict(list)
        for column in columns:
            dtype = column.dtype
            column_groups[dtype].append(column)

        for _, columns in column_groups.items():

            fields = list({c.name for c in columns})

            try:
                metrics = get_brain_blmect_reindexed_like(
                    reindex_like, fields=fields)
            except NoFundamentalData:
                metrics = None

            for column in columns:
                missing_value = MISSING_VALUES_BY_DTYPE[column.dtype]
                if metrics is not None:
                    metrics_for_column = metrics.loc[column.name]
                    values = metrics_for_column.astype(column.dtype).fillna(missing_value).values

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
