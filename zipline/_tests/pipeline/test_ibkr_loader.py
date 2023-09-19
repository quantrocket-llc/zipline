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
from unittest import mock
from unittest.mock import patch
import pandas as pd
import numpy as np
from zipline.pipeline.data import ibkr
from zipline.pipeline.loaders.ibkr import (
    IBKRAggregateShortableSharesPipelineLoader,
    IBKRBorrowFeesPipelineLoader)
from quantrocket.fundamental import NoFundamentalData

class IBKRShortableSharesLoaderTestCase(unittest.TestCase):

    @patch("zipline.pipeline.loaders.ibkr.get_ibkr_shortable_shares_reindexed_like")
    def test_shortable_shares(self, mock_get_ibkr_shortable_shares_reindexed_like):
        """
        Tests loading data via get_ibkr_shortable_shares_reindexed_like.
        """
        last_qty = ibkr.ShortableShares.LastQuantity
        min_qty = ibkr.ShortableShares.MinQuantity

        zipline_sids_to_real_sids = {
            1: "FI12345",
            2: "FI23456"
        }
        loader = IBKRAggregateShortableSharesPipelineLoader(zipline_sids_to_real_sids)
        domain = last_qty.domain
        columns = [last_qty, min_qty]
        dates = pd.date_range(start="2022-07-25", periods=2)
        sids= pd.Index([1, 2])
        mask = np.array([[True, True], [True, True]])


        def _mock_get_ibkr_shortable_shares_reindexed_like(
            reindex_like,
            aggregate=False,
            time=None,
            fields=None,
            shift=0):

            return pd.DataFrame(
                dict(
                    FI12345=[10100, 11000, 5100, 6100],
                    FI23456=[900, 800, 400, 500],
                ),
                index=pd.MultiIndex.from_product(
                    [["LastQuantity", "MinQuantity"], dates],
                    names=["Field", "Date"]
                )
            )

        mock_get_ibkr_shortable_shares_reindexed_like.side_effect = _mock_get_ibkr_shortable_shares_reindexed_like

        array = loader.load_adjusted_array(
            domain,
            columns,
            dates,
            sids,
            mask
        )

        self.assertEqual(len(mock_get_ibkr_shortable_shares_reindexed_like.mock_calls), 1)
        _, args, kwargs = mock_get_ibkr_shortable_shares_reindexed_like.mock_calls[0]
        self.assertListEqual(list(kwargs), ["aggregate", "fields", "shift"])
        self.assertEqual(kwargs["shift"], 1)
        self.assertTrue(kwargs["aggregate"])
        self.assertListEqual(kwargs["fields"], ["LastQuantity", "MinQuantity"])

        np.testing.assert_array_equal(
            array[last_qty].data,
            np.array([[10100, 900], [11000, 800]]))
        np.testing.assert_array_equal(
            array[min_qty].data,
            np.array([[5100, 400], [6100, 500]]))

    def test_no_data(self):
        """
        Tests handling when get_ibkr_shortable_shares_reindexed_like returns no data.
        """
        last_qty = ibkr.ShortableShares.LastQuantity
        min_qty = ibkr.ShortableShares.MinQuantity

        zipline_sids_to_real_sids = {
            1: "FI12345",
            2: "FI23456"
        }
        loader = IBKRAggregateShortableSharesPipelineLoader(zipline_sids_to_real_sids)
        domain = last_qty.domain
        columns = [last_qty, min_qty]
        dates = pd.date_range(start="2022-07-25", periods=2)
        sids= pd.Index([1, 2])
        mask = np.array([[True, True], [True, True]])


        def mock_get_ibkr_shortable_shares_reindexed_like(
            reindex_like,
            aggregate=False,
            time=None,
            fields=None,
            shift=0):

            raise NoFundamentalData("no shortable shares match the query parameters")

        with patch('zipline.pipeline.loaders.ibkr.get_ibkr_shortable_shares_reindexed_like', new=mock_get_ibkr_shortable_shares_reindexed_like):

            array = loader.load_adjusted_array(
                domain,
                columns,
                dates,
                sids,
                mask
            )

        np.testing.assert_array_equal(
            array[last_qty].data,
            np.array([[np.nan, np.nan], [np.nan, np.nan]]))
        np.testing.assert_array_equal(
            array[min_qty].data,
            np.array([[np.nan, np.nan], [np.nan, np.nan]]))

class IBKRBorrowFeesLoaderTestCase(unittest.TestCase):

    @patch("zipline.pipeline.loaders.ibkr.get_ibkr_borrow_fees_reindexed_like")
    def test_borrow_fees(self, mock_get_ibkr_borrow_fees_reindexed_like):
        """
        Tests loading data via get_ibkr_borrow_fees_reindexed_like.
        """
        fees = ibkr.BorrowFees.FeeRate

        zipline_sids_to_real_sids = {
            1: "FI12345",
            2: "FI23456"
        }
        loader = IBKRBorrowFeesPipelineLoader(zipline_sids_to_real_sids)
        domain = fees.domain
        columns = [fees]
        dates = pd.date_range(start="2022-07-25", periods=2)
        sids= pd.Index([1, 2])
        mask = np.array([[True, True], [True, True]])

        def _mock_get_ibkr_borrow_fees_reindexed_like(
            reindex_like,
            shift=0):

            return pd.DataFrame(
                dict(
                    FI12345=[0.25, 0.26],
                    FI23456=[20.25, 20.26],
                ),
                index=dates
            )

        mock_get_ibkr_borrow_fees_reindexed_like.side_effect = _mock_get_ibkr_borrow_fees_reindexed_like

        array = loader.load_adjusted_array(
            domain,
            columns,
            dates,
            sids,
            mask
        )

        self.assertEqual(len(mock_get_ibkr_borrow_fees_reindexed_like.mock_calls), 1)
        _, args, kwargs = mock_get_ibkr_borrow_fees_reindexed_like.mock_calls[0]
        self.assertListEqual(list(kwargs), ["shift"])
        self.assertEqual(kwargs["shift"], 1)

        np.testing.assert_array_equal(
            array[fees].data,
            np.array([[0.25, 20.25], [0.26, 20.26]]))

    def test_no_data(self):
        """
        Tests handling when get_ibkr_borrow_fees_reindexed_like returns no data.
        """
        fees = ibkr.BorrowFees.FeeRate

        zipline_sids_to_real_sids = {
            1: "FI12345",
            2: "FI23456"
        }
        loader = IBKRBorrowFeesPipelineLoader(zipline_sids_to_real_sids)
        domain = fees.domain
        columns = [fees]
        dates = pd.date_range(start="2022-07-25", periods=2)
        sids= pd.Index([1, 2])
        mask = np.array([[True, True], [True, True]])

        def mock_get_ibkr_borrow_fees_reindexed_like(
            reindex_like,
            shift=0):

            raise NoFundamentalData("no borrow fees match the query parameters")

        with patch('zipline.pipeline.loaders.ibkr.get_ibkr_borrow_fees_reindexed_like', new=mock_get_ibkr_borrow_fees_reindexed_like):

            array = loader.load_adjusted_array(
                domain,
                columns,
                dates,
                sids,
                mask
            )

        np.testing.assert_array_equal(
            array[fees].data,
            np.array([[np.nan, np.nan], [np.nan, np.nan]]))
