import pandas as pd

from zipline._testing import (
    MockDailyBarReader,
    create_daily_df_for_asset,
    create_minute_df_for_asset,
    str_to_seconds,
)
from zipline._testing.fixtures import (
    WithCreateBarData,
    WithMakeAlgo,
    ZiplineTestCase,
)

reference_missing_position_by_unexpected_type_algo = """
def initialize(context):
    pass

def handle_data(context, data):
    context.portfolio.positions["foobar"]
"""


class TestAPIShim(WithCreateBarData,
                  WithMakeAlgo,
                  ZiplineTestCase):

    START_DATE = pd.Timestamp("2016-01-05", tz='UTC')
    END_DATE = pd.Timestamp("2016-01-28", tz='UTC')
    SIM_PARAMS_DATA_FREQUENCY = 'minute'

    sids = ASSET_FINDER_EQUITY_SIDS = 1, 2, 3

    @classmethod
    def make_equity_minute_bar_data(cls):
        for sid in cls.sids:
            yield sid, create_minute_df_for_asset(
                cls.trading_calendar,
                cls.SIM_PARAMS_START,
                cls.SIM_PARAMS_END,
            )

    @classmethod
    def make_equity_daily_bar_data(cls, country_code, sids):
        for sid in sids:
            yield sid, create_daily_df_for_asset(
                cls.trading_calendar,
                cls.SIM_PARAMS_START,
                cls.SIM_PARAMS_END,
            )

    @classmethod
    def make_splits_data(cls):
        return pd.DataFrame([
            {
                'effective_date': str_to_seconds('2016-01-06'),
                'ratio': 0.5,
                'sid': 3,
            }
        ])

    @classmethod
    def make_adjustment_writer_equity_daily_bar_reader(cls):
        return MockDailyBarReader(
            dates=cls.nyse_calendar.sessions_in_range(
                cls.START_DATE,
                cls.END_DATE,
            ),
        )

    @classmethod
    def init_class_fixtures(cls):
        super(TestAPIShim, cls).init_class_fixtures()

        cls.asset1 = cls.asset_finder.retrieve_asset(1)
        cls.asset2 = cls.asset_finder.retrieve_asset(2)
        cls.asset3 = cls.asset_finder.retrieve_asset(3)

    def create_algo(self, code, filename=None, sim_params=None):
        if sim_params is None:
            sim_params = self.sim_params

        return self.make_algo(
            script=code,
            sim_params=sim_params,
            algo_filename=filename
        )

    def test_reference_empty_position_by_unexpected_type(self):

        with self.assertRaises(ValueError) as cm:

            algo = self.create_algo(
                reference_missing_position_by_unexpected_type_algo
            )
            algo.run()

        self.assertEqual(
            str(cm.exception),
            "Position lookup expected a value of type Asset but got str"
            " instead."
        )
