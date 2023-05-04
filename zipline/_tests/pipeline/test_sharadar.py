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
    sharadar,
    filters)

class SharadarFactorsTestCase(unittest.TestCase):


    @parameterized.expand([
        (None, None, None, None),
        ('ARQ', None, None, True),
        ('ARY', None, None, None),
        ('ART', -1, None, None),
        ('ART', -1, -1, True),
    ])
    def test_piotroski_f_score(
        self,
        dimension,
        period_offset,
        previous_period_offset,
        use_mask):

        if not any([dimension, period_offset, previous_period_offset, use_mask]):
            term = sharadar.PiotroskiFScore()
        else:
            kwargs = {}
            if period_offset is not None:
                kwargs["period_offset"] = period_offset
            if previous_period_offset is not None:
                kwargs["previous_period_offset"] = previous_period_offset
            if use_mask:
                kwargs["mask"] = filters.StaticSids(['A', 'B'])

            term = sharadar.PiotroskiFScore(
                dimension=dimension,
                **kwargs)

        dimension = dimension or "ART"
        period_offset = period_offset or 0
        previous_period_offset = previous_period_offset or (
            -1 if dimension.endswith("Y") else -4)
        previous_period_offset = period_offset + previous_period_offset

        self.assertEqual(
            repr(term),
            "NumExprFactor(expr='(((((((x_0 + x_1) + (x_2)) + (x_3)) + (x_4)) + (x_5)) + (x_6)) + (x_7)) + (x_8)', "
            "bindings={'x_0': BooleanFactor([NumExprFilter(...)], 0), "
            "'x_1': BooleanFactor([NumExprFilter(...)], 0), "
            "'x_2': BooleanFactor([NumExprFilter(...)], 0), "
            "'x_3': BooleanFactor([NumExprFilter(...)], 0), "
            "'x_4': BooleanFactor([NumExprFilter(...)], 0), "
            "'x_5': BooleanFactor([NumExprFilter(...)], 0), "
            "'x_6': BooleanFactor([NumExprFilter(...)], 0), "
            "'x_7': BooleanFactor([NumExprFilter(...)], 0), "
            "'x_8': BooleanFactor([NumExprFilter(...)], 0)})"
        )

        # unpack x_0 (ROA > 0)
        self.assertEqual(
            repr(term.bindings["x_0"].inputs),
            "(NumExprFilter(expr='x_0 > (0.0)', "
            f"bindings={{'x_0': Latest([Fundamentals.slice(dimension='{dimension}', period_offset={period_offset})<US>.ROA], 1)}}),)"
        )

        # unpack x_1 (NCFO > 0)
        self.assertEqual(
            repr(term.bindings["x_1"].inputs),
            "(NumExprFilter(expr='x_0 > (0.0)', "
            f"bindings={{'x_0': Latest([Fundamentals.slice(dimension='{dimension}', period_offset={period_offset})<US>.NCFO], 1)}}),)"
        )

        # unpack x_2 (ROA > ROA(-1))
        self.assertEqual(
            repr(term.bindings["x_2"].inputs),
            "(NumExprFilter(expr='x_0 > x_1', "
            f"bindings={{'x_0': Latest([Fundamentals.slice(dimension='{dimension}', period_offset={period_offset})<US>.ROA], 1), "
            f"'x_1': Latest([Fundamentals.slice(dimension='{dimension}', period_offset={previous_period_offset})<US>.ROA], 1)}}),)"
        )

        # unpack x_3 (NCFO / ASSETS > ROA)
        self.assertEqual(
            repr(term.bindings["x_3"].inputs),
            "(NumExprFilter(expr='(x_0 / x_1) > (x_2)', "
            f"bindings={{'x_0': Latest([Fundamentals.slice(dimension='{dimension}', period_offset={period_offset})<US>.NCFO], 1), "
            f"'x_1': Latest([Fundamentals.slice(dimension='{dimension}', period_offset={period_offset})<US>.ASSETSAVG], 1), "
            f"'x_2': Latest([Fundamentals.slice(dimension='{dimension}', period_offset={period_offset})<US>.ROA], 1)}}),)"
        )

        # unpack x_4 (DEBTNC / ASSETS < DEBTNC(-1) / ASSETS(-1))
        self.assertEqual(
            repr(term.bindings["x_4"].inputs),
            "(NumExprFilter(expr='(x_0 / x_1) < (x_2 / x_3)', "
            f"bindings={{'x_0': Latest([Fundamentals.slice(dimension='{dimension}', period_offset={period_offset})<US>.DEBTNC], 1), "
            f"'x_1': Latest([Fundamentals.slice(dimension='{dimension}', period_offset={period_offset})<US>.ASSETSAVG], 1), "
            f"'x_2': Latest([Fundamentals.slice(dimension='{dimension}', period_offset={previous_period_offset})<US>.DEBTNC], 1), "
            f"'x_3': Latest([Fundamentals.slice(dimension='{dimension}', period_offset={previous_period_offset})<US>.ASSETSAVG], 1)}}),)"
        )

        # unpack x_5 (CURRENTRATIO > CURRENT RATIO(-1))
        self.assertEqual(
            repr(term.bindings["x_5"].inputs),
            "(NumExprFilter(expr='x_0 > x_1', "
            f"bindings={{'x_0': Latest([Fundamentals.slice(dimension='{dimension}', period_offset={period_offset})<US>.CURRENTRATIO], 1), "
            f"'x_1': Latest([Fundamentals.slice(dimension='{dimension}', period_offset={previous_period_offset})<US>.CURRENTRATIO], 1)}}),)"
        )

        # unpack x_6 (SHARESWA <= SHARESWA(-1))
        self.assertEqual(
            repr(term.bindings["x_6"].inputs),
            "(NumExprFilter(expr='x_0 <= x_1', "
            f"bindings={{'x_0': Latest([Fundamentals.slice(dimension='{dimension}', period_offset={period_offset})<US>.SHARESWA], 1), "
            f"'x_1': Latest([Fundamentals.slice(dimension='{dimension}', period_offset={previous_period_offset})<US>.SHARESWA], 1)}}),)"
        )

        # unpack x_7 (GROSSMARGIN > GROSSMARGIN(-1))
        self.assertEqual(
            repr(term.bindings["x_7"].inputs),
            "(NumExprFilter(expr='x_0 > x_1', "
            f"bindings={{'x_0': Latest([Fundamentals.slice(dimension='{dimension}', period_offset={period_offset})<US>.GROSSMARGIN], 1), "
            f"'x_1': Latest([Fundamentals.slice(dimension='{dimension}', period_offset={previous_period_offset})<US>.GROSSMARGIN], 1)}}),)"
        )

        # unpack x_8 (ASSETTURNOVER > ASSETTURNOVER(-1))
        self.assertEqual(
            repr(term.bindings["x_8"].inputs),
            "(NumExprFilter(expr='x_0 > x_1', "
            f"bindings={{'x_0': Latest([Fundamentals.slice(dimension='{dimension}', period_offset={period_offset})<US>.ASSETTURNOVER], 1), "
            f"'x_1': Latest([Fundamentals.slice(dimension='{dimension}', period_offset={previous_period_offset})<US>.ASSETTURNOVER], 1)}}),)"
        )

        for i in range(8):
            for latestinput in term.bindings[f"x_{i}"].inputs[0].bindings.values():
                if use_mask:
                    self.assertEqual(repr(latestinput.mask), "StaticSids([SecuritiesMaster.Sid], 1)")
                else:
                    self.assertEqual(repr(latestinput.mask), "AssetExists()")

    @parameterized.expand([
        (None, None, None),
        ('ARQ', None, True),
        ('ARY', None, None),
        ('ART', -1, True),
    ])
    def test_altman_z_score(
        self,
        dimension,
        period_offset,
        use_mask):

        if not any([dimension, period_offset, use_mask]):
            term = sharadar.AltmanZScore()
        else:
            kwargs = {}
            if period_offset is not None:
                kwargs["period_offset"] = period_offset
            if use_mask:
                kwargs["mask"] = filters.StaticSids(['A', 'B'])

            term = sharadar.AltmanZScore(
                dimension=dimension,
                **kwargs)

        dimension = dimension or "ART"
        period_offset = period_offset or 0

        self.assertEqual(
            repr(term),
            "NumExprFactor(expr='(((((1.2) * (x_0 / x_1)) + ((1.4) * (x_2 / x_1))) + ((3.3) * (x_3 / x_1))) + ((0.6) * (x_4 / x_5))) + ((1.0) * (x_6 / x_1))', "
            f"bindings={{'x_0': Latest([Fundamentals.slice(dimension='{dimension}', period_offset={period_offset})<US>.WORKINGCAPITAL], 1), "
            f"'x_1': Latest([Fundamentals.slice(dimension='{dimension}', period_offset={period_offset})<US>.ASSETS], 1), "
            f"'x_2': Latest([Fundamentals.slice(dimension='{dimension}', period_offset={period_offset})<US>.RETEARN], 1), "
            f"'x_3': Latest([Fundamentals.slice(dimension='{dimension}', period_offset={period_offset})<US>.EBIT], 1), "
            f"'x_4': Latest([Fundamentals.slice(dimension='{dimension}', period_offset={period_offset})<US>.MARKETCAP], 1), "
            f"'x_5': Latest([Fundamentals.slice(dimension='{dimension}', period_offset={period_offset})<US>.LIABILITIES], 1), "
            f"'x_6': Latest([Fundamentals.slice(dimension='{dimension}', period_offset={period_offset})<US>.REVENUE], 1)}})"
        )

        for latestinput in term.bindings.values():
            if use_mask:
                self.assertEqual(repr(latestinput.mask), "NumExprFilter(expr='(~x_0) & (x_1)', bindings={'x_0': ArrayPredicate([Latest(...)], 0), 'x_1': StaticSids([SecuritiesMaster.Sid], 1)})")
                self.assertEqual(repr(latestinput.mask.bindings['x_1']), "StaticSids([SecuritiesMaster.Sid], 1)")
            else:
                self.assertEqual(repr(latestinput.mask), "NumExprFilter(expr='~x_0', bindings={'x_0': ArrayPredicate([Latest(...)], 0)})")

            self.assertEqual(repr(latestinput.mask.bindings['x_0']), "ArrayPredicate([Latest(...)], 0)")
            self.assertEqual(repr(latestinput.mask.bindings['x_0'].inputs), "(Latest([SecuritiesMaster.sharadar_Sector], 1),)")
            self.assertEqual(latestinput.mask.bindings['x_0'].params["op"].__name__, "isin")
            self.assertEqual(sorted(latestinput.mask.bindings['x_0'].params["opargs"][0]), ['Financial Services', 'Real Estate'])

    @parameterized.expand([
        (None, None, None),
        ('ARQ', None, True),
        ('ARY', None, None),
        ('ART', -1, True),
    ])
    def test_interest_coverage_ratio(
        self,
        dimension,
        period_offset,
        use_mask):

        if not any([dimension, period_offset, use_mask]):
            term = sharadar.InterestCoverageRatio()
        else:
            kwargs = {}
            if period_offset is not None:
                kwargs["period_offset"] = period_offset
            if use_mask:
                kwargs["mask"] = filters.StaticSids(['A', 'B'])

            term = sharadar.InterestCoverageRatio(
                dimension=dimension,
                **kwargs)

        dimension = dimension or "ART"
        period_offset = period_offset or 0

        self.assertEqual(
            repr(term),
            "NumExprFactor(expr='x_0 / x_1', "
            f"bindings={{'x_0': Latest([Fundamentals.slice(dimension='{dimension}', period_offset={period_offset})<US>.EBIT], 1), "
            f"'x_1': Latest([Fundamentals.slice(dimension='{dimension}', period_offset={period_offset})<US>.INTEXP], 1)}})"
        )

        # each input should have a mask that only computes ICR if both EBIT and INTEXP
        # are positive
        for _term in term.bindings.values():
            self.assertEqual(
                repr(_term.mask),
                "NumExprFilter(expr='(x_0 > (0.0)) & (x_1 > (0.0))', "
                f"bindings={{'x_0': Latest([Fundamentals.slice(dimension='{dimension}', period_offset={period_offset})<US>.INTEXP], 1), "
                f"'x_1': Latest([Fundamentals.slice(dimension='{dimension}', period_offset={period_offset})<US>.EBIT], 1)}})"
            )

            for latestinput in _term.mask.bindings.values():
                if use_mask:
                    self.assertEqual(repr(latestinput.mask), "StaticSids([SecuritiesMaster.Sid], 1)")
                else:
                    self.assertEqual(repr(latestinput.mask), "AssetExists()")
