#
# Copyright 2020-2024 QuantRocket LLC
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

from zipline.pipeline.data import reuters
from zipline.pipeline.data import sharadar
from zipline.pipeline.data import brain
from zipline.pipeline.data import alpaca
from zipline.pipeline.data import ibkr
from zipline.pipeline.data.master import SecuritiesMaster
from zipline.pipeline.data.db import Database

from zipline.pipeline.loaders.reuters import (
    ReutersFinancialsPipelineLoader,
    ReutersEstimatesPipelineLoader
)
from zipline.pipeline.loaders.sharadar import (
    SharadarFundamentalsPipelineLoader,
    SharadarSP500PipelineLoader,
    SharadarInstitutionsPipelineLoader
)
from zipline.pipeline.loaders.brain import (
    BSIPipelineLoader,
    BLMCFPipelineLoader,
    BLMECTPipelineLoader

)
from zipline.pipeline.loaders.alpaca import AlpacaETBPipelineLoader
from zipline.pipeline.loaders.ibkr import (
    IBKRAggregateShortableSharesPipelineLoader,
    IBKRBorrowFeesPipelineLoader
)
from zipline.pipeline.loaders.master import SecuritiesMasterPipelineLoader
from zipline.pipeline.loaders.db import DatabasePipelineLoader

class QuantRocketPipelineLoaderRouter:
    """
    Routes to PipelineLoaders.
    """
    def __init__(self, sids_to_real_sids, calendar, default_loader, default_loader_columns):

        # Default
        self.default_loader = default_loader
        self.default_loader_columns = [col.unspecialize() for col in default_loader_columns]

        # Reuters financials
        self.reuters_financials_loader = ReutersFinancialsPipelineLoader(
            sids_to_real_sids)

        # Reuters estimates
        self.reuters_estimates_loader = ReutersEstimatesPipelineLoader(
            sids_to_real_sids)

        # Sharadar
        self.sharadar_fundamentals_loader = SharadarFundamentalsPipelineLoader(
            sids_to_real_sids)
        self.sharadar_sp500_loader = SharadarSP500PipelineLoader(
            sids_to_real_sids)
        self.sharadar_institutions_loader = SharadarInstitutionsPipelineLoader(
            sids_to_real_sids
        )

        # Brain
        self.bsi_loader = BSIPipelineLoader(
            sids_to_real_sids)
        self.blmcf_loader = BLMCFPipelineLoader(
            sids_to_real_sids)
        self.blmect_loader = BLMECTPipelineLoader(
            sids_to_real_sids)

        # Alpaca
        self.alpaca_etb_loader = AlpacaETBPipelineLoader(
            sids_to_real_sids)

        # IBKR
        self.ibkr_shortable_shares_loader = IBKRAggregateShortableSharesPipelineLoader(
            sids_to_real_sids)
        self.ibkr_borrow_fees_loader = IBKRBorrowFeesPipelineLoader(
            sids_to_real_sids)

        # Master
        self.securities_master_loader = SecuritiesMasterPipelineLoader(
            sids_to_real_sids)

        # Database
        self.database_loader = DatabasePipelineLoader(
            sids_to_real_sids, calendar)

    def isin(self, column, dataset):
        """
        Checks dataset membership regardless of specialization.
        """
        return column in dataset.columns or column.unspecialize() in dataset.columns

    def __call__(self, column):
        if column.unspecialize() in self.default_loader_columns:
            return self.default_loader

        # Master
        elif self.isin(column, SecuritiesMaster):
            return self.securities_master_loader

        # Sharadar
        elif (
            hasattr(column.dataset, "dataset_family")
            and column.dataset.dataset_family == sharadar.Fundamentals):
            return self.sharadar_fundamentals_loader
        elif (
            hasattr(column.dataset, "dataset_family")
            and column.dataset.dataset_family == sharadar.Institutions):
            return self.sharadar_institutions_loader
        elif self.isin(column, sharadar.SP500):
            return self.sharadar_sp500_loader

        # Brain
        elif (
            hasattr(column.dataset, "dataset_family")
            and column.dataset.dataset_family == brain.BSI):
            return self.bsi_loader
        elif (
            hasattr(column.dataset, "dataset_family")
            and column.dataset.dataset_family == brain.BLMCF):
            return self.blmcf_loader
        elif self.isin(column, brain.BLMECT):
            return self.blmect_loader

        # Reuters
        elif (
            hasattr(column.dataset, "dataset_family")
            and column.dataset.dataset_family == reuters.Estimates):
            return self.reuters_estimates_loader
        elif (
            hasattr(column.dataset, "dataset_family")
            and column.dataset.dataset_family == reuters.Financials):
            return self.reuters_financials_loader

        # Alpaca
        elif self.isin(column, alpaca.ETB):
            return self.alpaca_etb_loader

        # IBKR
        elif self.isin(column, ibkr.ShortableShares):
            return self.ibkr_shortable_shares_loader
        elif self.isin(column, ibkr.BorrowFees):
            return self.ibkr_borrow_fees_loader

        # Database
        elif issubclass(column.dataset, Database):
            return self.database_loader

        raise ValueError(
            "No PipelineLoader registered for column %s." % column.unspecialize()
        )
