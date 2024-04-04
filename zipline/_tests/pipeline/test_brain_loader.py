# Copyright 2024 QuantRocket LLC - All Rights Reserved
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
from zipline.pipeline.data import brain
from zipline.pipeline.loaders.brain import (
    BSIPipelineLoader,
    BLMCFPipelineLoader,
    BLMECTPipelineLoader)
from zipline.utils.numpy_utils import NaTD
from quantrocket.fundamental import NoFundamentalData

class BSILoaderTestCase(unittest.TestCase):

    @patch("zipline.pipeline.loaders.brain.get_brain_bsi_reindexed_like")
    def test_query_by_column_groups(self,
                                    mock_get_brain_bsi_reindexed_like):
        """
        Tests that the BSIPipelineLoader appropriately groups columns
        for querying get_brain_bsi_reindexed_like.
        """
        bsi_1 = brain.BSI.slice(1)
        bsi_7 = brain.BSI.slice(7)

        bsi_1_sentiment = bsi_1.SENTIMENT_SCORE
        bsi_1_volume = bsi_1.VOLUME
        bsi_7_sentiment = bsi_7.SENTIMENT_SCORE

        zipline_sids_to_real_sids = {
            1: "FI12345",
            2: "FI23456"
        }
        loader = BSIPipelineLoader(zipline_sids_to_real_sids)
        domain = bsi_7.domain
        columns = [bsi_1_sentiment, bsi_1_volume, bsi_7_sentiment]
        dates = pd.date_range(start="2022-07-25", periods=2)
        sids= pd.Index([1, 2])
        mask = np.array([[True, True], [True, True]])


        def _mock_get_brain_bsi_reindexed_like(
            reindex_like,
            fields=None,
            N=1):

            if N == 1 and set(fields) == {"SENTIMENT_SCORE", "VOLUME"}:

                return pd.DataFrame(
                    dict(
                        FI12345=[1.35, 1.35, 5e10, 5e10],
                        FI23456=[0.10, 0.10, 1e10, 1e10],
                    ),
                    index=pd.MultiIndex.from_product(
                        [["SENTIMENT_SCORE", "VOLUME"], dates],
                        names=["Field", "Date"]
                    )
                )

            elif N == 7 and fields == ["SENTIMENT_SCORE"]:

                return pd.DataFrame(
                    dict(
                        FI12345=[1.40, 1.40],
                        FI23456=[0.20, 0.20],
                    ),
                    index=pd.MultiIndex.from_product(
                        [["SENTIMENT_SCORE"], dates],
                        names=["Field", "Date"]
                    )
                )
            else:
                raise ValueError(f"unexpected parameter combination: {N}, {fields}")

        mock_get_brain_bsi_reindexed_like.side_effect = _mock_get_brain_bsi_reindexed_like

        array = loader.load_adjusted_array(
            domain,
            columns,
            dates,
            sids,
            mask
        )

        self.assertEqual(len(mock_get_brain_bsi_reindexed_like.mock_calls), 2)
        expected_calls = [
            (1, {"SENTIMENT_SCORE", "VOLUME"}),
            (7, {"SENTIMENT_SCORE"})
        ]
        for mock_call in mock_get_brain_bsi_reindexed_like.mock_calls:
            _, args, kwargs = mock_call
            N = kwargs["N"]
            fields = set(kwargs["fields"])
            expected_calls.remove((N, fields))

        self.assertEqual(len(expected_calls), 0 )

        np.testing.assert_array_equal(
            array[bsi_1_sentiment].data,
            np.array([[1.35, 0.10], [1.35, 0.10]]))
        np.testing.assert_array_equal(
            array[bsi_1_volume].data,
            np.array([[5e10, 1e10], [5e10, 1e10]]))
        np.testing.assert_array_equal(
            array[bsi_7_sentiment].data,
            np.array([[1.40, 0.20], [1.40, 0.20]]))

    def test_no_data(self):
        """
        Tests handling when get_brain_bsi_reindexed_like returns no data.
        """
        bsi_1 = brain.BSI.slice(1)

        bsi_1_sentiment = bsi_1.SENTIMENT_SCORE
        bsi_1_volume = bsi_1.VOLUME

        zipline_sids_to_real_sids = {
            1: "FI12345",
            2: "FI23456"
        }
        loader = BSIPipelineLoader(zipline_sids_to_real_sids)
        domain = bsi_1_sentiment.domain
        columns = [bsi_1_sentiment, bsi_1_volume]
        dates = pd.date_range(start="2022-07-25", periods=2)
        sids= pd.Index([1, 2])
        mask = np.array([[True, True], [True, True]])


        def mock_get_brain_bsi_reindexed_like(
            reindex_like,
            fields=None,
            N=1):

            raise NoFundamentalData("no data match the query parameters")

        with patch('zipline.pipeline.loaders.brain.get_brain_bsi_reindexed_like', new=mock_get_brain_bsi_reindexed_like):

            array = loader.load_adjusted_array(
                domain,
                columns,
                dates,
                sids,
                mask
            )

        np.testing.assert_array_equal(
            array[bsi_1_sentiment].data,
            np.array([[np.nan, np.nan], [np.nan, np.nan]]))
        np.testing.assert_array_equal(
            array[bsi_1_volume].data,
            np.array([[np.nan, np.nan], [np.nan, np.nan]]))

