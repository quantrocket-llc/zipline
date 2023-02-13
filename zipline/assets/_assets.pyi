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

class Asset:
    """
    Base class for entities that can be owned by a trading algorithm.

    Parameters
    ----------
    sid : int
        Internal Zipline sid. Persistent unique identifier assigned to the asset.
    zipline_sid: int
        Internal Zipline sid (alias for Asset.sid).
    real_sid: str
        The QuantRocket sid.
    symbol : str
        Most recent ticker under which the asset traded. This field can change
        without warning if the asset changes tickers. Use ``real_sid`` if you need a
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
        Date on which the asset first traded.
    end_date : pd.Timestamp
        Last date on which the asset traded. This value is set
        to the current (real time) date for assets that are still trading.
    tick_size : float
        Minimum amount that the price can change for this asset.
    multiplier : float
        The contract multiplier
    price_magnifier : float
        The price magnifier by which to divide prices when prices are quoted in a smaller
        unit than the asset's currency.
    auto_close_date : pd.Timestamp
        Date on which positions in this asset will be automatically liquidated
        to cash during a simulation. By default, this is three days after
        ``end_date``.
    """

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
