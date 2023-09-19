"""
Tests for zipline.pipeline.Pipeline
"""
from unittest import TestCase
import re

import inspect
import pandas as pd
from mock import patch

from zipline.pipeline import Factor, Filter, Pipeline
from zipline.pipeline.data import Column, DataSet, USEquityPricing
from zipline.pipeline.domain import (
    AmbiguousDomain,
    CA_EQUITIES,
    GENERIC,
    GB_EQUITIES,
    US_EQUITIES,
)
from zipline.pipeline.graph import display_graph
from zipline.utils.numpy_utils import float64_dtype
from zipline.pipeline.filters import (
    StaticAssets,
    StaticSids,
    StaticUniverse,
    SingleAsset
)
import zipline._testing.fixtures as zf
from zipline.pipeline.data.master import SecuritiesMaster

class SomeFactor(Factor):
    dtype = float64_dtype
    window_length = 5
    inputs = [USEquityPricing.close, USEquityPricing.high]


class SomeOtherFactor(Factor):
    dtype = float64_dtype
    window_length = 5
    inputs = [USEquityPricing.close, USEquityPricing.high]


class SomeFilter(Filter):
    window_length = 5
    inputs = [USEquityPricing.close, USEquityPricing.high]


class SomeOtherFilter(Filter):
    window_length = 5
    inputs = [USEquityPricing.close, USEquityPricing.high]