class BLMCFLoaderTestCase(unittest.TestCase):

    @patch("zipline.pipeline.loaders.brain.get_brain_blmcf_reindexed_like")
    def test_query_by_column_groups(self,
                                    mock_get_brain_blmcf_reindexed_like):
        """
        Tests that the BLMCFPipelineLoader appropriately groups columns
        for querying get_brain_blmcf_reindexed_like.
        """
        blmcf = brain.BLMCF.slice(None)
        blmcf_10k = brain.BLMCF.slice('10-K')

        blmcf_sentiment = blmcf.SENTIMENT
        blmcf_score_litigious = blmcf.SCORE_LITIGIOUS
        blmcf_10k_sentiment = blmcf_10k.SENTIMENT
        blmcf_last_report_date = blmcf.LAST_REPORT_DATE
        blmcf_last_report_category = blmcf.LAST_REPORT_CATEGORY

        zipline_sids_to_real_sids = {
            1: "FI12345",
            2: "FI23456"
        }
        loader = BLMCFPipelineLoader(zipline_sids_to_real_sids)
        domain = blmcf.domain
        columns = [blmcf_sentiment, blmcf_score_litigious, blmcf_10k_sentiment, blmcf_last_report_date, blmcf_last_report_category]
        dates = pd.date_range(start="2022-07-25", periods=2)
        sids= pd.Index([1, 2])
        mask = np.array([[True, True], [True, True]])


        def _mock_get_brain_blmcf_reindexed_like(
            reindex_like,
            fields=None,
            report_category=None):

            if report_category is None and set(fields) == {"SENTIMENT", "SCORE_LITIGIOUS"}:

                return pd.DataFrame(
                    dict(
                        FI12345=[1.35, 1.35, 0.5, 0.5],
                        FI23456=[0.10, 0.10, 0.6, 0.6],
                    ),
                    index=pd.MultiIndex.from_product(
                        [["SENTIMENT", "SCORE_LITIGIOUS"], dates],
                        names=["Field", "Date"]
                    )
                )

            elif report_category == "10-K" and fields == ["SENTIMENT"]:

                return pd.DataFrame(
                    dict(
                        FI12345=[1.40, 1.40],
                        FI23456=[0.20, 0.20],
                    ),
                    index=pd.MultiIndex.from_product(
                        [["SENTIMENT"], dates],
                        names=["Field", "Date"]
                    )
                )
            elif report_category == None and fields == ["LAST_REPORT_DATE"]:

                return pd.DataFrame(
                    dict(
                        FI12345=pd.to_datetime(["2022-06-30", "2022-06-30"]),
                        FI23456=pd.to_datetime(["2022-06-20", "2022-06-20"]),
                    ),
                    index=pd.MultiIndex.from_product(
                        [["LAST_REPORT_DATE"], dates],
                        names=["Field", "Date"]
                    )
                )
            elif report_category == None and fields == ["LAST_REPORT_CATEGORY"]:

                return pd.DataFrame(
                    dict(
                        FI12345=["10-Q", "10-Q"],
                        FI23456=["10-K", "10-K"],
                    ),
                    index=pd.MultiIndex.from_product(
                        [["LAST_REPORT_CATEGORY"], dates],
                        names=["Field", "Date"]
                    )
                )
            else:
                raise ValueError(f"unexpected parameter combination: {report_category}, {fields}")

        mock_get_brain_blmcf_reindexed_like.side_effect = _mock_get_brain_blmcf_reindexed_like

        array = loader.load_adjusted_array(
            domain,
            columns,
            dates,
            sids,
            mask
        )

        self.assertEqual(len(mock_get_brain_blmcf_reindexed_like.mock_calls), 4)
        expected_calls = [
            (None, {"SENTIMENT", "SCORE_LITIGIOUS"}),
            (None, {"LAST_REPORT_DATE"}),
            (None, {"LAST_REPORT_CATEGORY"}),
            ("10-K", {"SENTIMENT"})
        ]
        for mock_call in mock_get_brain_blmcf_reindexed_like.mock_calls:
            _, args, kwargs = mock_call
            report_category = kwargs["report_category"]
            fields = set(kwargs["fields"])
            expected_calls.remove((report_category, fields))

        self.assertEqual(len(expected_calls), 0)

        np.testing.assert_array_equal(
            array[blmcf_sentiment].data,
            np.array([[1.35, 0.10], [1.35, 0.10]]))
        np.testing.assert_array_equal(
            array[blmcf_score_litigious].data,
            np.array([[0.5, 0.6], [0.5, 0.6]]))
        np.testing.assert_array_equal(
            array[blmcf_10k_sentiment].data,
            np.array([[1.40, 0.20], [1.40, 0.20]]))
        np.testing.assert_array_equal(
            array[blmcf_last_report_category].data,
            np.array([["10-Q", "10-K"], ["10-Q", "10-K"]]))
        np.testing.assert_array_equal(
            array[blmcf_last_report_date].data,
            np.array([[np.datetime64("2022-06-30"), np.datetime64("2022-06-20")],
                      [np.datetime64("2022-06-30"), np.datetime64("2022-06-20")]]))

    def test_no_data(self):
        """
        Tests handling when get_brain_blmcf_reindexed_like returns no data.
        """
        blmcf = brain.BLMCF.slice(None)

        blmcf_sentiment = blmcf.SENTIMENT
        blmcf_last_report_date = blmcf.LAST_REPORT_DATE
        blmcf_last_report_category = blmcf.LAST_REPORT_CATEGORY

        zipline_sids_to_real_sids = {
            1: "FI12345",
            2: "FI23456"
        }
        loader = BLMCFPipelineLoader(zipline_sids_to_real_sids)
        domain = blmcf_sentiment.domain
        columns = [blmcf_sentiment, blmcf_last_report_date, blmcf_last_report_category]
        dates = pd.date_range(start="2022-07-25", periods=2)
        sids= pd.Index([1, 2])
        mask = np.array([[True, True], [True, True]])


        def mock_get_brain_blmcf_reindexed_like(
            reindex_like,
            fields=None,
            report_category=None):

            raise NoFundamentalData("no data match the query parameters")

        with patch('zipline.pipeline.loaders.brain.get_brain_blmcf_reindexed_like', new=mock_get_brain_blmcf_reindexed_like):

            array = loader.load_adjusted_array(
                domain,
                columns,
                dates,
                sids,
                mask
            )

        np.testing.assert_array_equal(
            array[blmcf_sentiment].data,
            np.array([[np.nan, np.nan], [np.nan, np.nan]]))
        np.testing.assert_array_equal(
            array[blmcf_last_report_date].data,
            np.array([[NaTD, NaTD], [NaTD, NaTD]]))
        self.assertEqual(
            array[blmcf_last_report_category].data.as_string_array().tolist(),
            [["", ""], ["", ""]])

