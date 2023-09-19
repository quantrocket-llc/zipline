# Copyright 2022 QuantRocket LLC - All Rights Reserved
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

import unittest
from unittest.mock import patch
import pandas as pd
import numpy as np
from zipline.pipeline.data import sharadar
from zipline.pipeline.loaders.sharadar import (
    SharadarFundamentalsPipelineLoader,
    SharadarInstitutionsPipelineLoader,
    SharadarSP500PipelineLoader)
from quantrocket.fundamental import NoFundamentalData

class SharadarFundamentalsLoaderTestCase(unittest.TestCase):

    @patch("zipline.pipeline.loaders.sharadar.get_sharadar_fundamentals_reindexed_like")
    def test_query_by_column_groups(self,
                                    mock_get_sharadar_fundamentals_reindexed_like):
        """
        Tests that the SharadarFundamentalsPipelineLoader appropriately groups columns
        for querying get_sharadar_fundamentals_reindexed_like.
        """
        sharadar_art = sharadar.Fundamentals.slice(dimension="ART", period_offset=0)
        sharadar_art_previous = sharadar.Fundamentals.slice(dimension="ART", period_offset=-1)
        sharadar_arq = sharadar.Fundamentals.slice(dimension="ARQ", period_offset=0)

        art_eps = sharadar_art.EPS
        art_reportperiod = sharadar_art.REPORTPERIOD
        art_previous_eps = sharadar_art_previous.EPS
        arq_eps = sharadar_arq.EPS
        arq_revenue = sharadar_arq.REVENUE

        zipline_sids_to_real_sids = {
            1: "FI12345",
            2: "FI23456"
        }
        loader = SharadarFundamentalsPipelineLoader(zipline_sids_to_real_sids)
        domain = art_eps.domain
        columns = [art_eps, art_previous_eps, art_reportperiod, arq_eps, arq_revenue]
        dates = pd.date_range(start="2022-07-25", periods=2)
        sids= pd.Index([1, 2])
        mask = np.array([[True, True], [True, True]])


        def _mock_get_sharadar_fundamentals_reindexed_like(
            reindex_like,
            fields=None,
            dimension="ART",
            period_offset=0):

            if dimension == 'ART' and period_offset == 0 and fields == ["REPORTPERIOD"]:

                return pd.DataFrame(
                    dict(
                        FI12345=["2022-06-30", "2022-06-30"],
                        FI23456=["2022-06-20", "2022-06-20"],
                    ),
                    index=pd.MultiIndex.from_product(
                        [["REPORTPERIOD"], dates],
                        names=["Field", "Date"]
                    )
                )
            elif dimension == 'ART' and period_offset == 0 and fields == ["EPS"]:

                return pd.DataFrame(
                    dict(
                        FI12345=[1.40, 1.40],
                        FI23456=[0.20, 0.20],
                    ),
                    index=pd.MultiIndex.from_product(
                        [["EPS"], dates],
                        names=["Field", "Date"]
                    )
                )

            elif dimension == 'ART' and period_offset == -1 and fields == ["EPS"]:

                return pd.DataFrame(
                    dict(
                        FI12345=[1.30, 1.30],
                        FI23456=[0.10, 0.10],
                    ),
                    index=pd.MultiIndex.from_product(
                        [["EPS"], dates],
                        names=["Field", "Date"]
                    )
                )
            elif dimension == 'ARQ' and period_offset == 0 and set(fields) == {"EPS", "REVENUE"}:

                return pd.DataFrame(
                    dict(
                        FI12345=[1.35, 1.35, 5e10, 5e10],
                        FI23456=[0.10, 0.10, 1e10, 1e10],
                    ),
                    index=pd.MultiIndex.from_product(
                        [["EPS", "REVENUE"], dates],
                        names=["Field", "Date"]
                    )
                )

            else:
                raise ValueError(f"unexpected parameter combination: {dimension}, {period_offset}, {fields}")

        mock_get_sharadar_fundamentals_reindexed_like.side_effect = _mock_get_sharadar_fundamentals_reindexed_like

        array = loader.load_adjusted_array(
            domain,
            columns,
            dates,
            sids,
            mask
        )

        self.assertEqual(len(mock_get_sharadar_fundamentals_reindexed_like.mock_calls), 4)
        expected_calls = [
            ("ART", 0, {"REPORTPERIOD"}),
            ("ART", 0, {"EPS"}),
            ("ART", -1, {"EPS"}),
            ("ARQ", 0, {"EPS", "REVENUE"})
        ]
        for mock_call in mock_get_sharadar_fundamentals_reindexed_like.mock_calls:
            _, args, kwargs = mock_call
            dimension = kwargs["dimension"]
            period_offset = kwargs["period_offset"]
            fields = set(kwargs["fields"])
            expected_calls.remove((dimension, period_offset, fields))

        self.assertEqual(len(expected_calls), 0 )

        np.testing.assert_array_equal(
            array[art_reportperiod].data,
            np.array([[np.datetime64('2022-06-30'), np.datetime64('2022-06-20')],
                    [np.datetime64('2022-06-30'), np.datetime64('2022-06-20')]]))
        np.testing.assert_array_equal(
            array[art_eps].data,
            np.array([[1.40, 0.2], [1.40, 0.2]]))
        np.testing.assert_array_equal(
            array[art_previous_eps].data,
            np.array([[1.30, 0.1], [1.30, 0.1]]))
        np.testing.assert_array_equal(
            array[arq_eps].data,
            np.array([[1.35, 0.1], [1.35, 0.1]]))
        np.testing.assert_array_equal(
            array[arq_revenue].data,
            np.array([[5e10, 1e10], [5e10, 1e10]]))

    def test_no_data(self):
        """
        Tests handling when get_sharadar_fundamentals_reindexed_like returns no data.
        """
        sharadar_arq = sharadar.Fundamentals.slice(dimension="ARQ", period_offset=0)

        arq_eps = sharadar_arq.EPS
        arq_revenue = sharadar_arq.REVENUE

        zipline_sids_to_real_sids = {
            1: "FI12345",
            2: "FI23456"
        }
        loader = SharadarFundamentalsPipelineLoader(zipline_sids_to_real_sids)
        domain = arq_eps.domain
        columns = [arq_eps, arq_revenue]
        dates = pd.date_range(start="2022-07-25", periods=2)
        sids= pd.Index([1, 2])
        mask = np.array([[True, True], [True, True]])


        def mock_get_sharadar_fundamentals_reindexed_like(
            reindex_like,
            fields=None,
            dimension="ART",
            period_offset=0):

            raise NoFundamentalData("no fundamental data match the query parameters")

        with patch('zipline.pipeline.loaders.sharadar.get_sharadar_fundamentals_reindexed_like', new=mock_get_sharadar_fundamentals_reindexed_like):

            array = loader.load_adjusted_array(
                domain,
                columns,
                dates,
                sids,
                mask
            )

        np.testing.assert_array_equal(
            array[arq_eps].data,
            np.array([[np.nan, np.nan], [np.nan, np.nan]]))
        np.testing.assert_array_equal(
            array[arq_revenue].data,
            np.array([[np.nan, np.nan], [np.nan, np.nan]]))