class PipelineTestCase(TestCase):

    def test_construction(self):
        p0 = Pipeline()
        self.assertEqual(p0.columns, {})
        self.assertIs(p0.screen, None)

        columns = {'f': SomeFactor()}
        p1 = Pipeline(columns=columns)
        self.assertEqual(p1.columns, columns)

        screen = SomeFilter()
        p2 = Pipeline(screen=screen)
        self.assertEqual(p2.columns, {})
        self.assertEqual(p2.screen, screen)

        p3 = Pipeline(columns=columns, screen=screen)
        self.assertEqual(p3.columns, columns)
        self.assertEqual(p3.screen, screen)

    def test_construction_bad_input_types(self):

        with self.assertRaises(TypeError):
            Pipeline(1)

        Pipeline({})

        with self.assertRaises(TypeError):
            Pipeline({}, 1)

        with self.assertRaises(TypeError):
            Pipeline({}, SomeFactor())

        with self.assertRaises(TypeError):
            Pipeline({'open': USEquityPricing.open})

        Pipeline({}, SomeFactor() > 5)

    def test_add(self):
        p = Pipeline()
        f = SomeFactor()

        p.add(f, 'f')
        self.assertEqual(p.columns, {'f': f})

        p.add(f > 5, 'g')
        self.assertEqual(p.columns, {'f': f, 'g': f > 5})

        with self.assertRaises(TypeError):
            p.add(f, 1)

        with self.assertRaises(TypeError):
            p.add(USEquityPricing.open, 'open')

    def test_overwrite(self):
        p = Pipeline()
        f = SomeFactor()
        other_f = SomeOtherFactor()

        p.add(f, 'f')
        self.assertEqual(p.columns, {'f': f})

        with self.assertRaises(KeyError) as e:
            p.add(other_f, 'f')
        [message] = e.exception.args
        self.assertEqual(message, "Column 'f' already exists.")

        p.add(other_f, 'f', overwrite=True)
        self.assertEqual(p.columns, {'f': other_f})

    def test_remove(self):
        f = SomeFactor()
        p = Pipeline(columns={'f': f})

        with self.assertRaises(KeyError) as e:
            p.remove('not_a_real_name')

        self.assertEqual(f, p.remove('f'))

        with self.assertRaises(KeyError) as e:
            p.remove('f')

        self.assertEqual(e.exception.args, ('f',))

    def test_set_screen(self):
        f, g = SomeFilter(), SomeOtherFilter()

        p = Pipeline()
        self.assertEqual(p.screen, None)

        p.set_screen(f)
        self.assertEqual(p.screen, f)

        with self.assertRaises(ValueError):
            p.set_screen(f)

        p.set_screen(g, overwrite=True)
        self.assertEqual(p.screen, g)

        with self.assertRaises(TypeError) as e:
            p.set_screen(f, g)

        message = e.exception.args[0]
        self.assertIn(
            "expected a value of type bool or int for argument 'overwrite'",
            message,
        )

    def test_show_graph(self):
        f = SomeFactor()
        p = Pipeline(columns={'f': SomeFactor()})

        # The real display_graph call shells out to GraphViz, which isn't a
        # requirement, so patch it out for testing.

        def mock_display_graph(g, format='svg', include_asset_exists=False):
            return (g, format, include_asset_exists)

        self.assertEqual(
            inspect.getfullargspec(display_graph),
            inspect.getfullargspec(mock_display_graph),
            msg="Mock signature doesn't match signature for display_graph."
        )

        patch_display_graph = patch(
            'zipline.pipeline.graph.display_graph',
            mock_display_graph,
        )

        with patch_display_graph:
            graph, format, include_asset_exists = p.show_graph()
            self.assertIs(graph.outputs['f'], f)
            # '' is a sentinel used for screen if it's not supplied.
            self.assertEqual(
                sorted(graph.outputs.keys()),
                ['f', graph.screen_name],
            )
            self.assertEqual(format, 'svg')
            self.assertEqual(include_asset_exists, False)

        with patch_display_graph:
            graph, format, include_asset_exists = p.show_graph(format='png')
            self.assertIs(graph.outputs['f'], f)
            # '' is a sentinel used for screen if it's not supplied.
            self.assertEqual(
                sorted(graph.outputs.keys()),
                ['f', graph.screen_name]
            )
            self.assertEqual(format, 'png')
            self.assertEqual(include_asset_exists, False)

        with patch_display_graph:
            graph, format, include_asset_exists = p.show_graph(format='jpeg')
            self.assertIs(graph.outputs['f'], f)
            self.assertEqual(
                sorted(graph.outputs.keys()),
                ['f', graph.screen_name]
            )
            self.assertEqual(format, 'jpeg')
            self.assertEqual(include_asset_exists, False)

        expected = (
            r".*\.show_graph\(\) expected a value in "
            r"\('svg', 'png', 'jpeg'\) for argument 'format', "
            r"but got 'fizzbuzz' instead."
        )

        with self.assertRaisesRegex(ValueError, expected):
            p.show_graph(format='fizzbuzz')

    def test_infer_domain_no_terms(self):
        self.assertEqual(Pipeline().domain(default=GENERIC), GENERIC)
        self.assertEqual(Pipeline().domain(default=US_EQUITIES), US_EQUITIES)

    def test_infer_domain_screen_only(self):
        class D(DataSet):
            c = Column(bool)

        filter_generic = D.c.latest
        filter_US = D.c.specialize(US_EQUITIES).latest
        filter_CA = D.c.specialize(CA_EQUITIES).latest

        self.assertEqual(
            Pipeline(screen=filter_generic).domain(default=GB_EQUITIES),
            GB_EQUITIES,
        )
        self.assertEqual(
            Pipeline(screen=filter_US).domain(default=GB_EQUITIES),
            US_EQUITIES,
        )
        self.assertEqual(
            Pipeline(screen=filter_CA).domain(default=GB_EQUITIES),
            CA_EQUITIES,
        )

    def test_infer_domain_outputs(self):
        class D(DataSet):
            c = Column(float)

        D_US = D.specialize(US_EQUITIES)
        D_CA = D.specialize(CA_EQUITIES)

        result = Pipeline({"f": D_US.c.latest}).domain(default=GB_EQUITIES)
        expected = US_EQUITIES
        self.assertEqual(result, expected)

        result = Pipeline({"f": D_CA.c.latest}).domain(default=GB_EQUITIES)
        expected = CA_EQUITIES
        self.assertEqual(result, expected)

    def test_conflict_between_outputs(self):
        class D(DataSet):
            c = Column(float)

        D_US = D.specialize(US_EQUITIES)
        D_CA = D.specialize(CA_EQUITIES)

        pipe = Pipeline({"f": D_US.c.latest, "g": D_CA.c.latest})
        with self.assertRaises(AmbiguousDomain) as e:
            pipe.domain(default=GENERIC)

        self.assertEqual(e.exception.domains, [CA_EQUITIES, US_EQUITIES])

    def test_conflict_between_output_and_screen(self):
        class D(DataSet):
            c = Column(float)
            b = Column(bool)

        D_US = D.specialize(US_EQUITIES)
        D_CA = D.specialize(CA_EQUITIES)

        pipe = Pipeline({"f": D_US.c.latest}, screen=D_CA.b.latest)
        with self.assertRaises(AmbiguousDomain) as e:
            pipe.domain(default=GENERIC)

        self.assertEqual(e.exception.domains, [CA_EQUITIES, US_EQUITIES])

