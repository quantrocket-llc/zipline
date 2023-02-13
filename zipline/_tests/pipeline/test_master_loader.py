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
from zipline.pipeline.data import master
from zipline.pipeline.loaders.master import SecuritiesMasterPipelineLoader

class SecuritiesMasterLoaderTestCase(unittest.TestCase):

    @patch("zipline.pipeline.loaders.master.get_securities_reindexed_like")
    def test_load_securities_master(self, mock_get_securities_reindexed_like):
        """
        Tests loading data via get_securities_reindexed_like.
        """
        sid = master.SecuritiesMaster.Sid
        symbol = master.SecuritiesMaster.Symbol

        zipline_sids_to_real_sids = {
            1: "FI12345",
            2: "FI23456"
        }
        loader = SecuritiesMasterPipelineLoader(zipline_sids_to_real_sids)
        domain = sid.domain
        columns = [sid, symbol]
        dates = pd.date_range(start="2022-07-25", periods=2)
        sids= pd.Int64Index([1, 2])
        mask = np.array([[True, True], [True, True]])


        def _mock_get_securities_reindexed_like(
            reindex_like,
            fields=None,
            ):

            return pd.DataFrame(
                dict(
                    FI12345=["FI12345", "FI12345", "ABC", "ABC"],
                    FI23456=["FI23456", "FI23456", "DEF", "DEF"],
                ),
                index=pd.MultiIndex.from_product(
                    [["Sid", "Symbol"], dates],
                    names=["Field", "Date"]
                )
            )

        mock_get_securities_reindexed_like.side_effect = _mock_get_securities_reindexed_like

        array = loader.load_adjusted_array(
            domain,
            columns,
            dates,
            sids,
            mask
        )

        self.assertEqual(len(mock_get_securities_reindexed_like.mock_calls), 1)
        _, args, kwargs = mock_get_securities_reindexed_like.mock_calls[0]
        self.assertListEqual(list(kwargs), ["fields"])
        self.assertListEqual(kwargs["fields"], ["Sid", "Symbol"])

        np.testing.assert_array_equal(
            array[sid].data,
            np.array([["FI12345", "FI23456"], ["FI12345", "FI23456"]]))
        np.testing.assert_array_equal(
            array[symbol].data,
            np.array([["ABC", "DEF"], ["ABC", "DEF"]]))

    def test_load_real_sid_only(self):
        """
        Tests loading only the Sid column, which shouldn't need to hit
        get_securities_reindexed_like (and thus mock isn't needed).
        """
        sid = master.SecuritiesMaster.Sid

        zipline_sids_to_real_sids = {
            1: "FI12345",
            2: "FI23456"
        }
        loader = SecuritiesMasterPipelineLoader(zipline_sids_to_real_sids)
        domain = sid.domain
        columns = [sid]
        dates = pd.date_range(start="2022-07-25", periods=2)
        sids= pd.Int64Index([1, 2])
        mask = np.array([[True, True], [True, True]])

        array = loader.load_adjusted_array(
            domain,
            columns,
            dates,
            sids,
            mask
        )

        np.testing.assert_array_equal(
            array[sid].data,
            np.array([["FI12345", "FI23456"], ["FI12345", "FI23456"]]))