class BLMECTLoaderTestCase(unittest.TestCase):

    @patch("zipline.pipeline.loaders.brain.get_brain_blmect_reindexed_like")
    def test_query_by_column_groups(self,
                                    mock_get_brain_blmect_reindexed_like):
        """
        Tests that the BLMECTPipelineLoader appropriately groups columns
        for querying get_brain_blmect_reindexed_like.
        """
        blmect = brain.BLMECT

        blmect_sentiment = blmect.MD_SENTIMENT
        blmect_score_litigious = blmect.MD_SCORE_LITIGIOUS
        blmect_last_transcript_date = blmect.LAST_TRANSCRIPT_DATE

        zipline_sids_to_real_sids = {
            1: "FI12345",
            2: "FI23456"
        }
        loader = BLMECTPipelineLoader(zipline_sids_to_real_sids)
        domain = blmect.domain
        columns = [blmect_sentiment, blmect_score_litigious, blmect_last_transcript_date]
        dates = pd.date_range(start="2022-07-25", periods=2)
        sids= pd.Index([1, 2])
        mask = np.array([[True, True], [True, True]])


        def _mock_get_brain_blmect_reindexed_like(
            reindex_like,
            fields=None):

            if set(fields) == {"MD_SENTIMENT", "MD_SCORE_LITIGIOUS"}:

                return pd.DataFrame(
                    dict(
                        FI12345=[1.35, 1.35, 0.5, 0.5],
                        FI23456=[0.10, 0.10, 0.6, 0.6],
                    ),
                    index=pd.MultiIndex.from_product(
                        [["MD_SENTIMENT", "MD_SCORE_LITIGIOUS"], dates],
                        names=["Field", "Date"]
                    )
                )

            elif fields == ["LAST_TRANSCRIPT_DATE"]:

                return pd.DataFrame(
                    dict(
                        FI12345=pd.to_datetime(["2022-06-30", "2022-06-30"]),
                        FI23456=pd.to_datetime(["2022-06-20", "2022-06-20"]),
                    ),
                    index=pd.MultiIndex.from_product(
                        [["LAST_TRANSCRIPT_DATE"], dates],
                        names=["Field", "Date"]
                    )
                )
            else:
                raise ValueError(f"unexpected parameter combination: {report_category}, {fields}")

        mock_get_brain_blmect_reindexed_like.side_effect = _mock_get_brain_blmect_reindexed_like

        array = loader.load_adjusted_array(
            domain,
            columns,
            dates,
            sids,
            mask
        )

        self.assertEqual(len(mock_get_brain_blmect_reindexed_like.mock_calls), 2)
        expected_calls = [
            ({"MD_SENTIMENT", "MD_SCORE_LITIGIOUS"},),
            ({"LAST_TRANSCRIPT_DATE"},),
        ]
        for mock_call in mock_get_brain_blmect_reindexed_like.mock_calls:
            _, args, kwargs = mock_call
            fields = set(kwargs["fields"])
            expected_calls.remove((fields,))

        self.assertEqual(len(expected_calls), 0)

        np.testing.assert_array_equal(
            array[blmect_sentiment].data,
            np.array([[1.35, 0.10], [1.35, 0.10]]))
        np.testing.assert_array_equal(
            array[blmect_score_litigious].data,
            np.array([[0.5, 0.6], [0.5, 0.6]]))
        np.testing.assert_array_equal(
            array[blmect_last_transcript_date].data,
            np.array([[np.datetime64("2022-06-30"), np.datetime64("2022-06-20")],
                      [np.datetime64("2022-06-30"), np.datetime64("2022-06-20")]]))

    def test_no_data(self):
        """
        Tests handling when get_brain_blmect_reindexed_like returns no data.
        """
        blmect = brain.BLMECT

        blmect_sentiment = blmect.MD_SENTIMENT
        blmect_last_transcript_date = blmect.LAST_TRANSCRIPT_DATE

        zipline_sids_to_real_sids = {
            1: "FI12345",
            2: "FI23456"
        }
        loader = BLMECTPipelineLoader(zipline_sids_to_real_sids)
        domain = blmect_sentiment.domain
        columns = [blmect_sentiment, blmect_last_transcript_date]
        dates = pd.date_range(start="2022-07-25", periods=2)
        sids= pd.Index([1, 2])
        mask = np.array([[True, True], [True, True]])


        def mock_get_brain_blmect_reindexed_like(
            reindex_like,
            fields=None):

            raise NoFundamentalData("no data match the query parameters")

        with patch('zipline.pipeline.loaders.brain.get_brain_blmect_reindexed_like', new=mock_get_brain_blmect_reindexed_like):

            array = loader.load_adjusted_array(
                domain,
                columns,
                dates,
                sids,
                mask
            )

        np.testing.assert_array_equal(
            array[blmect_sentiment].data,
            np.array([[np.nan, np.nan], [np.nan, np.nan]]))
        np.testing.assert_array_equal(
            array[blmect_last_transcript_date].data,
            np.array([[NaTD, NaTD], [NaTD, NaTD]]))
