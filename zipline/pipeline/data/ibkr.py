# Copyright 2020 QuantRocket LLC - All Rights Reserved
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

from zipline.utils.numpy_utils import float64_dtype
from zipline.pipeline.data import Column, DataSet
from zipline.pipeline.data.dataset import BoundFloatColumn

class ShortableShares(DataSet):
    """
    DataSet representing the previous day's shortable shares.

    Attributes
    ----------
    MinQuantity : float
        minimum quantity of shortable shares for the day

    MaxQuantity : float
        maximum quantity of shortable shares for the day

    MeanQuantity : float
        average quantity of shortable shares for the day

    LastQuantity : float
        last quantity of shortable shares for the day

    Examples
    --------
    Get the number of shortable shares for the previous day:

    >>> shares = ibkr.ShortableShares.LastQuantity.latest    # doctest: +SKIP
    """
    MinQuantity: BoundFloatColumn = Column(float64_dtype)
    """minimum quantity of shortable shares for the day"""
    MaxQuantity: BoundFloatColumn = Column(float64_dtype)
    """maximum quantity of shortable shares for the day"""
    MeanQuantity: BoundFloatColumn = Column(float64_dtype)
    """average quantity of shortable shares for the day"""
    LastQuantity: BoundFloatColumn = Column(float64_dtype)
    """last quantity of shortable shares for the day"""

class BorrowFees(DataSet):
    """
    DataSet representing the previous day's borrow fees.

    Attributes
    ----------
    FeeRate : float
        The annualized interest rate on short positions. For example, 1.0198
        indicates an annualized interest rate of 1.0198%.

    Examples
    --------
    Get the previous day's borrow fees:

    >>> fees = ibkr.BorrowFee.FeeRate.latest    # doctest: +SKIP
    """
    FeeRate: BoundFloatColumn = Column(float64_dtype)
    """The annualized interest rate on short positions. For example, 1.0198
    indicates an annualized interest rate of 1.0198%."""
