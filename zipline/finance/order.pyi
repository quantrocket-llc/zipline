#
# Copyright 2023 QuantRocket LLC
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
from typing import Literal
import pandas as pd
from zipline.assets import Asset
from enum import Enum

class ORDER_STATUS(Enum):
    OPEN = 0
    FILLED = 1
    CANCELLED = 2
    REJECTED = 3
    HELD = 4

class Order:
    """
    An order placed by an algorithm.

    Attributes
    ----------
    id : str
        order ID

    dt : pd.Timestamp
        datetime that the order was placed

    asset : zipline.assets.Asset
        asset for the order.

    amount : int
        the number of shares to buy/sell. A positive sign indicates
        a buy, and a negative sign indicates a sell.

    filled : int
        how many shares of the order have been filled so far

    commission : float
        the commission paid for this order

    stop : float
        stop price for the order

    limit : float
        limit price for the order

    stop_reached : bool
        whether the stop price has been reached

    limit_reached : bool
        whether the limit price has been reached

    direction : int
        the direction of the order, 1 for buy, -1 for sell

    status : int
        the status of the order. To check for a certain status,
        compare the status to `zipline.finance.order.ORDER_STATUS`.
        Possible choices: ORDER_STATUS.OPEN, ORDER_STATUS.FILLED,
        ORDER_STATUS.CANCELLED, ORDER_STATUS.REJECTED,
        ORDER_STATUS.HELD.

    open : bool
        whether the order is currently open

    open_amount : int
        the number of shares that are still open for this order
    """
    def __init__(
        self,
        dt: pd.Timestamp,
        asset: Asset,
        amount: int,
        stop: float = None,
        limit: float = None,
        filled: int = 0,
        commission: float = 0,
        id: str = None
        ):

        # get a string representation of the uuid.
        self.id: str = ...
        """Order ID"""
        self.dt: pd.Timestamp = ...
        """Datetime that the order was placed"""
        self.reason: str = ...
        """For rejected or held orders, the reason the order was rejected or held, if available"""
        self.created: pd.Timestamp = ...
        """Datetime that the order was created"""
        self.asset: Asset = ...
        """Asset for the order"""
        self.amount: int = ...
        """The number of shares to buy/sell. A positive sign indicates a buy, and a negative sign indicates a sell."""
        self.filled: int = ...
        """How many shares of the order have been filled so far"""
        self.commission: float = ...
        """The commission paid for this order"""
        self.stop: float = ...
        """Stop price for the order"""
        self.limit: float = ...
        """Limit price for the order"""
        self.stop_reached: bool = ...
        """Whether the stop price has been reached"""
        self.limit_reached: bool = ...
        """Whether the limit price has been reached"""
        self.direction: int = ...
        """The direction of the order, 1 for buy, -1 for sell"""

    @property
    def sid(self) -> Asset:
        """The asset (not sid) for this order. For backwards compatibility."""
        ...

    @property
    def status(self) -> Literal[
        ORDER_STATUS.OPEN,
        ORDER_STATUS.FILLED,
        ORDER_STATUS.CANCELLED,
        ORDER_STATUS.REJECTED,
        ORDER_STATUS.HELD]:
        """
        The status of the order. To check for a certain status, compare the status
        to `zipline.api.ORDER_STATUS`. Possible choices:

        - ORDER_STATUS.OPEN
        - ORDER_STATUS.FILLED
        - ORDER_STATUS.CANCELLED
        - ORDER_STATUS.REJECTED
        - ORDER_STATUS.HELD
        """
        ...

    @property
    def open(self) -> bool:
        """
        Whether the order is currently open.
        """
        ...

    @property
    def triggered(self) -> bool:
        """
        Whether the order has been triggered.

        For a market order, always True.
        For a stop order, True IFF stop_reached.
        For a limit order, True IFF limit_reached.
        """
        ...

    @property
    def open_amount(self) -> int:
        """The number of shares that are still open for this order."""
        ...