class SharadarInstitutionsLoaderTestCase(unittest.TestCase):

    def test_institutions_data(self):
        """
        Tests loading data from get_sharadar_institutions_reindexed_like.
        """
        total_val = sharadar.Institutions.slice(period_offset=0).TOTALVALUE
        fund_val = sharadar.Institutions.slice(period_offset=0).FNDVALUE

        zipline_sids_to_real_sids = {
            1: "FI12345",
            2: "FI23456"
        }
        loader = SharadarInstitutionsPipelineLoader(zipline_sids_to_real_sids)
        domain = total_val.domain
        columns = [total_val, fund_val]
        dates = pd.date_range(start="2022-07-25", periods=2)
        sids= pd.Index([1, 2])
        mask = np.array([[True, True], [True, True]])


        def mock_get_sharadar_institutions_reindexed_like(
            reindex_like,
            fields=None,
            shift=45):

            return pd.DataFrame(
                dict(
                    FI12345=[1.35, 1.36, 5e10, 6e10],
                    FI23456=[0.10, 0.12, 1e10, 2e10],
                ),
                index=pd.MultiIndex.from_product(
                    [["TOTALVALUE", "FNDVALUE"], dates],
                    names=["Field", "Date"]
                )
            )

        with patch('zipline.pipeline.loaders.sharadar.get_sharadar_institutions_reindexed_like', new=mock_get_sharadar_institutions_reindexed_like):

            array = loader.load_adjusted_array(
                domain,
                columns,
                dates,
                sids,
                mask
            )

        np.testing.assert_array_equal(
            array[total_val].data,
            np.array([[1.35, 0.10], [1.36, 0.12]]))
        np.testing.assert_array_equal(
            array[fund_val].data,
            np.array([[5e10, 1e10], [6e10, 2e10]]))

    def test_no_data(self):
        """
        Tests handling when get_sharadar_institutions_reindexed_like returns no data.
        """
        total_val = sharadar.Institutions.slice(period_offset=0).TOTALVALUE
        fund_val = sharadar.Institutions.slice(period_offset=0).FNDVALUE

        zipline_sids_to_real_sids = {
            1: "FI12345",
            2: "FI23456"
        }
        loader = SharadarInstitutionsPipelineLoader(zipline_sids_to_real_sids)
        domain = total_val.domain
        columns = [total_val, fund_val]
        dates = pd.date_range(start="2022-07-25", periods=2)
        sids= pd.Index([1, 2])
        mask = np.array([[True, True], [True, True]])


        def mock_get_sharadar_institutions_reindexed_like(
            reindex_like,
            fields=None,
            shift=45):

            raise NoFundamentalData("no fundamental data match the query parameters")

        with patch('zipline.pipeline.loaders.sharadar.get_sharadar_institutions_reindexed_like', new=mock_get_sharadar_institutions_reindexed_like):

            array = loader.load_adjusted_array(
                domain,
                columns,
                dates,
                sids,
                mask
            )

        np.testing.assert_array_equal(
            array[total_val].data,
            np.array([[np.nan, np.nan], [np.nan, np.nan]]))
        np.testing.assert_array_equal(
            array[fund_val].data,
            np.array([[np.nan, np.nan], [np.nan, np.nan]]))

class SharadarSP500LoaderTestCase(unittest.TestCase):

    def test_sp500_data(self):
        """
        Tests loading data from get_sharadar_sp500_reindexed_like.
        """
        in_sp500 = sharadar.SP500.in_sp500

        zipline_sids_to_real_sids = {
            1: "FI12345",
            2: "FI23456"
        }
        loader = SharadarSP500PipelineLoader(zipline_sids_to_real_sids)
        domain = in_sp500.domain
        columns = [in_sp500]
        dates = pd.date_range(start="2022-07-25", periods=2)
        sids= pd.Index([1, 2])
        mask = np.array([[True, True], [True, True]])


        def mock_get_sharadar_sp500_reindexed_like(reindex_like):

            return pd.DataFrame(
                dict(
                    FI12345=[True, True],
                    FI23456=[False, False],
                ),
                index=dates)

        with patch('zipline.pipeline.loaders.sharadar.get_sharadar_sp500_reindexed_like', new=mock_get_sharadar_sp500_reindexed_like):

            array = loader.load_adjusted_array(
                domain,
                columns,
                dates,
                sids,
                mask
            )

        np.testing.assert_array_equal(
            array[in_sp500].data,
            np.array([[True, False], [True, False]]))
