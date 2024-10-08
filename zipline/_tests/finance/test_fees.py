#
# Copyright 2024 QuantRocket LLC.
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
from six import string_types
import pandas as pd

from zipline.assets import Equity, Asset
from zipline.assets.continuous_futures import ContinuousFuture
from zipline.assets.synthetic import (
    make_simple_equity_info,
)
import zipline._testing.fixtures as zf
from quantrocket.fundamental import NoFundamentalData
from unittest.mock import patch

class TestFees(zf.WithMakeAlgo, zf.ZiplineTestCase):
    START_DATE = pd.Timestamp('2018-04-04')
    END_DATE = pd.Timestamp('2018-12-31')
    SIM_PARAMS_DATA_FREQUENCY = 'daily'
    DATA_PORTAL_USE_MINUTE_DATA = False
    EQUITY_DAILY_BAR_LOOKBACK_DAYS = 5  # max history window length

    STRING_TYPE_NAMES = [s.__name__ for s in string_types]
    STRING_TYPE_NAMES_STRING = ', '.join(STRING_TYPE_NAMES)
    ASSET_TYPE_NAME = Asset.__name__
    CONTINUOUS_FUTURE_NAME = ContinuousFuture.__name__
    ASSET_OR_STRING_TYPE_NAMES = ', '.join([ASSET_TYPE_NAME] +
                                           STRING_TYPE_NAMES)
    ASSET_OR_CF_TYPE_NAMES = ', '.join([ASSET_TYPE_NAME,
                                                  CONTINUOUS_FUTURE_NAME])

    sids = 0, 1, 3

    # FIXME: Pass a benchmark explicitly here.
    BENCHMARK_SID = None

    @classmethod
    def make_equity_info(cls):

        data = make_simple_equity_info(
            cls.sids,
            cls.START_DATE,
            cls.END_DATE,
            real_sids=[f"FI{sid}" for sid in cls.sids],
        )
        data.loc[3, 'symbol'] = 'TEST'
        data['auto_close_date'] = pd.NaT
        data.loc[0, 'auto_close_date'] = data.loc[0].end_date
        return data

    @classmethod
    def make_equity_daily_bar_data(cls, country_code, sids):
        cal = cls.exchange_calendars[Equity]
        sessions = cal.sessions_in_range(cls.START_DATE, cls.END_DATE)
        flat_frame = pd.DataFrame({
            'close': 10., 'high': 10.5, 'low': 9.5, 'open': 10., 'volume': 100,
        }, index=sessions)

        profitable_frame = pd.DataFrame({
            'close': [10 * (1.001 ** i) for i in range(len(sessions))],
            'high': [10.5 * (1.001 ** i) for i in range(len(sessions))],
            'low': [9.5 * (1.001 ** i) for i in range(len(sessions))],
            'open': [10 * (1.001 ** i) for i in range(len(sessions))],
            'volume': [100 for i in range(len(sessions))],
        }, index=sessions)

        unprofitable_frame = pd.DataFrame({
            'close': [10 * (0.999 ** i) for i in range(len(sessions))],
            'high': [10.5 * (0.999 ** i) for i in range(len(sessions))],
            'low': [9.5 * (0.999 ** i) for i in range(len(sessions))],
            'open': [10 * (0.999 ** i) for i in range(len(sessions))],
            'volume': [100 for i in range(len(sessions))],
        }, index=sessions)

        yield 0, flat_frame
        yield 1, profitable_frame
        yield 3, unprofitable_frame

    def test_margin_interest(self):
        test_algo = self.make_algo(
            script="""
import zipline.api as algo
from zipline.finance.slippage import NoSlippage
from zipline.finance.commission import NoCommission

def initialize(context):
    algo.set_margin_interest(0.05)
    algo.set_slippage(NoSlippage())
    algo.set_commission(NoCommission())
    context.invested = False

def handle_data(context, data):
    if not context.invested:
        algo.order_target_percent(algo.sid("FI0"), 2)
        context.invested = True
        """,
        )
        results = test_algo.run()

        # fees aren't assessed until first of the month, so the portfolio
        # value should be 100,000 until then.
        self.assertTrue(
            (results.portfolio_value.loc["2018-04"] == 100000).all()
        )
        self.assertTrue(
            (results.fees.loc["2018-04"] == 0).all()
        )

        # expected interest: $100,000 * 0.05 / 360 = $13.8889/day * 26 days = $361.11
        self.assertTrue(
            (results.portfolio_value.loc["2018-05"].round(3) == 99638.889).all()
        )
        # fee assessed on 1st day of month
        self.assertEqual(
            results.loc["2018-05"][['pnl', 'portfolio_value', 'fees']].round(3).iloc[0].to_dict(),
            {'pnl': -361.111, 'portfolio_value': 99638.889, 'fees': 361.111}
        )
        # no fee on 2nd day of month
        self.assertEqual(
            results.loc["2018-05"][['pnl', 'portfolio_value', 'fees']].round(3).iloc[1].to_dict(),
            {'pnl': 0.0, 'portfolio_value': 99638.889, 'fees': 0}
        )

        self.assertTrue(
            (results.portfolio_value.loc["2018-06"].round(3) == 99206.779).all()
        )
        self.assertEqual(
            results.loc["2018-06"][['pnl', 'portfolio_value', 'fees']].round(3).iloc[0].to_dict(),
            {'fees': 432.11, 'pnl': -432.11, 'portfolio_value': 99206.779}
        )
        # no fee on 2nd day of month
        self.assertEqual(
            results.loc["2018-06"][['pnl', 'portfolio_value', 'fees']].round(3).iloc[1].to_dict(),
            {'fees': 0.0, 'pnl': 0.0, 'portfolio_value': 99206.779}
        )

    def test_management_fee_with_date_rule(self):
        test_algo = self.make_algo(
            script="""
import zipline.api as algo
from zipline.finance.slippage import NoSlippage
from zipline.finance.commission import NoCommission

def initialize(context):
    algo.set_management_fee(0.02, date_rule=algo.date_rules.every_day())
    algo.set_slippage(NoSlippage())
    algo.set_commission(NoCommission())

def handle_data(context, data):
    pass
        """,
        )
        results = test_algo.run()
        # expected fee: $100,000 * 0.02 / 365 = $5.48/day
        results.index = results.index.strftime("%Y-%m-%d")
        self.assertEqual(
            results.portfolio_value.iloc[0:5].round(3).to_dict(),
            {'2018-04-04': 99994.521,
             '2018-04-05': 99989.041,
             '2018-04-06': 99983.563,
             # weekend accrual is 3x
             '2018-04-09': 99967.127,
             '2018-04-10': 99961.649}
        )

    def test_management_fee(self):
        test_algo = self.make_algo(
            script="""
import zipline.api as algo
from zipline.finance.slippage import NoSlippage
from zipline.finance.commission import NoCommission

def initialize(context):
    algo.set_management_fee(0.02)
    algo.set_slippage(NoSlippage())
    algo.set_commission(NoCommission())

def handle_data(context, data):
    pass
        """,
        )
        results = test_algo.run()

        # fees aren't assessed until first of the month, so the portfolio
        # value should be 100,000 until then.
        self.assertTrue(
            (results.portfolio_value.loc["2018-04"] == 100000).all()
        )
        # expected fee: $100,000 * 0.02 / 365 = $5.48/day x 28 days = $153.42
        self.assertTrue(
            (results.portfolio_value.loc["2018-05"].round(3) == 99846.575).all()
        )
        self.assertEqual(
            results.loc["2018-05"][['pnl', 'portfolio_value', 'fees']].round(3).iloc[0].to_dict(),
            {'pnl': -153.425, 'portfolio_value': 99846.575, 'fees': 153.425}
        )
        # expected fee: $99,846.575 * 0.02 / 365 = $5.47/day x 31 days = $169.60
        self.assertTrue(
            (results.portfolio_value.loc["2018-06"].round(3) == 99676.973).all()
        )

        self.assertEqual(
            results.loc["2018-06"][['pnl', 'portfolio_value', 'fees']].round(3).iloc[0].to_dict(),
            {'pnl': -169.602, 'portfolio_value': 99676.973, 'fees': 169.602}
        )

    def test_performance_fee(self):
        test_algo = self.make_algo(
            script="""
import zipline.api as algo
from zipline.finance.slippage import NoSlippage
from zipline.finance.commission import NoCommission

def initialize(context):
    algo.set_performance_fee(0.20)
    algo.set_slippage(NoSlippage())
    algo.set_commission(NoCommission())
    context.invested = False
    context.rotated = False

def handle_data(context, data):
    if not context.invested:
        # buy profitable sid
        algo.order_target_percent(algo.sid("FI1"), 1)
        context.invested = True

    if algo.get_datetime().month == 8 and not context.rotated:
        # sell profitable sid, buy unprofitable sid
        algo.order_target_percent(algo.sid("FI1"), 0)
        algo.order_target_percent(algo.sid("FI3"), 1)
        context.rotated = True
        """,
        )
        results = test_algo.run()

        # no fees in April, May, or June
        self.assertTrue(
            (results.fees.loc["2018-04"] == 0).all()
        )
        self.assertTrue(
            (results.fees.loc["2018-05"] == 0).all()
        )
        self.assertTrue(
            (results.fees.loc["2018-06"] == 0).all()
        )

        # cumulative pnl through June is $6,190.00
        total_pnl = results.pnl.loc[: "2018-06"].sum()
        self.assertEqual(total_pnl, 6190.00)

        # this yields a fee on the first day of July of $1,238
        self.assertEqual(
            results.loc["2018-07"].iloc[0].fees,
            1238.00
        )

        self.assertEqual(
            results.loc["2018-07"][['pnl', 'portfolio_value', 'fees']].round(3).iloc[0].to_dict(),
            {'fees': 1238.00, 'pnl': -1138.0, 'portfolio_value': 105052.0}
        )

        # the portfolio value is the prior day's portfolio value plus the
        # pnl
        prior_day_value = results.loc["2018-06"].iloc[-1].portfolio_value
        self.assertEqual(
            results.loc["2018-07"].iloc[0].portfolio_value,
            prior_day_value - 1138
        )

        # due to switching to a losing security and not hitting the
        # highwater mark, there are no further fees
        self.assertTrue(
            (results.fees.loc["2018-07":].iloc[1:] == 0).all()
        )

    def test_performance_fee_with_date_rule(self):
        test_algo = self.make_algo(
            script="""
import zipline.api as algo
from zipline.finance.slippage import NoSlippage
from zipline.finance.commission import NoCommission

def initialize(context):
    algo.set_performance_fee(0.20, date_rule=algo.date_rules.month_start())
    algo.set_slippage(NoSlippage())
    algo.set_commission(NoCommission())
    context.invested = False
    context.rotated = False
    context.rotated_again = False

def handle_data(context, data):
    if not context.invested:
        # buy profitable sid
        algo.order_target_percent(algo.sid("FI1"), 1)
        context.invested = True

    if algo.get_datetime().month == 6 and not context.rotated:
        # sell profitable sid, buy unprofitable sid
        algo.order_target_percent(algo.sid("FI1"), 0)
        algo.order_target_percent(algo.sid("FI3"), 1)
        context.rotated = True

    if algo.get_datetime().month == 7 and not context.rotated_again:
        # sell unprofitable sid, buy profitable sid
        algo.order_target_percent(algo.sid("FI3"), 0)
        algo.order_target_percent(algo.sid("FI1"), 1)
        context.rotated_again = True
        """,
        )
        results = test_algo.run()

        # no fees in April
        self.assertTrue(
            (results.fees.loc["2018-04"] == 0).all()
        )

        # cumulative pnl in April is $1720.0
        total_pnl = results.pnl.loc[: "2018-04"].sum()
        self.assertEqual(total_pnl, 1720.0)

        # this yields a fee on the first day of May of $344
        self.assertEqual(
            results.loc["2018-05"].iloc[0].fees,
            344
        )

        # cumulative pnl in May is $1916.0
        total_pnl = results.pnl.loc["2018-05"].sum()
        self.assertEqual(total_pnl, 1916.0)

        # this yields a fee on the first day of May of $383.2
        self.assertEqual(
            round(results.loc["2018-06"].iloc[0].fees, 2),
            383.20
        )

        # due to negative pnl in June, no fees in July
        self.assertEqual(
            results.loc["2018-07"].iloc[0].fees,
            0
        )

        # cumulative pnl in June and July is $-371.3
        total_pnl = results.pnl.loc["2018-06": "2018-07"].sum()
        self.assertEqual(round(total_pnl, 2), -371.3)

        # this yields a fee on the first day of Aug of $0
        self.assertEqual(
            round(results.loc["2018-08"].iloc[0].fees, 2),
            0
        )

        # cumulative pnl in June through Aug is $2040.55
        total_pnl = results.pnl.loc["2018-06": "2018-08"].sum()
        self.assertEqual(round(total_pnl, 2), 2040.55)

        # this yields a fee on the first day of Sept of $408
        self.assertEqual(
            round(results.loc["2018-09"].iloc[0].fees, 2),
            408.11
        )

    @patch("zipline.finance.fees.download_ibkr_borrow_fees")
    def test_borrow_fees(self, mock_download_ibkr_borrow_fees):

        test_algo = self.make_algo(
            script="""
import zipline.api as algo
from zipline.finance.slippage import NoSlippage
from zipline.finance.commission import NoCommission

def initialize(context):
    algo.set_borrow_fees_provider('ibkr')
    algo.set_slippage(NoSlippage())
    algo.set_commission(NoCommission())
    context.invested = False
    context.invested2 = False
    context.liquidated = False
    context.invested3 = False

def handle_data(context, data):
    if not context.invested:
        algo.order_target_percent(algo.sid("FI0"), -1)
        context.invested = True

    if algo.get_datetime().month == 5 and not context.invested2:
        algo.order_target_percent(algo.sid("FI1"), -1)
        # long position, borrow fees shouldn't be queried
        algo.order_target_percent(algo.sid("FI3"), 1)
        context.invested2 = True

    if algo.get_datetime().month == 7 and not context.liquidated:
        algo.order_target_percent(algo.sid("FI0"), 0)
        algo.order_target_percent(algo.sid("FI1"), 0)
        context.liquidated = True

    if algo.get_datetime().month == 8 and not context.invested3:
        # this will raise NoFundamentalData in the mocked function
        algo.order_target_percent(algo.sid("FI3"), -1)
        context.invested3 = True
        """,
        )

        def _mock_download_ibkr_borrow_fees(
                f, start_date=None, end_date=None,
                sids=None, **kwargs):

            if str(end_date) < "2018-04-16":
                raise ValueError("end_date should not have been earlier than 2018-04-16")

            # for this sid, simulate not data available
            if sids == ["FI3"]:
                raise NoFundamentalData("no data match the query parameters")

            data = []

            for sid in sids:
                fee = int(sid[2:]) + 1
                date = str(start_date)[:-2] + "01"
                if not date.endswith("01"):
                    # add a high fee to make sure we use the last
                    # data point per sid
                    data.append((date, sid, 1e10))
                data.append((date, sid, fee))

            fees = pd.DataFrame(data, columns=("Date", "Sid", "FeeRate"))
            fees.to_csv(f, index=False)
            f.seek(0)

        mock_download_ibkr_borrow_fees.side_effect = _mock_download_ibkr_borrow_fees

        results = test_algo.run()

        _, args, kwargs = mock_download_ibkr_borrow_fees.mock_calls[0]
        self.assertEqual(kwargs["sids"], ["FI0"])
        # queries are skipped until 2018-04-16, the data start date
        self.assertEqual(str(kwargs["end_date"]), "2018-04-16")
        # we should query back to the start of the month since data is sparse
        self.assertEqual(str(kwargs["start_date"]), "2018-04-01")

        # May 1 call
        _, args, kwargs = mock_download_ibkr_borrow_fees.mock_calls[10]
        self.assertEqual(kwargs["sids"], ["FI0"])
        self.assertEqual(str(kwargs["end_date"]), "2018-04-30")
        self.assertEqual(str(kwargs["start_date"]), "2018-04-01")

        # May 2 call
        _, args, kwargs = mock_download_ibkr_borrow_fees.mock_calls[11]
        self.assertEqual(kwargs["sids"], ["FI0"])
        self.assertEqual(str(kwargs["end_date"]), "2018-05-01")
        self.assertEqual(str(kwargs["start_date"]), "2018-05-01")

        # May 3 call, now querying two sids
        _, args, kwargs = mock_download_ibkr_borrow_fees.mock_calls[12]
        self.assertEqual(kwargs["sids"], ["FI0", "FI1"])
        self.assertEqual(str(kwargs["end_date"]), "2018-05-02")
        self.assertEqual(str(kwargs["start_date"]), "2018-05-01")

        # no fees assessed in April
        self.assertTrue((results.fees.loc["2018-04"] == 0).all())
        self.assertTrue((results.portfolio_value.loc["2018-04"] == 100000).all())

        # fees assessed on the first day in May
        # annual borrow fee = 1%
        # daily borrow fee % = 2.78e-05
        # shares -10000
        # share price 10.00
        # = $2.833 per day * 15 calendar days from the 16th to the 30th
        # = 42.50
        self.assertEqual(results.fees.loc["2018-05"].iloc[0], 42.5)
        self.assertEqual(results.portfolio_value.loc["2018-05"].iloc[0], 99957.5)
        # no further fees assessed in May
        self.assertTrue((results.fees.loc["2018-05"].iloc[1:] == 0).all())

        # fees assessed on the first day in June for both short positions
        # Sid 0: $2.833 per day * 31 calendar days
        # = 87.83
        # Sid 1:
        # annual borrow fee = 2%
        # daily borrow fee % = 5.56e-05}
        # shares -9807
        # share price rounded up 11
        # = $6.11 per day * 31 calendar days
        # = 189.50
        self.assertEqual(round(results.fees.loc["2018-06"].iloc[0], 2), 271.22)
        # no further fees assessed in June
        self.assertTrue((results.fees.loc["2018-06"].iloc[1:] == 0).all())

        # starting in August, we are short FI3, but it has no borrow fee data
        # available, so there are no fees
        self.assertTrue((results.fees.loc["2018-09"] == 0).all())
