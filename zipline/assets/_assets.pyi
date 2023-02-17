# Copyright 2022 QuantRocket LLC
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

import pandas as pd
from zipline.assets.exchange_info import ExchangeInfo

class Asset:
    """
    Base class for entities that can be owned by a trading algorithm.

    Parameters
    ----------
    sid : int
        Internal Zipline sid (security ID). For the QuantRocket sid, use real_sid.
    zipline_sid: int
        Internal Zipline sid (alias for Asset.sid). For the QuantRocket sid, use real_sid.
    real_sid: str
        The QuantRocket sid. Persistent unique identifier assigned to the asset.
    symbol : str
        Most recent ticker under which the asset traded. This field can change
        without warning if the asset changes tickers. Use ``real_sid`` for a
        persistent identifier.
    asset_name : str
        Full name of the asset.
    exchange : str
        Canonical short name of the exchange on which the asset trades (e.g.,
        'NYSE').
    exchange_full : str
        Full name of the exchange on which the asset trades (e.g., 'NEW YORK
        STOCK EXCHANGE').
    country_code : str
        Two character code indicating the country in which the asset trades.
    currency : str
        ISO currency of asset.
    start_date : pd.Timestamp
        First date for which price data is available for this asset
    end_date : pd.Timestamp
        Last date for which price data is available for this asset
    multiplier : float
        The contract multiplier
    price_magnifier : float
        The price magnifier by which to divide prices when prices are quoted in a smaller
        unit than the asset's currency. Rarely used.
    auto_close_date : pd.Timestamp
        Delisted date for equities, or last trade date for futures.
    """
    def __init__(
        self,
        sid: int,
        real_sid: str,
        symbol: str,
        asset_name: str,
        exchange_info: ExchangeInfo,
        currency: str,
        start_date: pd.Timestamp,
        end_date: pd.Timestamp,
        first_traded: pd.Timestamp,
        auto_close_date: pd.Timestamp,
        tick_size: float,
        multiplier: float,
        price_magnifier: float
        ):

        self.sid: int = sid
        """Internal Zipline sid (security ID). For the QuantRocket sid, use real_sid."""
        self.zipline_sid: int = sid
        """Internal Zipline sid (alias for Asset.sid). For the QuantRocket sid, use real_sid."""
        self.real_sid : str = real_sid
        """The QuantRocket sid. Persistent unique identifier assigned to the asset."""
        self.symbol: str = symbol
        """Most recent ticker under which the asset traded. This field can change without warning if the asset changes tickers. Use ``real_sid`` for a persistent identifier."""
        self.asset_name: str = asset_name
        """Full name of the asset."""
        self.exchange: str = None
        """Canonical short name of the exchange on which the asset trades (e.g.,
        'NYSE')."""
        self.exchange_full: str = None
        """Full name of the exchange on which the asset trades (e.g., 'NEW YORK
        STOCK EXCHANGE')."""
        self.exchange_info: ExchangeInfo = exchange_info
        """ExchangeInfo object."""
        self.currency: str = currency
        """ISO currency of asset."""
        self.start_date: pd.Timestamp = start_date
        """First date for which price data is available for this asset."""
        self.end_date: pd.Timestamp = end_date
        """Last date for which price data is available for this asset."""
        self.auto_close_date: pd.Timestamp = auto_close_date
        """Delisted date for equities, or last trade date for futures."""
        self.price_multiplier: float = multiplier
        """The contract multiplier"""
        self.price_magnifier: float = price_magnifier
        """The price magnifier by which to divide prices when prices are quoted in a smaller unit than the asset's currency. Rarely used."""

    def from_dict(cls, dict_):
        """
        Build an Asset instance from a dict.
        """
        ...

    def is_alive_for_session(self, session_label: pd.Timestamp) -> bool:
        """
        Returns whether the asset is alive at the given dt.

        Parameters
        ----------
        session_label: pd.Timestamp
            The desired session label to check. (midnight UTC)

        Returns
        -------
        boolean: whether the asset is alive at the given dt.
        """
        ...

    def is_exchange_open(self, dt_minute: pd.Timestamp) -> bool:
        """
        Parameters
        ----------
        dt_minute: pd.Timestamp (UTC, tz-aware)
            The minute to check.

        Returns
        -------
        boolean: whether the asset's exchange is open at the given minute.
        """
        ...

class Equity(Asset):
    """
    Asset subclass representing partial ownership of a company, trust, or
    partnership.
    """
    ...

class Future(Asset):
    """Asset subclass representing ownership of a futures contract.

    See Also
    --------
    zipline.api.continuous_future - Create a specifier for a continuous contract.
    """

    def to_dict(self):
        """
        Convert to a python dict.
        """
        ...

def make_asset_array(size, asset): ...
