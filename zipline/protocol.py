#
# Copyright 2016 Quantopian, Inc.
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
from typing import TYPE_CHECKING

import pandas as pd
from enum import Enum
from .assets import Asset
from ._protocol import BarData as BarData, InnerPosition  # noqa


class MutableView(object):
    """A mutable view over an "immutable" object.

    Parameters
    ----------
    ob : any
        The object to take a view over.
    """
    # add slots so we don't accidentally add attributes to the view instead of
    # ``ob``
    __slots__ = ('_mutable_view_ob',)

    def __init__(self, ob):
        object.__setattr__(self, '_mutable_view_ob', ob)

    def __getattr__(self, attr):
        return getattr(self._mutable_view_ob, attr)

    def __setattr__(self, attr, value):
        vars(self._mutable_view_ob)[attr] = value

    def __repr__(self):
        return '%s(%r)' % (type(self).__name__, self._mutable_view_ob)


# Datasource type should completely determine the other fields of a
# message with its type.
DATASOURCE_TYPE = Enum(
    'DATASOURCE_TYPE',
    ['AS_TRADED_EQUITY',
    'MERGER',
    'SPLIT',
    'DIVIDEND',
    'TRADE',
    'TRANSACTION',
    'ORDER',
    'EMPTY',
    'DONE',
    'CUSTOM',
    'BENCHMARK',
    'COMMISSION',
    'CLOSE_POSITION']
)

# Expected fields/index values for a dividend Series.
DIVIDEND_FIELDS = [
    'declared_date',
    'ex_date',
    'gross_amount',
    'net_amount',
    'pay_date',
    'payment_sid',
    'ratio',
    'sid',
]
# Expected fields/index values for a dividend payment Series.
DIVIDEND_PAYMENT_FIELDS = [
    'id',
    'payment_sid',
    'cash_amount',
    'share_count',
]


class Event(object):

    def __init__(self, initial_values=None):
        if initial_values:
            self.__dict__.update(initial_values)

    def keys(self):
        return self.__dict__.keys()

    def __eq__(self, other):
        return hasattr(other, '__dict__') and self.__dict__ == other.__dict__

    def __contains__(self, name):
        return name in self.__dict__

    def __repr__(self):
        return "Event({0})".format(self.__dict__)

    def to_series(self, index=None):
        return pd.Series(self.__dict__, index=index)

class Order(Event):
    pass

class Portfolio(object):
    """Object providing read-only access to current portfolio state.
    Available in algorithms via `context.portfolio`.

    Attributes
    ----------
    positions : dict-like of :class:`zipline.assets.Asset` to :class:`zipline.protocol.Position`
        Dict-like object where the keys are assets and the values contain information about the
        currently-held position for that asset.

    cash : float
        Amount of cash currently held in portfolio.

    cash_flow : float
        The change in cash over the lifetime of the portfolio.

    portfolio_value : float
        Current liquidation value of the portfolio's holdings.
        This is equal to ``cash + sum(shares * price)``

    starting_cash : float
        Amount of cash in the portfolio at the start of the backtest.

    positions_value : float
        The net value of all positions in the portfolio.

    positions_exposure : float
        The net exposure of all positions in the portfolio.

    start_date : pd.Timestamp
        The start date for the period being recorded.

    pnl : float
        The portfolio's profit and loss for the period being recorded.

    returns : float
        The portfolio's returns for the period being recorded.

    Examples
    --------
    Check the current portfolio value::

        portfolio_value = context.portfolio.portfolio_value

    Print the current positions::

        for asset, position in context.portfolio.positions.items():
            print(asset, position.amount)
    """

    def __init__(
        self,
        start_date: pd.Timestamp = None,
        capital_base: float = 0.0
        ):
        self = MutableView(self)
        self.cash_flow: float = 0.0
        """The change in cash over the lifetime of the portfolio."""
        self.starting_cash: float = capital_base
        """Amount of cash in the portfolio at the start of the backtest."""
        self.portfolio_value: float = capital_base
        """Current liquidation value of the portfolio's holdings. This is equal to ``cash + sum(shares * price)``"""
        self.pnl: float = 0.0
        """The portfolio's profit and loss for the period being recorded."""
        self.returns: float = 0.0
        """The portfolio's returns for the period being recorded."""
        self.cash: float = capital_base
        """Amount of cash currently held in portfolio."""
        self.positions: dict[Asset, Position] = Positions()
        """
        Dict-like object where the keys are assets and the values contain
        information about the currently-held position for that asset.

        Examples
        --------
        >>> for asset, position in context.portfolio.positions.items():
        ...     print(asset, position.amount)
        """
        self.start_date: pd.Timestamp = start_date
        """The start date for the period being recorded."""
        self.positions_value: float = 0.0
        """The net value of all positions in the portfolio."""
        self.positions_exposure: float = 0.0
        """The net exposure of all positions in the portfolio."""

    @property
    def capital_used(self) -> float:
        return self.cash_flow

    def __setattr__(self, attr, value):
        raise AttributeError('cannot mutate Portfolio objects')

    def __repr__(self):
        return "Portfolio({0})".format(self.__dict__)

    @property
    def current_portfolio_weights(self) -> 'pd.Series[float]':
        """
        Compute each asset's weight in the portfolio by calculating its held
        value divided by the total value of all positions.

        Each equity's value is its price times the number of shares held. Each
        futures contract's value is its unit price times number of shares held
        times the multiplier.

        Returns
        -------
        weights : pd.Series[float]
            Series mapping each asset to its weight in the portfolio.
        """
        position_values = pd.Series({
            asset: (
                    position.last_sale_price *
                    position.amount *
                    asset.price_multiplier
            )
            for asset, position in self.positions.items()
        }, dtype="float64")
        return position_values / self.portfolio_value


