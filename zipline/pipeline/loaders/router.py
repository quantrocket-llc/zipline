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

from zipline.pipeline.data.reuters import (
    ReutersAnnualFinancials,
    ReutersInterimFinancials,
    ReutersAnnualEstimates,
    ReutersAnnualActuals,
    ReutersQuarterlyEstimates,
    ReutersQuarterlyActuals
)
from zipline.pipeline.data.sharadar import (
    SharadarSP500,
    SharadarAnnualFundamentals,
    SharadarQuarterlyFundamentals,
    SharadarTrailingTwelveMonthFundamentals,
    SharadarInstitutions
)
from zipline.pipeline.data.master import SecuritiesMaster

from zipline.pipeline.loaders.reuters import (
    ReutersFinancialsPipelineLoader,
    ReutersEstimatesPipelineLoader
)
from zipline.pipeline.loaders.sharadar import (
    SharadarFundamentalsPipelineLoader,
    SharadarSP500PipelineLoader,
    SharadarInstitutionsPipelineLoader
)
from zipline.pipeline.loaders.master import SecuritiesMasterPipelineLoader

class QuantRocketPipelineLoaderRouter:
    """
    Routes to PipelineLoaders.
    """
    def __init__(self, asset_db_conn, calendar, default_loader, default_loader_columns):
        self.asset_db_conn = asset_db_conn
        zipline_sids_to_real_sids = self._get_all_asset_sids()

        # Default
        self.default_loader = default_loader
        self.default_loader_columns = default_loader_columns

        # Reuters financials
        self.reuters_annual_financials_loader = ReutersFinancialsPipelineLoader(
            zipline_sids_to_real_sids, interim=False)
        self.reuters_interim_financials_loader = ReutersFinancialsPipelineLoader(
            zipline_sids_to_real_sids, interim=True)

        # Reuters estimates
        self.reuters_annual_estimates_loader = ReutersEstimatesPipelineLoader(
            zipline_sids_to_real_sids, period_type="A", field="Mean")
        self.reuters_annual_actuals_loader = ReutersEstimatesPipelineLoader(
            zipline_sids_to_real_sids, period_type="A", field="Actual")
        self.reuters_quarterly_estimates_loader = ReutersEstimatesPipelineLoader(
            zipline_sids_to_real_sids, period_type="Q", field="Mean")
        self.reuters_quarterly_actuals_loader = ReutersEstimatesPipelineLoader(
            zipline_sids_to_real_sids, period_type="Q", field="Actual")

        # Sharadar
        self.sharadar_quarterly_fundamentals_loader = SharadarFundamentalsPipelineLoader(
            zipline_sids_to_real_sids, dimension="ARQ")
        self.sharadar_annual_fundamentals_loader = SharadarFundamentalsPipelineLoader(
            zipline_sids_to_real_sids, dimension="ARY")
        self.sharadar_ttm_fundamentals_loader = SharadarFundamentalsPipelineLoader(
            zipline_sids_to_real_sids, dimension="ART")
        self.sharadar_sp500_loader = SharadarSP500PipelineLoader(
            zipline_sids_to_real_sids)
        self.sharadar_institutions_loader = SharadarInstitutionsPipelineLoader(
            zipline_sids_to_real_sids
        )

        # Master
        self.securities_master_loader = SecuritiesMasterPipelineLoader(
            zipline_sids_to_real_sids)

    def isin(self, column, dataset):
        """
        Checks dataset membership regardless of specialization.
        """
        return column in dataset.columns or column.unspecialize() in dataset.columns

    def __call__(self, column):
        if column in self.default_loader_columns:
            return self.default_loader
        elif self.isin(column, SecuritiesMaster):
            return self.securities_master_loader
        elif self.isin(column, SharadarQuarterlyFundamentals):
            return self.sharadar_quarterly_fundamentals_loader
        elif self.isin(column, SharadarTrailingTwelveMonthFundamentals):
            return self.sharadar_ttm_fundamentals_loader
        elif self.isin(column, SharadarAnnualFundamentals):
            return self.sharadar_annual_fundamentals_loader
        elif self.isin(column, SharadarInstitutions):
            return self.sharadar_institutions_loader
        elif self.isin(column, SharadarSP500):
            return self.sharadar_sp500_loader
        elif self.isin(column, ReutersAnnualEstimates):
            return self.reuters_annual_estimates_loader
        elif self.isin(column, ReutersAnnualActuals):
            return self.reuters_annual_actuals_loader
        elif self.isin(column, ReutersQuarterlyEstimates):
            return self.reuters_quarterly_estimates_loader
        elif self.isin(column, ReutersQuarterlyActuals):
            return self.reuters_quarterly_actuals_loader
        elif self.isin(column, ReutersAnnualFinancials):
            return self.reuters_annual_financials_loader
        elif self.isin(column, ReutersInterimFinancials):
            return self.reuters_interim_financials_loader
        raise ValueError(
            "No PipelineLoader registered for column %s." % column.unspecialize()
        )

    def _get_all_asset_sids(self):
        """
        Returns a dict of real sids to zipline sids, and a dict of zipline sids to real sids.
        """
        sql = """
        SELECT
            sid,
            real_sid
        FROM
            equities
        """
        result = self.asset_db_conn.execute(sql)
        zipline_sids_to_real_sids = dict([(row[0], row[1]) for row in result.fetchall()])
        return zipline_sids_to_real_sids
