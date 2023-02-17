#
# Copyright 2014 Quantopian, Inc.
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

# Note that part of the API is implemented in TradingAlgorithm as
# methods (e.g. order). These are added to this namespace via the
# decorator ``api_method`` inside of algorithm.py.
from zipline.finance import (
    asset_restrictions,
    commission,
    execution,
    slippage,
    cancel_policy
)
from zipline.finance.cancel_policy import (
    NeverCancel,
    EODCancel
)
from zipline.finance.slippage import (
    FixedSlippage, # noqa: backward compat
    FixedBasisPointsSlippage, # noqa: backward compat
    VolumeShareSlippage, # noqa: backward compat
)
from zipline.finance.order import ORDER_STATUS
from zipline.utils.events import (
    date_rules,
    time_rules
)
from zipline.protocol import BarData

# The user interacts with zipline.algorithm.TradingAlgorithm via zipline.api
# functions and via the context object, which provides access to the account
# and portfolio objects and allows storage of arbitrary values. The Context
# class below cannot be used directly, but is used to document the context
# object passed to initialize(), handle_data(), before_trading_start(), and
# scheduled functions. See api.pyi for the actual documentation.
context_not_impl_msg = (
    "The Context class is only used for type hints for autocomplete and cannot be "
    "used directly, please use the `context` object passed to initialize(), "
    "handle_data(), before_trading_start(), and scheduled functions."
)
class Context:

    def __init__(self):
        raise NotImplementedError(context_not_impl_msg)

    def __setattr__(self, name, value):
        raise NotImplementedError(context_not_impl_msg)

    def __getattr__(self, name):
        raise NotImplementedError(context_not_impl_msg)

    @property
    def recorded_vars(self):
        raise NotImplementedError(context_not_impl_msg)

    @property
    def portfolio(self):
        raise NotImplementedError(context_not_impl_msg)

    @property
    def account(self):
        raise NotImplementedError(context_not_impl_msg)

__all__ = [
    'asset_restrictions',
    'cancel_policy',
    'commission',
    'execution',
    'slippage',
    'date_rules',
    'time_rules',
    'Context',
    'BarData',
    'attach_pipeline',
    'batch_market_order',
    'cancel_order',
    'continuous_future',
    'future_symbol',
    'get_datetime',
    'get_environment',
    'get_open_orders',
    'get_order',
    'order',
    'order_percent',
    'order_target',
    'order_target_percent',
    'order_target_value',
    'order_value',
    'pipeline_output',
    'record',
    'set_realtime_db',
    'schedule_function',
    'set_asset_restrictions',
    'set_benchmark',
    'set_cancel_policy',
    'EODCancel',
    'NeverCancel',
    'set_commission',
    'set_long_only',
    'set_max_leverage',
    'set_max_order_count',
    'set_max_order_size',
    'set_max_position_size',
    'set_min_leverage',
    'set_slippage',
    'sid',
    'ORDER_STATUS',
]