class Account(object):
    """
    The account object tracks information about the trading account.
    The values are updated as the algorithm runs and its keys remain
    unchanged. These values are calculated by Zipline based on the
    algorithm's capital base and order activity and do not reflect the
    actual values of the broker.

    Available in algorithms via `context.account`.

    Attributes
    ----------
    settled_cash : float
        the amount of settled cash in the account

    accrued_interest : float

    buying_power : float

    equity_with_loan : float
        the portfolio value plus any cash in the account

    total_positions_value : float
        the value of all positions

    total_positions_exposure : float
        the total exposure of all positions in the portfolio

    regt_equity : float

    regt_margin : float

    initial_margin_requirement : float

    maintenance_margin_requirement : float

    available_funds : float

    excess_liquidity : float

    cushion : float

    day_trades_remaining : float

    leverage : float
        the gross leverage of the account, that is, the gross value of all positions
        divided by the account value

    net_leverage : float
        the net leverage of the account, that is, the net value of all positions
        divided by the account value

    net_liquidation : float
        the total account value
    """

    def __init__(self):
        self = MutableView(self)
        self.settled_cash: float = 0.0
        """The amount of settled cash in the account."""
        self.accrued_interest: float = 0.0
        self.buying_power: float = float('inf')
        self.equity_with_loan: float = 0.0
        """The portfolio value plus any cash in the account."""
        self.total_positions_value: float = 0.0
        """The value of all positions."""
        self.total_positions_exposure: float = 0.0
        """The total exposure of all positions in the portfolio."""
        self.regt_equity: float = 0.0
        self.regt_margin: float = float('inf')
        self.initial_margin_requirement: float = 0.0
        self.maintenance_margin_requirement: float = 0.0
        self.available_funds: float = 0.0
        self.excess_liquidity: float = 0.0
        self.cushion: float = 0.0
        self.day_trades_remaining: float = float('inf')
        self.leverage: float = 0.0
        """The gross leverage of the account, that is, the gross value of all positions divided by the account value."""
        self.net_leverage: float = 0.0
        """The net leverage of the account, that is, the net value of all positions divided by the account value."""
        self.net_liquidation: float = 0.0
        """The total account value."""

    def __setattr__(self, attr, value):
        raise AttributeError('cannot mutate Account objects')

    def __repr__(self):
        return "Account({0})".format(self.__dict__)

class Position(object):
    """
    A position held by an algorithm. Accessible via `context.portfolio.positions`.

    Attributes
    ----------
    asset : zipline.assets.Asset
        The held asset.

    amount : int
        Number of shares held. Short positions are represented with negative
        values.

    cost_basis : float
        Average price at which currently-held shares were acquired.

    last_sale_price : float
        Most recent price for the position.

    last_sale_date : pd.Timestamp
        Datetime at which ``last_sale_price`` was last updated.

    Examples
    --------
    Print the current positions in the portfolio::

        for asset, position in context.portfolio.positions.items():
            print(asset, position.amount)
    """
    __slots__ = ('_underlying_position',)

    def __init__(self, underlying_position):
        object.__setattr__(self, '_underlying_position', underlying_position)

        if TYPE_CHECKING:
            self.asset: Asset = None
            """The held asset."""
            self.amount: int = 0
            """Number of shares held. Short positions are represented with negative
            values."""
            self.cost_basis: float = 0.0
            """Average price at which currently-held shares were acquired."""
            self.last_sale_price: float = 0.0
            """Most recent price for the position."""
            self.last_sale_date: pd.Timestamp = None
            """Datetime at which ``last_sale_price`` was last updated."""

    def __getattr__(self, attr):
        return getattr(self._underlying_position, attr)

    def __setattr__(self, attr, value):
        raise AttributeError('cannot mutate Position objects')

    @property
    def sid(self) -> Asset:
        """
        Alias for ``asset`` for backwards compatibility.
        """
        return self.asset

    def __repr__(self):
        return 'Position(%r)' % {
            k: getattr(self, k)
            for k in (
                'asset',
                'amount',
                'cost_basis',
                'last_sale_price',
                'last_sale_date',
            )
        }

class Positions(dict):
    """A dict-like object containing the algorithm's current positions.
    """

    def __missing__(self, key):
        if isinstance(key, Asset):
            return Position(InnerPosition(key))

        raise ValueError(
            "Position lookup expected a value of type Asset but got {0}"
            " instead.".format(type(key).__name__))
