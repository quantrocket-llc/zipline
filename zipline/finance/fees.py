import io
import pandas as pd
import math
from quantrocket.fundamental import download_ibkr_borrow_fees, NoFundamentalData
from zipline.utils.events import date_rules

class FeeTracker:

    def __init__(self, calendar, ledger):
        self.fee_models = {}
        self.calendar = calendar
        self.ledger = ledger

    def add_model(self, model):
        # associate the model's date rule with the calendar
        model.date_rule.cal = self.calendar
        self.fee_models[model.__class__.__name__] = model

    def accrue(self, dt):
        for model in self.fee_models.values():
            model.accrue(dt)

    def assess(self, dt):
        for model in self.fee_models.values():
            if model.date_rule.should_trigger(dt):
                accrued = model.accrued
                self.ledger.process_fee(accrued)
                model.accrued = 0.0

class FeeModel:

    def __init__(self, date_rule=None) -> None:
        # the date rule for when fees are assessed (fees
        # always accrue daily)
        self.date_rule = date_rule or date_rules.month_start()
        self.accrued = 0.0

    def accrue(self, dt):
        """
        This method runs daily and should calculate daily fees and
        increment the accrued attribute. Positive values of self.accrued
        will be debited as fees when assessed.
        """
        raise NotImplementedError("subclasses must implement accrue")

class MarginInterest(FeeModel):

    def __init__(self, rate, account, calendar):
        self.rate = rate
        self.daily_rate = rate / 360
        self.account = account
        self.calendar = calendar
        super().__init__()

    def accrue(self, dt):
        cash = self.account.settled_cash
        if cash >= 0:
            return

        today_session = self.calendar.minute_to_session(dt)
        previous_session = self.calendar.previous_session(today_session)
        # count the days since the last session (weekend margin interest is 3x)
        days_since_last_session = (today_session - previous_session).days

        interest = abs(cash) * self.daily_rate * days_since_last_session
        self.accrued += interest

class IBKRBorrowFees(FeeModel):

    def __init__(self, portfolio, calendar):
        self.portfolio = portfolio
        self.calendar = calendar
        super().__init__()

    def accrue(self, dt):

        today_session = self.calendar.minute_to_session(dt)

        # borrow fees are only available starting on 2018-04-16,
        # skip until 2018-04-17 because we query by previous session
        if today_session < pd.Timestamp("2018-04-17"):
            return

        short_positions = {
            asset: position
            for asset, position in self.portfolio.positions.items()
            if position.amount < 0}

        if not short_positions:
            return

        previous_session = self.calendar.previous_session(today_session)

        # query borrow fees for previous session
        f = io.StringIO()
        try:
            download_ibkr_borrow_fees(
                f,
                sids=[asset.real_sid for asset in short_positions],
                # query back to the first of month, since borrow fees are stored sparsely: https://qrok.it/dl/qr/ibkr-short
                start_date=previous_session.replace(day=1).date(),
                end_date=previous_session.date()
            )
        except NoFundamentalData:
                return

        borrow_fees = pd.read_csv(f, parse_dates=["Date"])
        borrow_fees = borrow_fees.sort_values("Date").drop_duplicates('Sid', keep="last")
        borrow_fees = borrow_fees.set_index("Sid").FeeRate

        # convert to decimals
        borrow_fees = borrow_fees / 100
        # convert to daily rates
        daily_borrow_fees = borrow_fees / 360 # industry convention is to divide annual fee by 360, not 365

        # count the days since the last session (weekend borrow fees are 3x)
        days_since_last_session = (today_session - previous_session).days

        daily_borrow_fees = daily_borrow_fees.to_dict()

        for asset, short_position in short_positions.items():

            if asset.real_sid not in daily_borrow_fees:
                continue

            asset_borrow_fee = (
                # the assessed borrow fee for this sid is the daily borrow fee rate...
                daily_borrow_fees[asset.real_sid]
                # ...multiplied by the position value (with share price rounded up to nearest dollar)...
                * abs(short_position.amount) * math.ceil(short_position.last_sale_price)
                # ...multiplied by 102% (by industry convention)...
                * 1.02
                # ...multiplied by the number of days since the last session
                * days_since_last_session
            )
            self.accrued += asset_borrow_fee

class ManagementFee(FeeModel):

    def __init__(self, fee_pct, portfolio, date_rule, calendar):
        self.fee_pct = fee_pct
        self.daily_pct = fee_pct / 365
        self.portfolio = portfolio
        self.calendar = calendar
        super().__init__(date_rule=date_rule)

    def accrue(self, dt):

        today_session = self.calendar.minute_to_session(dt)
        previous_session = self.calendar.previous_session(today_session)
        # count the days since the last session (weekend margin interest is 3x)
        days_since_last_session = (today_session - previous_session).days

        fee = self.portfolio.portfolio_value * self.daily_pct * days_since_last_session
        self.accrued += fee

class PerformanceFee(FeeModel):

    def __init__(self, fee_pct, portfolio, date_rule):
        self.fee_pct = fee_pct
        self.portfolio = portfolio
        self.pnl_highwater = 0.0
        super().__init__(date_rule=date_rule)

    def accrue(self, dt):
        # performance fees don't accrue until they are assessed;
        # otherwise, a performance fee would be assessed on a
        # mid-year or mid-quarter profit that subsequently disappears
        if not self.date_rule.should_trigger(dt):
            return

        cumulative_pnl = self.portfolio.pnl
        if cumulative_pnl <= self.pnl_highwater:
            return

        performance_fee = self.fee_pct * (cumulative_pnl - self.pnl_highwater)
        self.accrued += performance_fee
        self.pnl_highwater = cumulative_pnl
