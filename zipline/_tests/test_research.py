# Copyright 2023 QuantRocket LLC - All Rights Reserved
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
from zipline.pipeline import Pipeline
from zipline.research import (
    use_bundle,
    get_forward_returns,
    run_pipeline,
    get_data,
    sid,
    symbol,
    continuous_future,
)
from zipline.research.exceptions import ValidationError
import pandas as pd
import numpy as np


class UseBundleTestCase(unittest.TestCase):

    @patch("zipline.research.pipeline.load_extensions")
    @patch("zipline.research.pipeline.get_default_bundle")
    @patch("zipline.research.bardata.load_extensions")
    @patch("zipline.research.bardata.get_default_bundle")
    @patch("zipline.research.continuous_future_module.load_extensions")
    @patch("zipline.research.continuous_future_module.get_default_bundle")
    @patch("zipline.research.sid_module.load_extensions")
    @patch("zipline.research.sid_module.get_default_bundle")
    def test_use_bundle(
        self,
        mock_sid_get_default_bundle,
        mock_sid_load_extensions,
        mock_contfut_get_default_bundle,
        mock_contfut_load_extensions,
        mock_bardata_get_default_bundle,
        mock_bardata_load_extensions,
        mock_pipeline_get_default_bundle,
        mock_pipeline_load_extensions,
        ):
        """
        Tests that sid() and symbol() use the default bundle if no bundle is specified
        and use_bundle() has not been called.
        """
        # First, test with no use_bundle call, which should use the default bundle

        # sid() and symbol()
        mock_sid_get_default_bundle.return_value = {"default_bundle": "usstock-1min"}
        with self.assertRaises(Exception):
            sid("FIBBG000B9XRY4")
        mock_sid_load_extensions.assert_called_once_with(code="usstock-1min")

        with self.assertRaises(Exception):
            symbol("AAPL")

        self.assertEqual(mock_sid_load_extensions.call_count, 2)
        self.assertEqual(mock_sid_load_extensions.call_args_list[1][1]["code"], "usstock-1min")

        # continuous_future()
        mock_contfut_get_default_bundle.return_value = {"default_bundle": "usfutures-1min"}

        with self.assertRaises(Exception):
            continuous_future("CL")

        mock_contfut_load_extensions.assert_called_once_with(code="usfutures-1min")

        # get_data()
        mock_bardata_get_default_bundle.return_value = {"default_bundle": "usstock-1min"}

        with self.assertRaises(Exception):
            get_data("2018-01-01")

        mock_bardata_load_extensions.assert_called_once_with(code="usstock-1min")

        # run_pipeline() and get_forward_returns()
        mock_pipeline_get_default_bundle.return_value = {"default_bundle": "usstock-1min"}

        with self.assertRaises(Exception):
            run_pipeline(Pipeline(), "2018-01-01", "2018-01-01")

        mock_pipeline_load_extensions.assert_called_once_with(code="usstock-1min")

        with self.assertRaises(Exception):
            get_forward_returns(pd.Series([1]), periods=[1])

        self.assertEqual(mock_pipeline_load_extensions.call_count, 2)
        self.assertEqual(mock_pipeline_load_extensions.call_args_list[1][1]["code"], "usstock-1min")

        # now set a default bundle and make sure it is used
        use_bundle("my-bundle")

        # sid() and symbol()
        with self.assertRaises(Exception):
            sid("FIBBG000B9XRY4")

        self.assertEqual(mock_sid_load_extensions.call_count, 3)
        self.assertEqual(mock_sid_load_extensions.call_args_list[2][1]["code"], "my-bundle")

        with self.assertRaises(Exception):
            symbol("AAPL")

        self.assertEqual(mock_sid_load_extensions.call_count, 4)
        self.assertEqual(mock_sid_load_extensions.call_args_list[3][1]["code"], "my-bundle")

        # continuous_future()
        with self.assertRaises(Exception):
            continuous_future("CL")

        self.assertEqual(mock_contfut_load_extensions.call_count, 2)
        self.assertEqual(mock_contfut_load_extensions.call_args_list[1][1]["code"], "my-bundle")

        # get_data()
        with self.assertRaises(Exception):
            get_data("2018-01-01")

        self.assertEqual(mock_bardata_load_extensions.call_count, 2)
        self.assertEqual(mock_bardata_load_extensions.call_args_list[1][1]["code"], "my-bundle")

        # run_pipeline() and get_forward_returns()
        with self.assertRaises(Exception):
            run_pipeline(Pipeline(), "2018-01-01", "2018-01-01")

        self.assertEqual(mock_pipeline_load_extensions.call_count, 3)
        self.assertEqual(mock_pipeline_load_extensions.call_args_list[2][1]["code"], "my-bundle")

        with self.assertRaises(Exception):
            get_forward_returns(pd.Series([1]), periods=[1])

        self.assertEqual(mock_pipeline_load_extensions.call_count, 4)
        self.assertEqual(mock_pipeline_load_extensions.call_args_list[3][1]["code"], "my-bundle")

        # test that specifying a bundle overrides use_bundle()

        # sid() and symbol()
        with self.assertRaises(Exception):
            sid("FIBBG000B9XRY4", bundle="my-other-bundle")

        self.assertEqual(mock_sid_load_extensions.call_count, 5)
        self.assertEqual(mock_sid_load_extensions.call_args_list[4][1]["code"], "my-other-bundle")

        with self.assertRaises(Exception):
            symbol("AAPL", bundle="my-other-bundle")

        self.assertEqual(mock_sid_load_extensions.call_count, 6)
        self.assertEqual(mock_sid_load_extensions.call_args_list[5][1]["code"], "my-other-bundle")

        # continuous_future()
        with self.assertRaises(Exception):
            continuous_future("CL", bundle="my-other-bundle")

        self.assertEqual(mock_contfut_load_extensions.call_count, 3)
        self.assertEqual(mock_contfut_load_extensions.call_args_list[2][1]["code"], "my-other-bundle")

        # get_data()
        with self.assertRaises(Exception):
            get_data("2018-01-01", bundle="my-other-bundle")

        self.assertEqual(mock_bardata_load_extensions.call_count, 3)
        self.assertEqual(mock_bardata_load_extensions.call_args_list[2][1]["code"], "my-other-bundle")

        # run_pipeline() and get_forward_returns()
        with self.assertRaises(Exception):
            run_pipeline(Pipeline(), "2018-01-01", "2018-01-01", bundle="my-other-bundle")

        self.assertEqual(mock_pipeline_load_extensions.call_count, 5)
        self.assertEqual(mock_pipeline_load_extensions.call_args_list[4][1]["code"], "my-other-bundle")

        with self.assertRaises(Exception):
            get_forward_returns(pd.Series([1]), periods=[1], bundle="my-other-bundle")

        self.assertEqual(mock_pipeline_load_extensions.call_count, 6)
        self.assertEqual(mock_pipeline_load_extensions.call_args_list[5][1]["code"], "my-other-bundle")

    def test_no_such_bundle(self):
        """
        Test that ValidationError is raised when the bundle does not exist.
        """
        with self.assertRaises(ValidationError):
            use_bundle("no-such-bundle")
