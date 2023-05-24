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
from parameterized import parameterized
from zipline.pipeline import (
    periodic,
    sharadar,
    filters,
    EquityPricing)
from zipline.pipeline.factors import Latest

def OPMARGIN(period_offset=0, mask=None):
    fundamentals = sharadar.Fundamentals.slice(dimension="ART", period_offset=period_offset)
    return Latest(fundamentals.OPINC, mask=mask) / Latest(fundamentals.REVENUE, mask=mask)

class PeriodicTermsTestCase(unittest.TestCase):

    def test_window_length_must_be_greater_than_2(self):
        with self.assertRaises(ValueError) as cm:
            periodic.AllPeriodsIncreasing(
                sharadar.Fundamentals.slice('ART').DIVYIELD,
                window_length=0
            )

        self.assertEqual(str(cm.exception), "window_length must be 2 or greater")

        with self.assertRaises(ValueError) as cm:
            periodic.AllPeriodsDecreasing(
                sharadar.Fundamentals.slice('ART').DIVYIELD,
                window_length=-1
            )

        self.assertEqual(str(cm.exception), "window_length must be 2 or greater")

    def test_step_must_be_longer_than_window_length(self):
        with self.assertRaises(ValueError) as cm:
            periodic.AllPeriodsIncreasing(
                sharadar.Fundamentals.slice('ART').DIVYIELD,
                window_length=4,
                step=4
            )
        self.assertEqual(str(cm.exception), "window_length must be greater than step")

    def test_not_a_bound_column_or_incorrect_signature(self):
        with self.assertRaises(ValueError) as cm:
            periodic.AllPeriodsIncreasing(
                sharadar.Fundamentals.slice('ART').DIVYIELD.latest,
                window_length=4,
            )
        self.assertEqual(
            str(cm.exception),
            "expected a BoundColumn or callable but got Latest([Fundamentals.slice(dimension='ART', period_offset=0)<US>.DIVYIELD], 1). "
            "Hint: pass the column itself instead of column.latest.")

        with self.assertRaises(ValueError) as cm:
            periodic.AllPeriodsIncreasing(
                {},
                window_length=4,
            )
        self.assertEqual(
            str(cm.exception),
            "expected a BoundColumn or callable but got {}")

        with self.assertRaises(ValueError) as cm:
            periodic.AllPeriodsIncreasing(
                EquityPricing.close,
                window_length=4,
            )
        self.assertEqual(
            str(cm.exception),
            "Column must belong to a DataSet with a period_offset coordinate but got: EquityPricing.close::float64")

        with self.assertRaises(ValueError) as cm:
            periodic.AllPeriodsIncreasing(
                lambda foo, mask: None,
                window_length=4,
            )
        self.assertEqual(
            str(cm.exception),
            "<lambda> must have a period_offset parameter")

        with self.assertRaises(ValueError) as cm:
            periodic.AllPeriodsIncreasing(
                lambda period_offset: None,
                window_length=4,
            )
        self.assertEqual(
            str(cm.exception),
            "<lambda> must have a mask parameter")

    def test_periodic_cagr_periods_per_year_error_handling(self):

        with self.assertRaises(ValueError) as cm:
            periodic.PeriodicCAGR(
                lambda period_offset, mask: None,
                window_length=4,
            )
        self.assertEqual(
            str(cm.exception),
            "periods_per_year cannot be inferred and must be specified")

        with self.assertRaises(ValueError) as cm:
            periodic.PeriodicCAGR(
                sharadar.Fundamentals.slice('ART').DIVYIELD,
                window_length=3,
            )
        self.assertEqual(
            str(cm.exception),
            "window_length (3) must be greater than periods_per_year (4)")

    @parameterized.expand([
        ('ART', 4, None, None, None,
         ("NumExprFilter(expr='((x_0 > x_1) & (x_1 > x_2)) & (x_2 > x_3)', "
         "bindings={'x_0': Latest([Fundamentals.slice(dimension='ART', period_offset=0)<US>.DIVYIELD], 1), "
         "'x_1': Latest([Fundamentals.slice(dimension='ART', period_offset=-1)<US>.DIVYIELD], 1), "
         "'x_2': Latest([Fundamentals.slice(dimension='ART', period_offset=-2)<US>.DIVYIELD], 1), "
         "'x_3': Latest([Fundamentals.slice(dimension='ART', period_offset=-3)<US>.DIVYIELD], 1)})")
         ),
        ('ARQ', 16, 4, True, True,
         ("NumExprFilter(expr='((x_0 >= x_1) & (x_1 >= x_2)) & (x_2 >= x_3)', "
          "bindings={'x_0': Latest([Fundamentals.slice(dimension='ARQ', period_offset=0)<US>.DIVYIELD], 1), "
          "'x_1': Latest([Fundamentals.slice(dimension='ARQ', period_offset=-4)<US>.DIVYIELD], 1), "
          "'x_2': Latest([Fundamentals.slice(dimension='ARQ', period_offset=-8)<US>.DIVYIELD], 1), "
          "'x_3': Latest([Fundamentals.slice(dimension='ARQ', period_offset=-12)<US>.DIVYIELD], 1)})")
         ),
    ])
    def test_all_periods_increasing(
        self,
        dimension,
        window_length,
        step,
        allow_equal,
        use_mask,
        expected):

        kwargs = dict(
            window_length=window_length)
        if step is not None:
            kwargs["step"] = step
        if allow_equal is not None:
            kwargs["allow_equal"] = allow_equal
        if use_mask:
            kwargs["mask"] = filters.StaticSids(["A", "B"])

        term = periodic.AllPeriodsIncreasing(
            sharadar.Fundamentals.slice(dimension).DIVYIELD, **kwargs)

        self.assertEqual(repr(term), expected)

        for input in term.inputs:
            if use_mask:
                self.assertEqual(repr(input.mask), "StaticSids([SecuritiesMaster.Sid], 1)")
            else:
                self.assertEqual(repr(input.mask), "AssetExists()")

    def test_all_periods_increasing_callable(self):

        term = periodic.AllPeriodsIncreasing(
            OPMARGIN, window_length=3, allow_equal=True)

        self.assertEqual(
            repr(term),
            "NumExprFilter(expr='((x_0 / x_1) <= (x_2)) & ((x_0 / x_1) >= (x_3 / x_4))', "
            "bindings={'x_0': Latest([Fundamentals.slice(dimension='ART', period_offset=-1)<US>.OPINC], 1), "
            "'x_1': Latest([Fundamentals.slice(dimension='ART', period_offset=-1)<US>.REVENUE], 1), "
            "'x_2': Latest([NumExprFactor(...)], 1), "
            "'x_3': Latest([Fundamentals.slice(dimension='ART', period_offset=-2)<US>.OPINC], 1), "
            "'x_4': Latest([Fundamentals.slice(dimension='ART', period_offset=-2)<US>.REVENUE], 1)})"
        )

        # unpack x_2
        self.assertEqual(
            repr(term.bindings["x_2"].inputs),
            "(NumExprFactor(expr='x_0 / x_1', "
            "bindings={'x_0': Latest([Fundamentals.slice(dimension='ART', period_offset=0)<US>.OPINC], 1), "
            "'x_1': Latest([Fundamentals.slice(dimension='ART', period_offset=0)<US>.REVENUE], 1)}),)"
        )

        for input in term.inputs:
            self.assertEqual(repr(input.mask), "AssetExists()")

    @parameterized.expand([
        ('ART', 4, None, None, None,
         ("NumExprFilter(expr='((x_0 < x_1) & (x_1 < x_2)) & (x_2 < x_3)', "
          "bindings={'x_0': Latest([Fundamentals.slice(dimension='ART', period_offset=0)<US>.EPS], 1), "
          "'x_1': Latest([Fundamentals.slice(dimension='ART', period_offset=-1)<US>.EPS], 1), "
          "'x_2': Latest([Fundamentals.slice(dimension='ART', period_offset=-2)<US>.EPS], 1), "
          "'x_3': Latest([Fundamentals.slice(dimension='ART', period_offset=-3)<US>.EPS], 1)})")
         ),
        ('ARQ', 16, 4, True, True,
         ("NumExprFilter(expr='((x_0 <= x_1) & (x_1 <= x_2)) & (x_2 <= x_3)', "
          "bindings={'x_0': Latest([Fundamentals.slice(dimension='ARQ', period_offset=0)<US>.EPS], 1), "
          "'x_1': Latest([Fundamentals.slice(dimension='ARQ', period_offset=-4)<US>.EPS], 1), "
          "'x_2': Latest([Fundamentals.slice(dimension='ARQ', period_offset=-8)<US>.EPS], 1), "
          "'x_3': Latest([Fundamentals.slice(dimension='ARQ', period_offset=-12)<US>.EPS], 1)})")
         ),
    ])
    def test_all_periods_decreasing(
        self,
        dimension,
        window_length,
        step,
        allow_equal,
        use_mask,
        expected):

        kwargs = dict(
            window_length=window_length)
        if step is not None:
            kwargs["step"] = step
        if allow_equal is not None:
            kwargs["allow_equal"] = allow_equal
        if use_mask:
            kwargs["mask"] = filters.StaticSids(["A", "B"])

        term = periodic.AllPeriodsDecreasing(
            sharadar.Fundamentals.slice(dimension).EPS, **kwargs)

        self.assertEqual(repr(term), expected)

        for input in term.inputs:
            if use_mask:
                self.assertEqual(repr(input.mask), "StaticSids([SecuritiesMaster.Sid], 1)")
            else:
                self.assertEqual(repr(input.mask), "AssetExists()")

    def test_all_periods_decreasing_callable(self):

        term = periodic.AllPeriodsDecreasing(
            OPMARGIN, window_length=3, mask=filters.StaticSids(["A", "B"]))

        self.assertEqual(
            repr(term),
            "NumExprFilter(expr='((x_0 / x_1) > (x_2)) & ((x_0 / x_1) < (x_3 / x_4))', "
            "bindings={'x_0': Latest([Fundamentals.slice(dimension='ART', period_offset=-1)<US>.OPINC], 1), "
            "'x_1': Latest([Fundamentals.slice(dimension='ART', period_offset=-1)<US>.REVENUE], 1), "
            "'x_2': Latest([NumExprFactor(...)], 1), "
            "'x_3': Latest([Fundamentals.slice(dimension='ART', period_offset=-2)<US>.OPINC], 1), "
            "'x_4': Latest([Fundamentals.slice(dimension='ART', period_offset=-2)<US>.REVENUE], 1)})"
        )

        # unpack x_2
        self.assertEqual(
            repr(term.bindings["x_2"].inputs),
            "(NumExprFactor(expr='x_0 / x_1', "
            "bindings={'x_0': Latest([Fundamentals.slice(dimension='ART', period_offset=0)<US>.OPINC], 1), "
            "'x_1': Latest([Fundamentals.slice(dimension='ART', period_offset=0)<US>.REVENUE], 1)}),)"
        )

        for input in term.inputs:
            self.assertEqual(repr(input.mask), "StaticSids([SecuritiesMaster.Sid], 1)")

    @parameterized.expand([
        ('ART', 99, 2, None, None, None,
         ("NumExprFactor(expr='x_0 + x_1', "
          "bindings={'x_0': BooleanFactor([NumExprFilter(...)], 0), "
          "'x_1': BooleanFactor([NumExprFilter(...)], 0)})"),
          ("(NumExprFilter(expr='x_0 > (99.0)', "
           "bindings={'x_0': Latest([Fundamentals.slice(dimension='ART', period_offset=0)<US>.ASSETS], 1)}),)"),
           ("(NumExprFilter(expr='x_0 > (99.0)', "
            "bindings={'x_0': Latest([Fundamentals.slice(dimension='ART', period_offset=-1)<US>.ASSETS], 1)}),)"),
            ("NumExprFilter(expr='(x_0 + x_1) == (2.0)', "
             "bindings={'x_0': BooleanFactor([NumExprFilter(...)], 0), "
             "'x_1': BooleanFactor([NumExprFilter(...)], 0)})")
         ),
        ('ARQ', 88, 5, 4, True, True,
         ("NumExprFactor(expr='x_0 + x_1', "
          "bindings={'x_0': BooleanFactor([NumExprFilter(...)], 0), "
          "'x_1': BooleanFactor([NumExprFilter(...)], 0)})"),
          ("(NumExprFilter(expr='x_0 >= (88.0)', "
           "bindings={'x_0': Latest([Fundamentals.slice(dimension='ARQ', period_offset=0)<US>.ASSETS], 1)}),)"),
           ("(NumExprFilter(expr='x_0 >= (88.0)', "
            "bindings={'x_0': Latest([Fundamentals.slice(dimension='ARQ', period_offset=-4)<US>.ASSETS], 1)}),)"),
            ("NumExprFilter(expr='(x_0 + x_1) == (2.0)', "
             "bindings={'x_0': BooleanFactor([NumExprFilter(...)], 0), "
             "'x_1': BooleanFactor([NumExprFilter(...)], 0)})")
         ),
    ])
    def test_periods_above(
        self,
        dimension,
        value,
        window_length,
        step,
        allow_equal,
        use_mask,
        expected_count_periods_above,
        expected_x_0,
        expected_x_1,
        expected_all_periods_above):

        kwargs = dict(
            window_length=window_length)
        if step is not None:
            kwargs["step"] = step
        if allow_equal is not None:
            kwargs["allow_equal"] = allow_equal
        if use_mask:
            kwargs["mask"] = filters.StaticSids(["A", "B"])

        term = periodic.CountPeriodsAbove(
            sharadar.Fundamentals.slice(dimension).ASSETS, value, **kwargs)

        self.assertEqual(repr(term), expected_count_periods_above)
        self.assertEqual(repr(term.bindings["x_0"].inputs), expected_x_0)
        self.assertEqual(repr(term.bindings["x_1"].inputs), expected_x_1)

        for booleanfactor in term.inputs:
            for numexprfilter in booleanfactor.inputs:
                for latest in numexprfilter.inputs:
                    if use_mask:
                        self.assertEqual(repr(latest.mask), "StaticSids([SecuritiesMaster.Sid], 1)")
                    else:
                        self.assertEqual(repr(latest.mask), "AssetExists()")

        # repeat with AllPeriodsAbove
        term = periodic.AllPeriodsAbove(
            sharadar.Fundamentals.slice(dimension).ASSETS, value, **kwargs)

        self.assertEqual(repr(term), expected_all_periods_above)
        self.assertEqual(repr(term.bindings["x_0"].inputs), expected_x_0)
        self.assertEqual(repr(term.bindings["x_1"].inputs), expected_x_1)

        for booleanfactor in term.inputs:
            for numexprfilter in booleanfactor.inputs:
                for latest in numexprfilter.inputs:
                    if use_mask:
                        self.assertEqual(repr(latest.mask), "StaticSids([SecuritiesMaster.Sid], 1)")
                    else:
                        self.assertEqual(repr(latest.mask), "AssetExists()")

    def test_count_periods_above_callable(self):

        term = periodic.CountPeriodsAbove(
            OPMARGIN, 77, window_length=2, allow_equal=True,
            mask=filters.StaticSids(["A", "B"]))

        self.assertEqual(
            repr(term),
            "NumExprFactor(expr='x_0 + x_1', "
            "bindings={'x_0': BooleanFactor([NumExprFilter(...)], 0), "
            "'x_1': BooleanFactor([NumExprFilter(...)], 0)})"
        )

        # unpack x_0
        self.assertEqual(
            repr(term.bindings["x_0"].inputs),
            "(NumExprFilter(expr='x_0 >= (77.0)', "
            "bindings={'x_0': Latest([NumExprFactor(...)], 1)}),)"
        )

        # unpack x_0 > x_0
        self.assertEqual(
            repr(term.bindings["x_0"].inputs[0].bindings["x_0"].inputs),
            "(NumExprFactor(expr='x_0 / x_1', "
            "bindings={'x_0': Latest([Fundamentals.slice(dimension='ART', period_offset=0)<US>.OPINC], 1), "
            "'x_1': Latest([Fundamentals.slice(dimension='ART', period_offset=0)<US>.REVENUE], 1)}),)"
        )

        for input in term.bindings["x_0"].inputs[0].bindings.values():
            self.assertEqual(repr(input.mask), "StaticSids([SecuritiesMaster.Sid], 1)")

        # unpack x_1
        self.assertEqual(
            repr(term.bindings["x_1"].inputs),
            "(NumExprFilter(expr='(x_0 / x_1) >= (77.0)', "
            "bindings={'x_0': Latest([Fundamentals.slice(dimension='ART', period_offset=-1)<US>.OPINC], 1), "
            "'x_1': Latest([Fundamentals.slice(dimension='ART', period_offset=-1)<US>.REVENUE], 1)}),)"
        )

        for input in term.bindings["x_1"].inputs[0].bindings.values():
            self.assertEqual(repr(input.mask), "StaticSids([SecuritiesMaster.Sid], 1)")

    @parameterized.expand([
        ('ART', 99, 2, None, None, None,
         ("NumExprFactor(expr='x_0 + x_1', "
          "bindings={'x_0': BooleanFactor([NumExprFilter(...)], 0), "
          "'x_1': BooleanFactor([NumExprFilter(...)], 0)})"),
          ("(NumExprFilter(expr='x_0 < (99.0)', "
           "bindings={'x_0': Latest([Fundamentals.slice(dimension='ART', period_offset=0)<US>.ASSETS], 1)}),)"),
           ("(NumExprFilter(expr='x_0 < (99.0)', "
            "bindings={'x_0': Latest([Fundamentals.slice(dimension='ART', period_offset=-1)<US>.ASSETS], 1)}),)"),
            ("NumExprFilter(expr='(x_0 + x_1) == (2.0)', "
             "bindings={'x_0': BooleanFactor([NumExprFilter(...)], 0), "
             "'x_1': BooleanFactor([NumExprFilter(...)], 0)})")
         ),
        ('ARQ', 88, 5, 4, True, True,
         ("NumExprFactor(expr='x_0 + x_1', "
          "bindings={'x_0': BooleanFactor([NumExprFilter(...)], 0), "
          "'x_1': BooleanFactor([NumExprFilter(...)], 0)})"),
          ("(NumExprFilter(expr='x_0 <= (88.0)', "
           "bindings={'x_0': Latest([Fundamentals.slice(dimension='ARQ', period_offset=0)<US>.ASSETS], 1)}),)"),
           ("(NumExprFilter(expr='x_0 <= (88.0)', "
            "bindings={'x_0': Latest([Fundamentals.slice(dimension='ARQ', period_offset=-4)<US>.ASSETS], 1)}),)"),
            ("NumExprFilter(expr='(x_0 + x_1) == (2.0)', "
             "bindings={'x_0': BooleanFactor([NumExprFilter(...)], 0), "
             "'x_1': BooleanFactor([NumExprFilter(...)], 0)})")
         ),
    ])
    def test_periods_below(
        self,
        dimension,
        value,
        window_length,
        step,
        allow_equal,
        use_mask,
        expected_count_periods_below,
        expected_x_0,
        expected_x_1,
        expected_all_periods_below):

        kwargs = dict(
            window_length=window_length)
        if step is not None:
            kwargs["step"] = step
        if allow_equal is not None:
            kwargs["allow_equal"] = allow_equal
        if use_mask:
            kwargs["mask"] = filters.StaticSids(["A", "B"])

        term = periodic.CountPeriodsBelow(
            sharadar.Fundamentals.slice(dimension).ASSETS, value, **kwargs)

        self.assertEqual(repr(term), expected_count_periods_below)
        self.assertEqual(repr(term.bindings["x_0"].inputs), expected_x_0)
        self.assertEqual(repr(term.bindings["x_1"].inputs), expected_x_1)

        for booleanfactor in term.inputs:
            for numexprfilter in booleanfactor.inputs:
                for latest in numexprfilter.inputs:
                    if use_mask:
                        self.assertEqual(repr(latest.mask), "StaticSids([SecuritiesMaster.Sid], 1)")
                    else:
                        self.assertEqual(repr(latest.mask), "AssetExists()")

        # repeat with AllPeriodsBelow
        term = periodic.AllPeriodsBelow(
            sharadar.Fundamentals.slice(dimension).ASSETS, value, **kwargs)

        self.assertEqual(repr(term), expected_all_periods_below)
        self.assertEqual(repr(term.bindings["x_0"].inputs), expected_x_0)
        self.assertEqual(repr(term.bindings["x_1"].inputs), expected_x_1)

        for booleanfactor in term.inputs:
            for numexprfilter in booleanfactor.inputs:
                for latest in numexprfilter.inputs:
                    if use_mask:
                        self.assertEqual(repr(latest.mask), "StaticSids([SecuritiesMaster.Sid], 1)")
                    else:
                        self.assertEqual(repr(latest.mask), "AssetExists()")

    def test_count_periods_below_callable(self):

        term = periodic.CountPeriodsBelow(
            OPMARGIN, 77, window_length=2, allow_equal=True,
            mask=filters.StaticSids(["A", "B"]))

        self.assertEqual(
            repr(term),
            "NumExprFactor(expr='x_0 + x_1', "
            "bindings={'x_0': BooleanFactor([NumExprFilter(...)], 0), "
            "'x_1': BooleanFactor([NumExprFilter(...)], 0)})"
        )

        # unpack x_0
        self.assertEqual(
            repr(term.bindings["x_0"].inputs),
            "(NumExprFilter(expr='x_0 <= (77.0)', "
            "bindings={'x_0': Latest([NumExprFactor(...)], 1)}),)"
        )

        # unpack x_0 > x_0
        self.assertEqual(
            repr(term.bindings["x_0"].inputs[0].bindings["x_0"].inputs),
            "(NumExprFactor(expr='x_0 / x_1', "
            "bindings={'x_0': Latest([Fundamentals.slice(dimension='ART', period_offset=0)<US>.OPINC], 1), "
            "'x_1': Latest([Fundamentals.slice(dimension='ART', period_offset=0)<US>.REVENUE], 1)}),)"
        )

        for input in term.bindings["x_0"].inputs[0].bindings.values():
            self.assertEqual(repr(input.mask), "StaticSids([SecuritiesMaster.Sid], 1)")

        # unpack x_1
        self.assertEqual(
            repr(term.bindings["x_1"].inputs),
            "(NumExprFilter(expr='(x_0 / x_1) <= (77.0)', "
            "bindings={'x_0': Latest([Fundamentals.slice(dimension='ART', period_offset=-1)<US>.OPINC], 1), "
            "'x_1': Latest([Fundamentals.slice(dimension='ART', period_offset=-1)<US>.REVENUE], 1)}),)"
        )

        for input in term.bindings["x_1"].inputs[0].bindings.values():
            self.assertEqual(repr(input.mask), "StaticSids([SecuritiesMaster.Sid], 1)")

    @parameterized.expand([
        ('ART', 3, None, None,
         ("NumExprFilter(expr='(x_0 & x_1) & (x_2)', "
          "bindings={'x_0': NotNullFilter([Latest(...)], 0), "
          "'x_1': NotNullFilter([Latest(...)], 0), "
          "'x_2': NotNullFilter([Latest(...)], 0)})"),
          ("(Latest([Fundamentals.slice(dimension='ART', period_offset=0)<US>.MARKETCAP], 1),)"),
          ("(Latest([Fundamentals.slice(dimension='ART', period_offset=-1)<US>.MARKETCAP], 1),)"),
          ("(Latest([Fundamentals.slice(dimension='ART', period_offset=-2)<US>.MARKETCAP], 1),)"),
         ),
        ('ARQ', 9, 4, True,
         ("NumExprFilter(expr='(x_0 & x_1) & (x_2)', "
          "bindings={'x_0': NotNullFilter([Latest(...)], 0), "
          "'x_1': NotNullFilter([Latest(...)], 0), "
          "'x_2': NotNullFilter([Latest(...)], 0)})"),
          ("(Latest([Fundamentals.slice(dimension='ARQ', period_offset=0)<US>.MARKETCAP], 1),)"),
          ("(Latest([Fundamentals.slice(dimension='ARQ', period_offset=-4)<US>.MARKETCAP], 1),)"),
          ("(Latest([Fundamentals.slice(dimension='ARQ', period_offset=-8)<US>.MARKETCAP], 1),)"),
         ),
    ])
    def test_all_periods_present(
        self,
        dimension,
        window_length,
        step,
        use_mask,
        expected,
        expected_x_0,
        expected_x_1,
        expected_x_2):

        kwargs = dict(
            window_length=window_length)
        if step is not None:
            kwargs["step"] = step
        if use_mask:
            kwargs["mask"] = filters.StaticSids(["A", "B"])

        term = periodic.AllPeriodsPresent(
            sharadar.Fundamentals.slice(dimension).MARKETCAP, **kwargs)

        self.assertEqual(repr(term), expected)
        self.assertEqual(repr(term.bindings["x_0"].inputs), expected_x_0)
        self.assertEqual(repr(term.bindings["x_1"].inputs), expected_x_1)
        self.assertEqual(repr(term.bindings["x_2"].inputs), expected_x_2)

        for notnullfilter in term.inputs:
            for latest in notnullfilter.inputs:
                if use_mask:
                    self.assertEqual(repr(latest.mask), "StaticSids([SecuritiesMaster.Sid], 1)")
                else:
                    self.assertEqual(repr(latest.mask), "AssetExists()")

    def test_all_periods_present_callable(self):

        term = periodic.AllPeriodsPresent(
            OPMARGIN, window_length=3, mask=filters.StaticSids(["A", "B"]))

        self.assertEqual(
            repr(term),
            "NumExprFilter(expr='(x_0 & x_1) & (x_2)', "
            "bindings={'x_0': NotNullFilter([Latest(...)], 0), "
            "'x_1': NotNullFilter([NumExprFactor(...)], 0), "
            "'x_2': NotNullFilter([NumExprFactor(...)], 0)})"
        )

        # unpack x_0
        self.assertEqual(
            repr(term.bindings["x_0"].inputs[0].inputs),
            "(NumExprFactor(expr='x_0 / x_1', "
            "bindings={'x_0': Latest([Fundamentals.slice(dimension='ART', period_offset=0)<US>.OPINC], 1), "
            "'x_1': Latest([Fundamentals.slice(dimension='ART', period_offset=0)<US>.REVENUE], 1)}),)"
        )

        for latestinput in term.bindings["x_0"].inputs:
            self.assertEqual(repr(latestinput.mask), "StaticSids([SecuritiesMaster.Sid], 1)")

        # unpack x_1
        self.assertEqual(
            repr(term.bindings["x_1"].inputs),
            "(NumExprFactor(expr='x_0 / x_1', "
            "bindings={'x_0': Latest([Fundamentals.slice(dimension='ART', period_offset=-1)<US>.OPINC], 1), "
            "'x_1': Latest([Fundamentals.slice(dimension='ART', period_offset=-1)<US>.REVENUE], 1)}),)"
        )

        for latestinput in term.bindings["x_1"].inputs[0].bindings.values():
            self.assertEqual(repr(latestinput.mask), "StaticSids([SecuritiesMaster.Sid], 1)")

        # unpack x_2
        self.assertEqual(
            repr(term.bindings["x_2"].inputs),
            "(NumExprFactor(expr='x_0 / x_1', "
            "bindings={'x_0': Latest([Fundamentals.slice(dimension='ART', period_offset=-2)<US>.OPINC], 1), "
            "'x_1': Latest([Fundamentals.slice(dimension='ART', period_offset=-2)<US>.REVENUE], 1)}),)"
        )

        for latestinput in term.bindings["x_2"].inputs[0].bindings.values():
            self.assertEqual(repr(latestinput.mask), "StaticSids([SecuritiesMaster.Sid], 1)")

    @parameterized.expand([
        ('ART', 4, None, None,
         ("NumExprFactor(expr='(((x_0 + x_1) + (x_2)) + (x_3)) / (4.0)', "
          "bindings={'x_0': Latest([Fundamentals.slice(dimension='ART', period_offset=0)<US>.DPS], 1), "
          "'x_1': Latest([Fundamentals.slice(dimension='ART', period_offset=-1)<US>.DPS], 1), "
          "'x_2': Latest([Fundamentals.slice(dimension='ART', period_offset=-2)<US>.DPS], 1), "
          "'x_3': Latest([Fundamentals.slice(dimension='ART', period_offset=-3)<US>.DPS], 1)})")
         ),
        ('ARQ', 16, 4, True,
         ("NumExprFactor(expr='(((x_0 + x_1) + (x_2)) + (x_3)) / (4.0)', "
          "bindings={'x_0': Latest([Fundamentals.slice(dimension='ARQ', period_offset=0)<US>.DPS], 1), "
          "'x_1': Latest([Fundamentals.slice(dimension='ARQ', period_offset=-4)<US>.DPS], 1), "
          "'x_2': Latest([Fundamentals.slice(dimension='ARQ', period_offset=-8)<US>.DPS], 1), "
          "'x_3': Latest([Fundamentals.slice(dimension='ARQ', period_offset=-12)<US>.DPS], 1)})")
         ),
    ])
    def test_periodic_average(
        self,
        dimension,
        window_length,
        step,
        use_mask,
        expected):

        kwargs = dict(
            window_length=window_length)
        if step is not None:
            kwargs["step"] = step
        if use_mask:
            kwargs["mask"] = filters.StaticSids(["A", "B"])

        term = periodic.PeriodicAverage(
            sharadar.Fundamentals.slice(dimension).DPS, **kwargs)

        self.assertEqual(repr(term), expected)

        for input in term.inputs:
            if use_mask:
                self.assertEqual(repr(input.mask), "StaticSids([SecuritiesMaster.Sid], 1)")
            else:
                self.assertEqual(repr(input.mask), "AssetExists()")

    def test_periodic_average_callable(self):

        term = periodic.PeriodicAverage(
            OPMARGIN, window_length=3)

        self.assertEqual(
            repr(term),
            "NumExprFactor(expr='(((x_2) + (x_0 / x_1)) + (x_3 / x_4)) / (3.0)', "
            "bindings={'x_0': Latest([Fundamentals.slice(dimension='ART', period_offset=-1)<US>.OPINC], 1), "
            "'x_1': Latest([Fundamentals.slice(dimension='ART', period_offset=-1)<US>.REVENUE], 1), "
            "'x_2': Latest([NumExprFactor(...)], 1), "
            "'x_3': Latest([Fundamentals.slice(dimension='ART', period_offset=-2)<US>.OPINC], 1), "
            "'x_4': Latest([Fundamentals.slice(dimension='ART', period_offset=-2)<US>.REVENUE], 1)})"
        )

        # unpack x_2
        self.assertEqual(
            repr(term.bindings["x_2"].inputs),
            "(NumExprFactor(expr='x_0 / x_1', "
            "bindings={'x_0': Latest([Fundamentals.slice(dimension='ART', period_offset=0)<US>.OPINC], 1), "
            "'x_1': Latest([Fundamentals.slice(dimension='ART', period_offset=0)<US>.REVENUE], 1)}),)"
        )

        for input in term.inputs:
            self.assertEqual(repr(input.mask), "AssetExists()")

    @parameterized.expand([
        ('ART', 4, None,
         ("NumExprFactor(expr='x_0 - x_1', "
          "bindings={'x_0': Latest([Fundamentals.slice(dimension='ART', period_offset=0)<US>.REVENUE], 1), "
          "'x_1': Latest([Fundamentals.slice(dimension='ART', period_offset=-3)<US>.REVENUE], 1)})")
         ),
        ('ARQ', 16, True,
         ("NumExprFactor(expr='x_0 - x_1', "
          "bindings={'x_0': Latest([Fundamentals.slice(dimension='ARQ', period_offset=0)<US>.REVENUE], 1), "
          "'x_1': Latest([Fundamentals.slice(dimension='ARQ', period_offset=-15)<US>.REVENUE], 1)})")
         ),
    ])
    def test_periodic_change(
        self,
        dimension,
        window_length,
        use_mask,
        expected):

        kwargs = dict(
            window_length=window_length)
        if use_mask:
            kwargs["mask"] = filters.StaticSids(["A", "B"])

        term = periodic.PeriodicChange(
            sharadar.Fundamentals.slice(dimension).REVENUE, **kwargs)

        self.assertEqual(repr(term), expected)

        for input in term.inputs:
            if use_mask:
                self.assertEqual(repr(input.mask), "StaticSids([SecuritiesMaster.Sid], 1)")
            else:
                self.assertEqual(repr(input.mask), "AssetExists()")

    @parameterized.expand([
        ('ART', 4, None,
         ("NumExprFactor(expr='(x_0 - x_1) / (abs(x_1))', "
          "bindings={'x_0': Latest([Fundamentals.slice(dimension='ART', period_offset=0)<US>.REVENUE], 1), "
          "'x_1': Latest([Fundamentals.slice(dimension='ART', period_offset=-3)<US>.REVENUE], 1)})")
         ),
        ('ARQ', 16, True,
         ("NumExprFactor(expr='(x_0 - x_1) / (abs(x_1))', "
          "bindings={'x_0': Latest([Fundamentals.slice(dimension='ARQ', period_offset=0)<US>.REVENUE], 1), "
          "'x_1': Latest([Fundamentals.slice(dimension='ARQ', period_offset=-15)<US>.REVENUE], 1)})")
         ),
    ])
    def test_periodic_percent_change(
        self,
        dimension,
        window_length,
        use_mask,
        expected):

        kwargs = dict(
            window_length=window_length)
        if use_mask:
            kwargs["mask"] = filters.StaticSids(["A", "B"])

        term = periodic.PeriodicPercentChange(
            sharadar.Fundamentals.slice(dimension).REVENUE, **kwargs)

        self.assertEqual(repr(term), expected)

        for input in term.inputs:
            if use_mask:
                self.assertEqual(repr(input.mask), "StaticSids([SecuritiesMaster.Sid], 1)")
            else:
                self.assertEqual(repr(input.mask), "AssetExists()")

    def test_periodic_percent_change_callable(self):

        term = periodic.PeriodicPercentChange(
            OPMARGIN, window_length=4, mask=filters.StaticSids(["A", "B"]))

        self.assertEqual(
            repr(term),
            "NumExprFactor(expr='((x_0 / x_1) - (x_2 / x_3)) / (abs(x_2 / x_3))', "
            "bindings={'x_0': Latest([Fundamentals.slice(dimension='ART', period_offset=0)<US>.OPINC], 1), "
            "'x_1': Latest([Fundamentals.slice(dimension='ART', period_offset=0)<US>.REVENUE], 1), "
            "'x_2': Latest([Fundamentals.slice(dimension='ART', period_offset=-3)<US>.OPINC], 1), "
            "'x_3': Latest([Fundamentals.slice(dimension='ART', period_offset=-3)<US>.REVENUE], 1)})"
        )

        for input in term.inputs:
            self.assertEqual(repr(input.mask), "StaticSids([SecuritiesMaster.Sid], 1)")

    @parameterized.expand([
        ('ARY', 4, None,
         ("NumExprFactor(expr='((x_0 / x_1) ** (0.25)) - (1.0)', "
          "bindings={'x_0': Latest([Fundamentals.slice(dimension='ARY', period_offset=0)<US>.DIVYIELD], 1), "
          "'x_1': IfElseFactor([NumExprFilter(...), Latest(...), ConstantFactor(...)], 0)})"),
          ("(NumExprFilter(expr='x_0 > (0.0)', "
           "bindings={'x_0': Latest([Fundamentals.slice(dimension='ARY', period_offset=-3)<US>.DIVYIELD], 1)}), "
           "Latest([Fundamentals.slice(dimension='ARY', period_offset=-3)<US>.DIVYIELD], 1), "
           "ConstantFactor(nan))")
         ),
        ('ARQ', 16, True,
         ("NumExprFactor(expr='((x_0 / x_1) ** (0.25)) - (1.0)', "
          "bindings={'x_0': Latest([Fundamentals.slice(dimension='ARQ', period_offset=0)<US>.DIVYIELD], 1), "
          "'x_1': IfElseFactor([NumExprFilter(...), Latest(...), ConstantFactor(...)], 0)})"),
          ("(NumExprFilter(expr='x_0 > (0.0)', "
           "bindings={'x_0': Latest([Fundamentals.slice(dimension='ARQ', period_offset=-15)<US>.DIVYIELD], 1)}), "
           "Latest([Fundamentals.slice(dimension='ARQ', period_offset=-15)<US>.DIVYIELD], 1), "
           "ConstantFactor(nan))")
         ),
    ])
    def test_periodic_cagr(
        self,
        dimension,
        window_length,
        use_mask,
        expected,
        expected_x1):

        kwargs = dict(
            window_length=window_length)
        if use_mask:
            kwargs["mask"] = filters.StaticSids(["A", "B"])

        term = periodic.PeriodicCAGR(
            sharadar.Fundamentals.slice(dimension).DIVYIELD, **kwargs)

        self.assertEqual(repr(term), expected)

        self.assertEqual(
            repr(term.bindings["x_1"].inputs), expected_x1)

        # Just check the Latest input to the IfElseFactor
        input = term.inputs[1].inputs[1]
        if use_mask:
            self.assertEqual(repr(input.mask), "StaticSids([SecuritiesMaster.Sid], 1)")
        else:
            self.assertEqual(repr(input.mask), "AssetExists()")

    def test_periodic_cagr_callable(self):

        term = periodic.PeriodicCAGR(
            OPMARGIN, window_length=16, periods_per_year=4)

        self.assertEqual(
            repr(term),
            "NumExprFactor(expr='(((x_0 / x_1) / (x_2)) ** (0.25)) - (1.0)', "
            "bindings={'x_0': Latest([Fundamentals.slice(dimension='ART', period_offset=0)<US>.OPINC], 1), "
            "'x_1': Latest([Fundamentals.slice(dimension='ART', period_offset=0)<US>.REVENUE], 1), "
            "'x_2': IfElseFactor([NumExprFilter(...), NumExprFactor(...), ConstantFactor(...)], 0)})"
        )

        # unpack x_2
        self.assertEqual(
            repr(term.bindings["x_2"].inputs),
            "(NumExprFilter(expr='(x_0 / x_1) > (0.0)', "
            "bindings={'x_0': Latest([Fundamentals.slice(dimension='ART', period_offset=-15)<US>.OPINC], 1), "
            "'x_1': Latest([Fundamentals.slice(dimension='ART', period_offset=-15)<US>.REVENUE], 1)}), "
            "NumExprFactor(expr='x_0 / x_1', "
            "bindings={'x_0': Latest([Fundamentals.slice(dimension='ART', period_offset=-15)<US>.OPINC], 1), "
            "'x_1': Latest([Fundamentals.slice(dimension='ART', period_offset=-15)<US>.REVENUE], 1)}), "
            "ConstantFactor(nan))"
        )

        # Just check the Latest inputs to the IfElseFactor
        for input in term.inputs[2].inputs[1:]:
            self.assertEqual(repr(input.mask), "AssetExists()")

    def test_periodic_high(self):

        term = periodic.PeriodicHigh(
            sharadar.Fundamentals.slice('ART').EPS,
            window_length=2,
            mask=filters.StaticSids(["A", "B"]))

        self.assertEqual(
            repr(term),
            "NumExprFactor(expr='(x_0 * x_1) + (x_2 * x_3)', "
            "bindings={'x_0': BooleanFactor([NumExprFilter(...)], 0), "
            "'x_1': Latest([Fundamentals.slice(dimension='ART', period_offset=0)<US>.EPS], 1), "
            "'x_2': BooleanFactor([NumExprFilter(...)], 0), "
            "'x_3': Latest([Fundamentals.slice(dimension='ART', period_offset=-1)<US>.EPS], 1)})"
        )

        self.assertEqual(
            repr(term.bindings['x_1'].mask),
            "StaticSids([SecuritiesMaster.Sid], 1)"
        )

        self.assertEqual(
            repr(term.bindings['x_3'].mask),
            "StaticSids([SecuritiesMaster.Sid], 1)"
        )

        # unpack x_0
        self.assertEqual(
            repr(term.bindings["x_0"].inputs),
            "(NumExprFilter(expr='x_0 > x_1', "
            "bindings={'x_0': Latest([Fundamentals.slice(dimension='ART', period_offset=0)<US>.EPS], 1), "
            "'x_1': Latest([Fundamentals.slice(dimension='ART', period_offset=-1)<US>.EPS], 1)}),)"
        )

        for latestinput in term.bindings["x_0"].inputs[0].bindings.values():
            self.assertEqual(repr(latestinput.mask), "StaticSids([SecuritiesMaster.Sid], 1)")

        # unpack x_2
        self.assertEqual(
            repr(term.bindings["x_2"].inputs),
            "(NumExprFilter(expr='x_0 > x_1', "
            "bindings={'x_0': Latest([Fundamentals.slice(dimension='ART', period_offset=-1)<US>.EPS], 1), "
            "'x_1': Latest([Fundamentals.slice(dimension='ART', period_offset=0)<US>.EPS], 1)}),)"
        )

        for latestinput in term.bindings["x_2"].inputs[0].bindings.values():
            self.assertEqual(repr(latestinput.mask), "StaticSids([SecuritiesMaster.Sid], 1)")

    def test_periodic_high_callable(self):

        term = periodic.PeriodicHigh(
            OPMARGIN,
            window_length=2)

        self.assertEqual(
            repr(term),
            "NumExprFactor(expr='(x_0 * x_1) + ((x_4) * (x_2 / x_3))', "
            "bindings={'x_0': BooleanFactor([NumExprFilter(...)], 0), "
            "'x_1': Latest([NumExprFactor(...)], 1), "
            "'x_2': Latest([Fundamentals.slice(dimension='ART', period_offset=-1)<US>.OPINC], 1), "
            "'x_3': Latest([Fundamentals.slice(dimension='ART', period_offset=-1)<US>.REVENUE], 1), "
            "'x_4': BooleanFactor([NumExprFilter(...)], 0)})"
        )

        # unpack x_0
        self.assertEqual(
            repr(term.bindings["x_0"].inputs),
            "(NumExprFilter(expr='(x_0 / x_1) < (x_2)', "
            "bindings={'x_0': Latest([Fundamentals.slice(dimension='ART', period_offset=-1)<US>.OPINC], 1), "
            "'x_1': Latest([Fundamentals.slice(dimension='ART', period_offset=-1)<US>.REVENUE], 1), "
            "'x_2': Latest([NumExprFactor(...)], 1)}),)"
        )

        # unpack x_0 x_2
        self.assertEqual(
            repr(term.bindings["x_0"].inputs[0].bindings["x_2"].inputs),
            "(NumExprFactor(expr='x_0 / x_1', "
            "bindings={'x_0': Latest([Fundamentals.slice(dimension='ART', period_offset=0)<US>.OPINC], 1), "
            "'x_1': Latest([Fundamentals.slice(dimension='ART', period_offset=0)<US>.REVENUE], 1)}),)"
        )

        # unpack x_1
        self.assertEqual(
            repr(term.bindings["x_1"].inputs),
            "(NumExprFactor(expr='x_0 / x_1', "
            "bindings={'x_0': Latest([Fundamentals.slice(dimension='ART', period_offset=0)<US>.OPINC], 1), "
            "'x_1': Latest([Fundamentals.slice(dimension='ART', period_offset=0)<US>.REVENUE], 1)}),)"
        )

        # unpack x_4
        self.assertEqual(
            repr(term.bindings["x_4"].inputs),
            "(NumExprFilter(expr='(x_0 / x_1) > (x_2)', "
            "bindings={'x_0': Latest([Fundamentals.slice(dimension='ART', period_offset=-1)<US>.OPINC], 1), "
            "'x_1': Latest([Fundamentals.slice(dimension='ART', period_offset=-1)<US>.REVENUE], 1), "
            "'x_2': Latest([NumExprFactor(...)], 1)}),)"
        )

        # unpack x_4 x_2
        self.assertEqual(
            repr(term.bindings["x_4"].inputs[0].bindings["x_2"].inputs),
            "(NumExprFactor(expr='x_0 / x_1', "
            "bindings={'x_0': Latest([Fundamentals.slice(dimension='ART', period_offset=0)<US>.OPINC], 1), "
            "'x_1': Latest([Fundamentals.slice(dimension='ART', period_offset=0)<US>.REVENUE], 1)}),)"
        )

    def test_periodic_low(self):

        term = periodic.PeriodicLow(
            sharadar.Fundamentals.slice('ARQ').EPS,
            window_length=12,
            step=4)

        self.assertEqual(
            repr(term),
            "NumExprFactor(expr='((x_0 * x_1) + (x_2 * x_3)) + (x_4 * x_5)', "
            "bindings={'x_0': BooleanFactor([NumExprFilter(...)], 0), "
            "'x_1': Latest([Fundamentals.slice(dimension='ARQ', period_offset=0)<US>.EPS], 1), "
            "'x_2': BooleanFactor([NumExprFilter(...)], 0), "
            "'x_3': Latest([Fundamentals.slice(dimension='ARQ', period_offset=-4)<US>.EPS], 1), "
            "'x_4': BooleanFactor([NumExprFilter(...)], 0), "
            "'x_5': Latest([Fundamentals.slice(dimension='ARQ', period_offset=-8)<US>.EPS], 1)})"
        )

        self.assertEqual(
            repr(term.bindings['x_1'].mask),
            "AssetExists()"
        )

        self.assertEqual(
            repr(term.bindings['x_3'].mask),
            "AssetExists()"
        )

        self.assertEqual(
            repr(term.bindings['x_5'].mask),
            "AssetExists()"
        )

        # unpack x_0
        self.assertEqual(
            repr(term.bindings["x_0"].inputs),
            "(NumExprFilter(expr='(x_0 < x_1) & (x_0 < x_2)', "
            "bindings={'x_0': Latest([Fundamentals.slice(dimension='ARQ', period_offset=0)<US>.EPS], 1), "
            "'x_1': Latest([Fundamentals.slice(dimension='ARQ', period_offset=-4)<US>.EPS], 1), "
            "'x_2': Latest([Fundamentals.slice(dimension='ARQ', period_offset=-8)<US>.EPS], 1)}),)"
        )

        for latestinput in term.bindings["x_0"].inputs[0].bindings.values():
            self.assertEqual(repr(latestinput.mask), "AssetExists()")

        # unpack x_2
        self.assertEqual(
            repr(term.bindings["x_2"].inputs),
            "(NumExprFilter(expr='(x_0 < x_1) & (x_0 < x_2)', "
            "bindings={'x_0': Latest([Fundamentals.slice(dimension='ARQ', period_offset=-4)<US>.EPS], 1), "
            "'x_1': Latest([Fundamentals.slice(dimension='ARQ', period_offset=0)<US>.EPS], 1), "
            "'x_2': Latest([Fundamentals.slice(dimension='ARQ', period_offset=-8)<US>.EPS], 1)}),)"
        )

        for latestinput in term.bindings["x_2"].inputs[0].bindings.values():
            self.assertEqual(repr(latestinput.mask), "AssetExists()")

        # unpack x_4
        self.assertEqual(
            repr(term.bindings["x_4"].inputs),
            "(NumExprFilter(expr='(x_0 < x_1) & (x_0 < x_2)', "
            "bindings={'x_0': Latest([Fundamentals.slice(dimension='ARQ', period_offset=-8)<US>.EPS], 1), "
            "'x_1': Latest([Fundamentals.slice(dimension='ARQ', period_offset=0)<US>.EPS], 1), "
            "'x_2': Latest([Fundamentals.slice(dimension='ARQ', period_offset=-4)<US>.EPS], 1)}),)"
        )

        for latestinput in term.bindings["x_4"].inputs[0].bindings.values():
            self.assertEqual(repr(latestinput.mask), "AssetExists()")