class PrescreenTestCase(zf.WithAssetFinder, zf.ZiplineTestCase):

    def assert_prescreen_dict_equal(self, a, b):
        """
        Assert that two prescreen dicts are equal.
        """
        self.assertEqual(a.keys(), b.keys())
        for key in a:
            if key == "fields":
                self.assertEqual(len(a[key]), len(b[key]))
                for a_field, b_field in zip(a[key], b[key]):
                    self.assertEqual(a_field.keys(), b_field.keys())
                    self.assertEqual(set(a_field.keys()), set(["field", "op", "negate", "values"]))
                    self.assertEqual(a_field["field"], b_field["field"])
                    self.assertEqual(a_field["op"], b_field["op"])
                    self.assertEqual(a_field["negate"], b_field["negate"])
                    if isinstance(a_field["values"], list):
                        self.assertSetEqual(set(a_field["values"]), set(b_field["values"]))
                    else:
                        self.assertEqual(a_field["values"], b_field["values"])
            else:
                self.assertSetEqual(set(a[key]), set(b[key]))

    def test_static_assets(self):
        """
        Tests that static asset screens are converted to prescreens.
        """
        assets = self.asset_finder.retrieve_all([65, 66])
        pipe = Pipeline(
            columns={'f': SomeFactor()},
            screen=StaticAssets(assets),
        )
        self.assertIsNone(pipe.screen)
        self.assert_prescreen_dict_equal(
            pipe._prescreen,
            {"sids": [65, 66]}
        )

    def test_single_asset(self):
        """
        Tests that single asset screens are converted to prescreens.
        """
        asset = self.asset_finder.retrieve_asset(66)
        pipe = Pipeline(
            columns={'f': SomeFactor()},
            screen=SingleAsset(asset),
        )
        self.assertIsNone(pipe.screen)
        self.assert_prescreen_dict_equal(
            pipe._prescreen,
            {"sids": [66]}
        )

    def test_static_sids(self):
        """
        Tests that static sids screens are converted to prescreens.
        """
        pipe = Pipeline(
            columns={'f': SomeFactor()},
            screen=StaticSids(['66', '67']),
        )
        self.assertIsNone(pipe.screen)
        self.assert_prescreen_dict_equal(
            pipe._prescreen,
            {"real_sids": ["66", "67"]}
        )

    @patch("zipline.pipeline.filters.filter.get_securities")
    def test_static_universe(self, mock_get_securities):
        """
        Tests that static universe screens are converted to prescreens.
        """
        mock_get_securities.return_value = pd.DataFrame(index=['65', '67'])
        pipe = Pipeline(
            columns={'f': SomeFactor()},
            screen=StaticUniverse('test-universe'),
        )
        self.assertIsNone(pipe.screen)
        self.assert_prescreen_dict_equal(
            pipe._prescreen,
            {"real_sids": ["65", "67"]}
        )

    def test_securities_master(self):
        """
        Tests that securities master screens are converted to prescreens.
        """
        pipe = Pipeline(
            columns={'f': SomeFactor()},
            screen=SecuritiesMaster.SecType.latest.eq('STK'),
        )
        self.assertIsNone(pipe.screen)
        self.assert_prescreen_dict_equal(
            pipe._prescreen,
            {"fields": [{
                "field": "SecType",
                "op": "eq",
                "negate": False,
                "values": ["STK"]
            }]})

        pipe = Pipeline(
            columns={'f': SomeFactor()},
            screen=~SecuritiesMaster.SecType.latest.eq('STK'),
        )
        self.assertIsNone(pipe.screen)
        self.assert_prescreen_dict_equal(
            pipe._prescreen,
            {"fields": [{
                "field": "SecType",
                "op": "eq",
                "negate": True,
                "values": ["STK"]
            }]})

        pipe = Pipeline(
            columns={'f': SomeFactor()},
            screen=SecuritiesMaster.Etf.latest,
        )
        self.assertIsNone(pipe.screen)
        self.assert_prescreen_dict_equal(
            pipe._prescreen,
            {"fields": [{
                "field": "Etf",
                "op": "eq",
                "negate": False,
                "values": [True]
            }]})

        pipe = Pipeline(
            columns={'f': SomeFactor()},
            screen=~SecuritiesMaster.Etf.latest,
        )
        self.assertIsNone(pipe.screen)
        self.assert_prescreen_dict_equal(
            pipe._prescreen,
            {"fields": [{
                "field": "Etf",
                "op": "eq",
                "negate": True,
                "values": [True]
            }]})

        pipe = Pipeline(
            columns={'f': SomeFactor()},
            screen=SecuritiesMaster.sharadar_Sector.latest != "Energy",
        )
        self.assertIsNone(pipe.screen)
        self.assert_prescreen_dict_equal(
            pipe._prescreen,
            {"fields": [{
                "field": "sharadar_Sector",
                "op": "eq",
                "negate": True,
                "values": ["Energy"]
            }]})

        pipe = Pipeline(
            columns={'f': SomeFactor()},
            screen=SecuritiesMaster.sharadar_Sector.latest.isin(["Energy", "Technology"]),
        )
        self.assertIsNone(pipe.screen)
        self.assert_prescreen_dict_equal(
            pipe._prescreen,
            {"fields": [{
                "field": "sharadar_Sector",
                "op": "eq",
                "negate": False,
                "values": ["Energy", "Technology"]
            }]})

        pipe = Pipeline(
            columns={'f': SomeFactor()},
            screen=~SecuritiesMaster.sharadar_Sector.latest.isin(["Energy", "Technology"]),
        )
        self.assertIsNone(pipe.screen)
        self.assert_prescreen_dict_equal(
            pipe._prescreen,
            {"fields": [{
                "field": "sharadar_Sector",
                "op": "eq",
                "negate": True,
                "values": ["Energy", "Technology"]
            }]})

        pipe = Pipeline(
            columns={'f': SomeFactor()},
            screen=SecuritiesMaster.sharadar_Category.latest.has_substring("Domestic"),
        )
        self.assertIsNone(pipe.screen)
        self.assert_prescreen_dict_equal(
            pipe._prescreen,
            {"fields": [{
                "field": "sharadar_Category",
                "op": "contains",
                "negate": False,
                "values": "Domestic"
            }]})

        pipe = Pipeline(
            columns={'f': SomeFactor()},
            screen=SecuritiesMaster.Symbol.latest.startswith("A"),
        )
        self.assertIsNone(pipe.screen)
        self.assert_prescreen_dict_equal(
            pipe._prescreen,
            {"fields": [{
                "field": "Symbol",
                "op": "startswith",
                "negate": False,
                "values": "A"
            }]})

        pipe = Pipeline(
            columns={'f': SomeFactor()},
            screen=SecuritiesMaster.Symbol.latest.endswith("ZZZ"),
        )
        self.assertIsNone(pipe.screen)
        self.assert_prescreen_dict_equal(
            pipe._prescreen,
            {"fields": [{
                "field": "Symbol",
                "op": "endswith",
                "negate": False,
                "values": "ZZZ"
            }]})

        # Classifier.matches(..) with str
        pipe = Pipeline(
            columns={'f': SomeFactor()},
            screen=SecuritiesMaster.Symbol.latest.matches(r"[A-B]{2}"),
        )
        self.assertIsNone(pipe.screen)
        self.assert_prescreen_dict_equal(
            pipe._prescreen,
            {"fields": [{
                "field": "Symbol",
                "op": "match",
                "negate": False,
                "values": "[A-B]{2}"
            }]})

        # Classifier.matches(..) with regex
        pipe = Pipeline(
            columns={'f': SomeFactor()},
            screen=SecuritiesMaster.Symbol.latest.matches(re.compile(r"[A-B]{2}")),
        )
        self.assertIsNone(pipe.screen)
        self.assert_prescreen_dict_equal(
            pipe._prescreen,
            {"fields": [{
                "field": "Symbol",
                "op": "match",
                "negate": False,
                "values": re.compile(r"[A-B]{2}")
            }]})

        # isnull on object dtype
        pipe = Pipeline(
            columns={'f': SomeFactor()},
            screen=SecuritiesMaster.alpaca_AssetId.latest.isnull()
        )
        self.assertIsNone(pipe.screen)
        self.assert_prescreen_dict_equal(
            pipe._prescreen,
            {"fields": [{
                "field": "alpaca_AssetId",
                "op": "isnull",
                "negate": False,
                "values": [True]
            }]})

        # notnull on object dtype
        pipe = Pipeline(
            columns={'f': SomeFactor()},
            screen=SecuritiesMaster.alpaca_AssetId.latest.notnull()
        )
        self.assertIsNone(pipe.screen)
        self.assert_prescreen_dict_equal(
            pipe._prescreen,
            {"fields": [{
                "field": "alpaca_AssetId",
                "op": "isnull",
                "negate": True,
                "values": [True]
            }]})

        # isnull on float dtype
        pipe = Pipeline(
            columns={'f': SomeFactor()},
            screen=SecuritiesMaster.ibkr_ConId.latest.isnull()
        )
        self.assertIsNone(pipe.screen)
        self.assert_prescreen_dict_equal(
            pipe._prescreen,
            {"fields": [{
                "field": "ibkr_ConId",
                "op": "isnull",
                "negate": False,
                "values": [True]
            }]})

        # notnull on object dtype
        pipe = Pipeline(
            columns={'f': SomeFactor()},
            screen=SecuritiesMaster.ibkr_ConId.latest.notnull()
        )
        self.assertIsNone(pipe.screen)
        self.assert_prescreen_dict_equal(
            pipe._prescreen,
            {"fields": [{
                "field": "ibkr_ConId",
                "op": "isnull",
                "negate": True,
                "values": [True]
            }]})

    def test_ANDed_securities_master(self):
        """
        Tests that ANDed securities master screens are converted to prescreens.
        """
        pipe = Pipeline(
            columns={'f': SomeFactor()},
            screen=(
            SecuritiesMaster.sharadar_Category.latest.has_substring("Domestic")
            & (SecuritiesMaster.sharadar_Sector.latest != "Energy")),
        )
        self.assertIsNone(pipe.screen)
        self.assert_prescreen_dict_equal(
            pipe._prescreen,
            {"fields": [
                {
                    "field": "sharadar_Category",
                    "op": "contains",
                    "negate": False,
                    "values": "Domestic"
                },
                {
                    "field": "sharadar_Sector",
                    "op": "eq",
                    "negate": True,
                    "values": ["Energy"]
                },
            ]})

        pipe = Pipeline(
            columns={'f': SomeFactor()},
            screen=(
            SecuritiesMaster.Etf.latest
            & SecuritiesMaster.Symbol.latest.isin(["MDY", "SPY"])
            & (SecuritiesMaster.Exchange.latest != "NYSE")),
        )
        self.assertIsNone(pipe.screen)
        self.assert_prescreen_dict_equal(
            pipe._prescreen,
            {"fields": [
                {
                    "field": "Etf",
                    "op": "eq",
                    "negate": False,
                    "values": [True]
                },
                {
                    "field": "Symbol",
                    "op": "eq",
                    "negate": False,
                    "values": ["MDY", "SPY"]
                },
                {
                    "field": "Exchange",
                    "op": "eq",
                    "negate": True,
                    "values": ["NYSE"]
                },
            ]})

    def test_not_prescreen(self):
        """
        Tests that prescreens aren't created for unsupported screens.
        """

        # non securities master screens are not supported
        pipe = Pipeline(
            columns={'f': SomeFactor()},
            screen=SomeFilter(),
        )
        self.assertIsNotNone(pipe.screen)
        self.assertIsNone(pipe._prescreen)

        # ANDed securities master and non securities master screens are not supported
        pipe = Pipeline(
            columns={'f': SomeFactor()},
            screen=(
            SecuritiesMaster.Etf.latest & SomeFilter()),
        )
        self.assertIsNotNone(pipe.screen)
        self.assertIsNone(pipe._prescreen)

        # ORed securities master screens are not supported
        pipe = Pipeline(
            columns={'f': SomeFactor()},
            screen=(
            SecuritiesMaster.Etf.latest | SecuritiesMaster.Exchange.latest.eq("NYSE")),
        )
        self.assertIsNotNone(pipe.screen)
        self.assertIsNone(pipe._prescreen)

        # using fillna on a securities master screen is not supported
        pipe = Pipeline(
            columns={'f': SomeFactor()},
            screen=(
                SecuritiesMaster.Symbol.latest.fillna("A").eq("A")),
        )
        self.assertIsNotNone(pipe.screen)
        self.assertIsNone(pipe._prescreen)
