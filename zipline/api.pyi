"""
Zipline Algorithm API.

The functions in this module are intended to be used within the context of
a Zipline algorithm. To use Zipline outside of the context of an algorithm,
see the `zipline.research` and `zipline.pipeline` modules.

Functions
---------
attach_pipeline
    Register a pipeline to be computed at the start of each day.

batch_market_order
    Place a batch market order for multiple assets.

cancel_order
    Cancel an open order.

continuous_future
    Create a continuous future from a specified root symbol.

future_symbol
    Lookup a futures contract with a given symbol.

get_datetime
    Get the current simulation datetime.

get_environment
    Query the execution environment (such as the date range, data frequency,
    and whether a backtest or live trading is running).

get_open_orders
    Retrieve all of the current open orders.

get_order
    Lookup an order based on the order id returned from one of the
    order functions.

order
    Place an order.

order_percent
    Place an order in the specified asset corresponding to the given
    percent of the current portfolio value.

order_target
    Place an order to adjust a position to a target number of shares.

order_target_percent
    Place an order to adjust a position to a target percent of the
    current portfolio value.

order_target_value
    Place an order to adjust a position to a target value.

order_value
    Place an order for a fixed amount of money.

pipeline_output
    Get the results of a pipeline specified by name.

capital_change
    Simulate a deposit or withdrawal from the algorithm's cash.

record
    Track and record values each day.

schedule_function
    Schedule a function to be called repeatedly in the future.

set_asset_restrictions
    Set a restriction on which assets can be ordered.

set_benchmark
    Set the benchmark asset.

set_cancel_policy
    Set the order cancellation policy for the simulation.

set_commission
    Set the commission models for the simulation.

set_long_only
    Set a rule specifying that this algorithm cannot take short
    positions.

set_max_leverage
    Set a limit on the maximum leverage of the algorithm.

set_max_order_count
    Set a limit on the number of orders that can be placed in a single
    day.

set_max_order_size
    Set a limit on the number of shares and/or dollar value of any single
    order placed for a specified asset.

set_max_position_size
    Set a limit on the number of shares and/or dollar value held for a
    given `asset`.

set_min_leverage
    Set a limit on the minimum leverage of the algorithm.

set_realtime_db
    Set the realtime database to use for querying up-to-date minute bars in
    live trading.

set_slippage
    Set the slippage models for the simulation.

set_management_fee
    Set the management fee for the simulation.

set_performance_fee
    Set the performance fee for the simulation.

set_margin_interest
    Set the margin interest rate for the simulation.

set_borrow_fees_provider
    Set the data provider whose borrow fee data will be used for
    debiting borrow fees on short positions during the simulation.

sid
    Lookup an Asset by its unique asset identifier.

symbol
    Lookup an Equity by its ticker symbol.

Classes
-------
Asset
    Base class for all assets.

BarData
    The data object passed to handle_data(), before_trading_start(), and
    scheduled functions. Provides methods for accessing minutely and daily
    price/volume data from Algorithm API functions.

Context
    The context object passed to initialize(), handle_data(), before_trading_start(), and
    scheduled functions. Provides access to the account and portfolio as well as any
    custom variables saved by the user.

date_rules
    Factories for date-based rules for `zipline.api.schedule_function`.

EODCancel
    Order cancellation policy that cancels orders at the end of the day.

NeverCancel
    Order cancellation policy that never cancels orders.

time_rules
    Factories for time-based rules for `zipline.api.schedule_function`.

Constants
---------
ORDER_STATUS
    enumeration of possible order statuses.

Modules
-------
asset_restrictions
    Classes for restricting trading of assets.

commission
    Commission models for simulations.

execution
    Execution styles (aka order types) for simulations.

slippage
    Slippage models for simulations.

Notes
-----
Usage Guide:

* Algorithm API: https://qrok.it/dl/z/zipline-algo
"""
from typing import Union, Callable, Literal, overload, Any, TypeVar
import pandas as pd
from zipline.assets import Asset, Future, ContinuousFuture
from zipline.finance import (
    asset_restrictions,
    commission,
    execution,
    slippage,
    cancel_policy
)
from zipline.finance.order import ORDER_STATUS
from zipline.pipeline import Pipeline
from zipline.protocol import Account, Portfolio
from zipline._protocol import BarData
from zipline.finance.order import Order
from zipline.utils.events import EventRule

__all__ = [
    'asset_restrictions',
    'cancel_policy',
    'commission',
    'execution',
    'slippage',
    'date_rules',
    'time_rules',
    'Asset',
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
    'capital_change',
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
    'set_management_fee',
    'set_performance_fee',
    'set_margin_interest',
    'set_borrow_fees_provider',
    'sid',
    'symbol',
    'ORDER_STATUS',
]

# The user interacts with zipline.algorithm.TradingAlgorithm via zipline.api
# functions and via the context object, which provides access to the account
# and portfolio objects and allows storage of arbitrary values. The Context
# class below cannot be used directly, but is used to document the context
# object passed to initialize(), handle_data(), before_trading_start(), and
# scheduled functions. The reason this class exists is to provide type hints,
# as the TradingAlgorithm class contains many methods not relevant to the user.
class Context:
    """
    The `context` object is passed to `initialize()`, `handle_data()`,
    `before_trading_start()`, and scheduled functions, and provides access to
    the account and portfolio as well as any custom variables saved by the
    user.

    Attributes
    ----------
    portfolio : :class:`zipline.protocol.Portfolio`
        The current portfolio.

    account : :class:`zipline.protocol.Account`
        The current account.

    recorded_vars : dict
        A copy of the variables that have been recorded using
        zipline.api.record().

    Notes
    -----
    Usage Guide:

    * Initialize: https://qrok.it/dl/z/zipline-init
    * Context object type hints: https://qrok.it/dl/z/zipline-context-type-hints

    Examples
    --------
    Save a variable to the context object::

        import zipline.api as algo

        def initialize(context: algo.Context):
            context.my_var = 1

    Print the current portfolio value and the current positions::

        def handle_data(context: algo.Context, data: algo.BarData):

            print(context.portfolio.portfolio_value)

            for asset, position in context.portfolio.positions.items():
                print(asset, position.amount)
    """

    # This will make pyright allow assignment to context.x
    def __setattr__(self, name: Any, value: Any) -> None:
        ...

    # This will make pyright allow access to any context.x
    def __getattr__(self, name: Any) -> Any:
        ...

    @property
    def recorded_vars(self) -> dict[str, Any]:
        """
        A copy of the variables that have been recorded
        using the `zipline.api.record()` function."""
        ...

    @property
    def portfolio(self) -> Portfolio:
        """
        The current portfolio.

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
        """
        ...

    @property
    def account(self) -> Account:
        """
        The current account details.

        The values are updated as the algorithm runs and its keys remain
        unchanged. These values are calculated by Zipline based on the
        algorithm's capital base and order activity and do not reflect the
        actual values of the broker.

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
        ...

def attach_pipeline(
    pipeline: Pipeline,
    name: str,
    chunks: int = None,
    eager: bool = True
    ) -> Pipeline:
    """Register a pipeline to be computed at the start of each day.

    Parameters
    ----------
    pipeline : Pipeline
        The pipeline to have computed.
    name : str
        The name of the pipeline.
    chunks : int or iterator, optional
        The number of days to compute pipeline results for. Increasing
        this number will make it longer to get the first results but
        may improve the total runtime of the simulation. If an iterator
        is passed, we will run in chunks based on values of the iterator.
        Default is True.
    eager : bool, optional
        Whether or not to compute this pipeline prior to
        before_trading_start.

    Returns
    -------
    pipeline : Pipeline
        Returns the pipeline that was attached unchanged.

    Notes
    -----
    Usage Guide:

    * Attach pipelines: https://qrok.it/dl/z/zipline-attach-pipelines

    See Also
    --------
    :func:`zipline.api.pipeline_output`
    """

def batch_market_order(share_counts: 'pd.Series[int]') -> 'pd.Index[str]':
    """Place a batch market order for multiple assets.

    Parameters
    ----------
    share_counts : pd.Series[Asset -> int]
        Map from asset to number of shares to order for that asset.

    Returns
    -------
    order_ids : pd.Index[str]
        Index of ids for newly-created orders.

    Notes
    -----
    Usage Guide:

    * Placing orders: https://qrok.it/dl/z/zipline-orders
    """

def cancel_order(order_param: Union[str, Order]) -> None:
    """Cancel an open order.

    Parameters
    ----------
    order_param : str or Order
        The order_id or order object to cancel.

    Notes
    -----
    Usage Guide:

    * Placing orders: https://qrok.it/dl/z/zipline-orders
    """

def continuous_future(
    root_symbol_str: str,
    offset: int = 0,
    roll: Literal["volume", "calendar"] = "volume",
    adjustment: Literal["mul", "add", None] = "mul",
    ) -> ContinuousFuture:
    """Create a continuous future from a specified root symbol.

    Parameters
    ----------
    root_symbol_str : str
        The root symbol for the future chain.

    offset : int, optional
        The distance from the primary contract. Default is 0.

    roll_style : str, optional
        How rolls are determined. Possible choices: 'volume',
        (roll when back contract volume exceeds front contract
        volume), or 'calendar' (roll on rollover date). Default
        is 'volume'.

    adjustment : str, optional
        Method for adjusting lookback prices between rolls. Options are
        'mul', 'add' or None. 'mul' calculates the ratio of front and back
        contracts on the roll date ((back - front)/front) and multiplies
        front contract prices by (1 + ratio). 'add' calculates the difference
        between back and front contracts on the roll date (back - front)
        and adds the difference to front contract prices. None concatenates
        contracts without any adjustment. Default is 'mul'.

    Returns
    -------
    continuous_future : ContinuousFuture
        The continuous future specifier.

    Notes
    -----
    Usage Guide:

    * Continuous Futures: https://qrok.it/dl/z/zipline-contfut

    Examples
    --------
    Create a continuous future for ES, rolling on volume::

        import zipline.api as algo
        algo.continuous_future("ES", roll="volume")
    """

def future_symbol(symbol: str) -> Future:
    """Lookup a futures contract with a given symbol.

    Parameters
    ----------
    symbol : str
        The symbol of the desired contract.

    Returns
    -------
    future : Future
        The future that trades with the name ``symbol``.

    Raises
    ------
    SymbolNotFound
        Raised when no contract named 'symbol' is found.
    """

def get_datetime(tz: str = None) -> pd.Timestamp:
    """
    Get the current simulation datetime.

    Parameters
    ----------
    tz : tzinfo or str, optional
        The timezone to return the datetime in. This defaults to utc.

    Returns
    -------
    dt : datetime
        The current simulation datetime converted to ``tz``.
    """

@overload
def get_environment(
    field: Literal['platform', 'arena', 'data_frequency']) -> str: ...

@overload
def get_environment(
    field: Literal['start', 'end']) -> pd.Timestamp: ...

@overload
def get_environment(
    field: Literal['capital_base']) -> float: ...

@overload
def get_environment(
    field: Literal['*']) -> dict[str, Union[str, float, pd.Timestamp]]: ...

def get_environment(field):
    """Query the execution environment.

    Parameters
    ----------
    field : {'arena', 'data_frequency', 'start', 'end', 'capital_base', 'platform', '*'}
        The field to query. The options have the following meanings:

            arena : str
                The arena from the simulation parameters. ``'backtest'`` or ``'trade'``.

            data_frequency : {'daily', 'minute'}
                data_frequency tells the algorithm if it is running with
                daily data or minute data.

            start : datetime
                The start date for the simulation.

            end : datetime
                The end date for the simulation.

            capital_base : float
                The starting capital for the simulation.

            platform : str
                The platform that the code is running on. By default this
                will be the string 'zipline'.

            * : dict[str -> any]
                Returns all of the fields in a dictionary.


    Returns
    -------
    val : any
        The value for the field queried. See above for more information.

    Raises
    ------
    ValueError
        Raised when ``field`` is not a valid option.

    Examples
    --------
    Only perform a certain action in live trading::

        import zipline.api as algo
        if algo.get_environment("arena") == "trade":
            ...
    """

@overload
def get_open_orders(
    asset: Literal[None] = None
    ) -> dict[Asset, list[Order]]:...

@overload
def get_open_orders(
    asset: Asset
    ) -> list[Order]:...

def get_open_orders(asset):
    """Retrieve all of the current open orders.

    Parameters
    ----------
    asset : Asset
        If passed and not None, return only the open orders for the given
        asset instead of all open orders.

    Returns
    -------
    open_orders : dict[list[Order]] or list[Order]
        If no asset is passed this will return a dict mapping Assets
        to a list containing all the open orders for the asset.
        If an asset is passed then this will return a list of the open
        orders for this asset.

    Notes
    -----
    Usage Guide:

    * Placing orders: https://qrok.it/dl/z/zipline-orders
    """

def get_order(order_id: str) -> Order:
    """Lookup an order based on the order id returned from one of the
    order functions.

    Parameters
    ----------
    order_id : str
        The unique identifier for the order.

    Returns
    -------
    order : Order
        The order object.

    Notes
    -----
    Usage Guide:

    * Placing orders: https://qrok.it/dl/z/zipline-orders
    """

def order(
    asset: Asset,
    amount: int,
    limit_price: float = None,
    stop_price: float = None,
    style: execution.ExecutionStyle = None
    ) -> Union[str, None]:
    """Place an order.

    Parameters
    ----------
    asset : Asset
        The asset that this order is for.
    amount : int
        The amount of shares to order. If ``amount`` is positive, this is
        the number of shares to buy or cover. If ``amount`` is negative,
        this is the number of shares to sell or short.
    limit_price : float, optional
        The limit price for the order.
    stop_price : float, optional
        The stop price for the order.
    style : zipline.api.execution.ExecutionStyle, optional
        The execution style for the order.

    Returns
    -------
    order_id : str or None
        The unique identifier for this order, or None if no order was
        placed.

    See Also
    --------
    :class:`zipline.api.execution.MarketOrder`
    :class:`zipline.api.execution.LimitOrder`
    :class:`zipline.api.execution.StopOrder`
    :class:`zipline.api.execution.StopLimitOrder`
    :func:`zipline.api.order_value`
    :func:`zipline.api.order_percent`
    :func:`zipline.api.order_target`
    :func:`zipline.api.order_target_value`
    :func:`zipline.api.order_target_percent`

    Notes
    -----
    The ``limit_price`` and ``stop_price`` arguments provide shorthands for
    passing common execution styles. Passing ``limit_price=N`` is
    equivalent to ``style=LimitOrder(N)``. Similarly, passing
    ``stop_price=M`` is equivalent to ``style=StopOrder(M)``, and passing
    ``limit_price=N`` and ``stop_price=M`` is equivalent to
    ``style=StopLimitOrder(N, M)``. It is an error to pass both a ``style``
    and ``limit_price`` or ``stop_price``.

    Usage Guide:

    * Placing orders: https://qrok.it/dl/z/zipline-orders
    """

def order_percent(
    asset: Asset,
    percent: float,
    limit_price: float = None,
    stop_price: float = None,
    style: execution.ExecutionStyle = None
    ) -> Union[str, None]:
    """Place an order in the specified asset corresponding to the given
    percent of the current portfolio value.

    Parameters
    ----------
    asset : Asset
        The asset that this order is for.
    percent : float
        The percentage of the portfolio value to allocate to ``asset``.
        This is specified as a decimal, for example: 0.50 means 50%.
    limit_price : float, optional
        The limit price for the order.
    stop_price : float, optional
        The stop price for the order.
    style: zipline.api.execution.ExecutionStyle
        The execution style for the order.

    Returns
    -------
    order_id : str
        The unique identifier for this order.

    See Also
    --------
    :class:`zipline.api.execution.MarketOrder`
    :class:`zipline.api.execution.LimitOrder`
    :class:`zipline.api.execution.StopOrder`
    :class:`zipline.api.execution.StopLimitOrder`
    :func:`zipline.api.order_value`
    :func:`zipline.api.order`
    :func:`zipline.api.order_target`
    :func:`zipline.api.order_target_value`
    :func:`zipline.api.order_target_percent`

    Notes
    -----
    See :func:`zipline.api.order` for more information about
    ``limit_price``, ``stop_price``, and ``style``

    Usage Guide:

    * Placing orders: https://qrok.it/dl/z/zipline-orders
    """

def order_target(
    asset: Asset,
    target: int,
    limit_price: float = None,
    stop_price: float = None,
    style: execution.ExecutionStyle = None
    ) -> Union[str, None]:
    """Place an order to adjust a position to a target number of shares. If
    the position doesn't already exist, this is equivalent to placing a new
    order. If the position does exist, this is equivalent to placing an
    order for the difference between the target number of shares and the
    current number of shares.

    Parameters
    ----------
    asset : Asset
        The asset that this order is for.
    target : int
        The desired number of shares of ``asset``.
    limit_price : float, optional
        The limit price for the order.
    stop_price : float, optional
        The stop price for the order.
    style: zipline.api.execution.ExecutionStyle
        The execution style for the order.

    Returns
    -------
    order_id : str
        The unique identifier for this order.

    See Also
    --------
    :class:`zipline.api.execution.MarketOrder`
    :class:`zipline.api.execution.LimitOrder`
    :class:`zipline.api.execution.StopOrder`
    :class:`zipline.api.execution.StopLimitOrder`
    :func:`zipline.api.order_value`
    :func:`zipline.api.order`
    :func:`zipline.api.order_percent`
    :func:`zipline.api.order_target_value`
    :func:`zipline.api.order_target_percent`

    Notes
    -----
    ``order_target`` does not take into account any open orders. For
    example::

        order_target(sid('A'), 10)
        order_target(sid('A'), 10)

    This code will result in 20 shares of ``sid('A')`` because the first
    call to ``order_target`` will not have been filled when the second
    ``order_target`` call is made.

    See :func:`zipline.api.order` for more information about
    ``limit_price``, ``stop_price``, and ``style``

    Usage Guide:

    * Placing orders: https://qrok.it/dl/z/zipline-orders
    """

def order_target_percent(
    asset: Asset,
    target: float,
    limit_price: float = None,
    stop_price: float = None,
    style: execution.ExecutionStyle = None
    ) -> Union[str, None]:
    """Place an order to adjust a position to a target percent of the
    current portfolio value. If the position doesn't already exist, this is
    equivalent to placing a new order. If the position does exist, this is
    equivalent to placing an order for the difference between the target
    percent and the current percent.

    Parameters
    ----------
    asset : Asset
        The asset that this order is for.
    target : float
        The desired percentage of the portfolio value to allocate to
        ``asset``. This is specified as a decimal, for example:
        0.50 means 50%.
    limit_price : float, optional
        The limit price for the order.
    stop_price : float, optional
        The stop price for the order.
    style: zipline.api.execution.ExecutionStyle
        The execution style for the order.

    Returns
    -------
    order_id : str
        The unique identifier for this order.

    See Also
    --------
    :class:`zipline.api.execution.MarketOrder`
    :class:`zipline.api.execution.LimitOrder`
    :class:`zipline.api.execution.StopOrder`
    :class:`zipline.api.execution.StopLimitOrder`
    :func:`zipline.api.order_value`
    :func:`zipline.api.order`
    :func:`zipline.api.order_percent`
    :func:`zipline.api.order_target`
    :func:`zipline.api.order_target_value`

    Notes
    -----
    ``order_target_value`` does not take into account any open orders. For
    example::

        order_target_percent(sid('A'), 10)
        order_target_percent(sid('A'), 10)

    This code will result in 20% of the portfolio being allocated to sid('A')
    because the first call to ``order_target_percent`` will not have been
    filled when the second ``order_target_percent`` call is made.

    See :func:`zipline.api.order` for more information about
    ``limit_price``, ``stop_price``, and ``style``

    Usage Guide:

    * Placing orders: https://qrok.it/dl/z/zipline-orders
    """

def order_target_value(
    asset: Asset,
    target: float,
    limit_price: float = None,
    stop_price: float = None,
    style: execution.ExecutionStyle = None
    ) -> Union[str, None]:
    """Place an order to adjust a position to a target value. If
    the position doesn't already exist, this is equivalent to placing a new
    order. If the position does exist, this is equivalent to placing an
    order for the difference between the target value and the
    current value.
    If the Asset being ordered is a Future, the 'target value' calculated
    is actually the target exposure, as Futures have no 'value'.

    Parameters
    ----------
    asset : Asset
        The asset that this order is for.
    target : float
        The desired total value of ``asset``.
    limit_price : float, optional
        The limit price for the order.
    stop_price : float, optional
        The stop price for the order.
    style: zipline.api.execution.ExecutionStyle
        The execution style for the order.

    Returns
    -------
    order_id : str
        The unique identifier for this order.

    See Also
    --------
    :class:`zipline.api.execution.MarketOrder`
    :class:`zipline.api.execution.LimitOrder`
    :class:`zipline.api.execution.StopOrder`
    :class:`zipline.api.execution.StopLimitOrder`
    :func:`zipline.api.order_value`
    :func:`zipline.api.order`
    :func:`zipline.api.order_percent`
    :func:`zipline.api.order_target`
    :func:`zipline.api.order_target_percent`

    Notes
    -----
    ``order_target_value`` does not take into account any open orders. For
    example::

        order_target_value(sid('A'), 10)
        order_target_value(sid('A'), 10)

    This code will result in 20 dollars of ``sid('A')`` because the first
    call to ``order_target_value`` will not have been filled when the
    second ``order_target_value`` call is made.

    See :func:`zipline.api.order` for more information about
    ``limit_price``, ``stop_price``, and ``style``

    Usage Guide:

    * Placing orders: https://qrok.it/dl/z/zipline-orders
    """

def order_value(
    asset: Asset,
    value: float,
    limit_price: float = None,
    stop_price: float = None,
    style: execution.ExecutionStyle = None
    ) -> Union[str, None]:
    """
    Place an order for a fixed amount of money.

    Equivalent to ``order(asset, value / data.current(asset, 'price'))``.

    Parameters
    ----------
    asset : Asset
        The asset that this order is for.
    value : float
        Amount of value of ``asset`` to be transacted. The number of shares
        bought or sold will be equal to ``value / current_price``.
        value > 0 :: Buy/Cover
        value < 0 :: Sell/Short
    limit_price : float, optional
        The limit price for the order.
    stop_price : float, optional
        The stop price for the order.
    style: zipline.api.execution.ExecutionStyle
        The execution style for the order.

    Returns
    -------
    order_id : str
        The unique identifier for this order.

    See Also
    --------
    :class:`zipline.api.execution.MarketOrder`
    :class:`zipline.api.execution.LimitOrder`
    :class:`zipline.api.execution.StopOrder`
    :class:`zipline.api.execution.StopLimitOrder`
    :func:`zipline.api.order`
    :func:`zipline.api.order_percent`
    :func:`zipline.api.order_target`
    :func:`zipline.api.order_target_value`
    :func:`zipline.api.order_target_percent`

    Notes
    -----
    See :func:`zipline.api.order` for more information about
    ``limit_price``, ``stop_price``, and ``style``

    Usage Guide:

    * Placing orders: https://qrok.it/dl/z/zipline-orders
    """

def capital_change(amount: float) -> None:
    """
    Simulate a deposit or withdrawal from the algorithm's cash.

    Parameters
    ----------
    amount : float, required
        The amount to deposit or withdraw. Negative amounts are
        withdrawals and positive amounts are deposits. The amount
        is assumed to be in the algorithm's base currency.

    Returns
    -------
    None

    Examples
    --------
    Withdraw $1,000::

        algo.capital_change(-1000)

    Deposit $1,000::

        algo.capital_change(1000)
    """

def pipeline_output(name: str) -> pd.DataFrame:
    """Get the results of the pipeline that was attached with the name:
    ``name``.

    Parameters
    ----------
    name : str
        Name of the pipeline for which results are requested.

    Returns
    -------
    results : pd.DataFrame
        DataFrame containing the results of the requested pipeline for
        the current simulation date.

    Raises
    ------
    NoSuchPipeline
        Raised when no pipeline with the name `name` has been registered.

    See Also
    --------
    :func:`zipline.api.attach_pipeline`

    Notes
    -----
    Usage Guide:

    * Pipeline output: https://qrok.it/dl/z/zipline-pipeline-output
    """

def record(**kwargs: Any) -> None:
    """Track and record values each day.

    Parameters
    ----------
    **kwargs
        The names and values to record.

    Notes
    -----
    These values will appear in the results CSV returned in backtests.
    """

def set_realtime_db(
    code: str,
    fields: dict[str, str] = {}
    ) -> None:
    """
    Set the realtime database to use for querying up-to-date minute bars in
    live trading.

    Parameters
    ----------
    code : str, required
        the realtime database code. Must be an aggregate database with
        1-minute bars.

    fields : dict, optional
        dict mapping expected Zipline field names ('close', 'high', 'low', 'open',
        'volume') to realtime database field names

    Returns
    -------
    None

    Notes
    -----
    Usage Guide:

    * Real-time data configuration: https://qrok.it/dl/z/zipline-realtime

    Examples
    --------
    Set the realtime database and map fields::

        algo.set_realtime_db(
            "us-stk-tick-1min",
            fields={
                "close": "LastPriceClose",
                "open": "LastPriceOpen",
                "high": "LastPriceHigh",
                "low": "LastPriceLow",
                "volume": "LastSizeSum"})
    """
    ...

ContextOrSubclass = TypeVar('ContextOrSubclass', bound=Context)

def schedule_function(
    func: Callable[[ContextOrSubclass, BarData], None],
    date_rule: EventRule = None,
    time_rule: EventRule = None,
    half_days: bool = True
    ) -> None:
    """
    Schedule a function to be called repeatedly in the future.

    Parameters
    ----------
    func : callable
        The function to execute when the rule is triggered. ``func`` should
        have the same signature as ``handle_data``.
    date_rule : zipline.utils.events.EventRule, optional
        Rule for the dates on which to execute ``func``. If not
        passed, the function will run every trading day.
    time_rule : zipline.utils.events.EventRule, optional
        Rule for the time at which to execute ``func``. If not passed, the
        function will execute at the end of the first market minute of the
        day.
    half_days : bool, optional
        Should this rule fire on half days? Default is True.

    Examples
    --------
    Schedule a function called rebalance to run every trading day 30 minutes
    after the open::

        import zipline.api as algo
        algo.schedule_function(
            rebalance,
            algo.date_rules.every_day(),
            algo.time_rules.market_open(minutes=30))

    See Also
    --------
    :class:`zipline.api.date_rules`
    :class:`zipline.api.time_rules`

    Notes
    -----
    Usage Guide:

    * Scheduled functions: https://qrok.it/dl/z/zipline-schedule
    """

class date_rules:
    """
    Factories for date-based :func:`~zipline.api.schedule_function` rules.

    See Also
    --------
    :func:`~zipline.api.schedule_function`

    Notes
    -----
    Usage Guide:

    * Scheduled functions: https://qrok.it/dl/z/zipline-schedule
    """

    @staticmethod
    def every_day() -> EventRule:
        """Create a rule that triggers every day.

        Returns
        -------
        rule : zipline.utils.events.EventRule
        """
        ...

    @staticmethod
    def month_start(days_offset: int = 0, months: list[int] = None) -> EventRule:
        """
        Create a rule that triggers a fixed number of trading days after the
        start of each month.

        Parameters
        ----------
        days_offset : int, optional
            Number of trading days to wait before triggering each
            month. Default is 0, i.e., trigger on the first trading day of the
            month.

        months : list[int], optional
            List of months to trigger (1-12). If not passed, trigger on every month.

        Returns
        -------
        rule : zipline.utils.events.EventRule

        Examples
        --------
        Trigger on the 3rd trading day of every month::

            algo.schedule_function(
                algo.date_rules.month_start(days_offset=2),
                ...
            )

        Trigger quarterly on the first trading day of the month::

            algo.schedule_function(
                algo.date_rules.month_start(months=[1, 4, 7, 10]),
                ...
            )
        """
        ...

    @staticmethod
    def month_end(days_offset: int = 0, months: list[int] = None) -> EventRule:
        """
        Create a rule that triggers a fixed number of trading days before the
        end of each month.

        Parameters
        ----------
        days_offset : int, optional
            Number of trading days prior to month end to trigger. Default is 0,
            i.e., trigger on the last day of the month.

        months : list[int], optional
            List of months to trigger (1-12). If not passed, trigger on every month.

        Returns
        -------
        rule : zipline.utils.events.EventRule

        Examples
        --------
        Trigger on the last trading day of every month::

            algo.schedule_function(
                algo.date_rules.month_end(),
                ...
            )

        Trigger quarterly on the 2nd to last trading day of the month::

            algo.schedule_function(
                algo.date_rules.month_end(days_offset=1, months=[1, 4, 7, 10]),
                ...
            )
        """
        ...

    @staticmethod
    def week_start(days_offset: int = 0) -> EventRule:
        """
        Create a rule that triggers a fixed number of trading days after the
        start of each week.

        Parameters
        ----------
        days_offset : int, optional
            Number of trading days to wait before triggering each week. Default
            is 0, i.e., trigger on the first trading day of the week.
        """
        ...

    @staticmethod
    def week_end(days_offset: int = 0) -> EventRule:
        """
        Create a rule that triggers a fixed number of trading days before the
        end of each week.

        Parameters
        ----------
        days_offset : int, optional
            Number of trading days prior to week end to trigger. Default is 0,
            i.e., trigger on the last trading day of the week.
        """
        ...

class time_rules:
    """Factories for time-based :func:`~zipline.api.schedule_function` rules.

    See Also
    --------
    :func:`~zipline.api.schedule_function`

    Notes
    -----
    Usage Guide:

    * Scheduled functions: https://qrok.it/dl/z/zipline-schedule
    """

    @staticmethod
    def market_open(
        offset: pd.Timedelta = None,
        hours: int = None,
        minutes: int = None
        ) -> EventRule:
        """
        Create a rule that triggers at a fixed offset from market open.

        The offset can be specified either as a :class:`datetime.timedelta`, or
        as a number of hours and minutes.

        Parameters
        ----------
        offset : datetime.timedelta, optional
            If passed, the offset from market open at which to trigger. Must be
            at least 1 minute.
        hours : int, optional
            If passed, number of hours to wait after market open.
        minutes : int, optional
            If passed, number of minutes to wait after market open.

        Returns
        -------
        rule : zipline.utils.events.EventRule

        Notes
        -----
        If no arguments are passed, the default offset is one minute after
        market open.

        If ``offset`` is passed, ``hours`` and ``minutes`` must not be
        passed. Conversely, if either ``hours`` or ``minutes`` are passed,
        ``offset`` must not be passed.
        """
        ...

    @staticmethod
    def market_close(
        offset: pd.Timedelta = None,
        hours: int = None,
        minutes: int = None
        ) -> EventRule:
        """
        Create a rule that triggers at a fixed offset from market close.

        The offset can be specified either as a :class:`datetime.timedelta`, or
        as a number of hours and minutes.

        Parameters
        ----------
        offset : datetime.timedelta, optional
            If passed, the offset from market close at which to trigger. Must
            be at least 1 minute.
        hours : int, optional
            If passed, number of hours to wait before market close.
        minutes : int, optional
            If passed, number of minutes to wait before market close.

        Returns
        -------
        rule : zipline.utils.events.EventRule

        Notes
        -----
        If no arguments are passed, the default offset is one minute before
        market close.

        If ``offset`` is passed, ``hours`` and ``minutes`` must not be
        passed. Conversely, if either ``hours`` or ``minutes`` are passed,
        ``offset`` must not be passed.
        """
        ...

    @staticmethod
    def every_minute() -> EventRule:
        """
        Create a rule that always triggers.
        """
        ...

def set_asset_restrictions(
    restrictions: asset_restrictions.Restrictions,
    on_error: Literal['fail', 'log'] = 'fail'
    ) -> None:
    """Set a restriction on which assets can be ordered.

    Parameters
    ----------
    restricted_list : zipline.finance.asset_restrictions.Restrictions
        An object providing information about restricted assets.

    See Also
    --------
    zipline.finance.asset_restrictions.StaticRestrictions
    """

def set_benchmark(benchmark: Asset) -> None:
    """Set the benchmark asset.

    Parameters
    ----------
    benchmark : Asset
        The asset to set as the new benchmark.

    Examples
    --------
    Set the benchmark to SPY::

        import zipline.api as algo
        spy = algo.sid("FIBBG000BDTBL9")
        algo.set_benchmark(spy)

    Notes
    -----
    Any dividends payed out for that new benchmark asset will be
    automatically reinvested.

    Usage Guide:

    * Benchmarks: https://qrok.it/dl/z/zipline-benchmark
    """

def set_cancel_policy(cancel_policy: cancel_policy.CancelPolicy) -> None:
    """Set the order cancellation policy for the simulation.

    Parameters
    ----------
    cancel_policy : CancelPolicy
        The cancellation policy to use.

    See Also
    --------
    :class:`zipline.api.EODCancel`
    :class:`zipline.api.NeverCancel`

    Usage Guide:

    * Time-in-force: https://qrok.it/dl/z/zipline-tif
    """

class EODCancel(cancel_policy.CancelPolicy):
    """
    Order cancellation policy that cancels orders at the end of the day. This is
    the default policy and does not need to be explicitly set. In live trading,
    this cancel policy will cause orders to be submitted with a Tif (time-in-force)
    of DAY.

    Parameters
    ----------
    warn_on_cancel : bool, optional
        Should a warning be raised if this causes an order to be cancelled?
    """
    def __init__(self, warn_on_cancel: bool =True):
        ...

class NeverCancel(cancel_policy.CancelPolicy):
    """
    Order cancellation policy that never cancels orders. In live trading, this
    cancel policy will cause orders to be submitted with a Tif (time-in-force) of GTC
    (Good-till-canceled).

    Examples
    --------
    Set the cancel policy to NeverCancel::

        from zipline.api import set_cancel_policy, cancel_policy
        def initialize(context):
            set_cancel_policy(cancel_policy.NeverCancel())
    """
    ...

def set_commission(
    us_equities: commission.EquityCommissionModel = None,
    us_futures: commission.FutureCommissionModel = None
    ) -> None:
    """Set the commission models for the simulation.

    Parameters
    ----------
    us_equities : zipline.api.commission.EquityCommissionModel
        The commission model to use for trading US equities.
    us_futures : zipline.api.commission.FutureCommissionModel
        The commission model to use for trading US futures.

    See Also
    --------
    :class:`zipline.api.commission.PerShare`
    :class:`zipline.api.commission.PerTrade`
    :class:`zipline.api.commission.PerDollar`

    Notes
    -----
    This function can only be called during
    :func:`~zipline.api.initialize`.

    Usage Guide:

    * Commissions and slippage: https://qrok.it/dl/z/zipline-commissions-slippage

    Examples
    --------
    Set the equities commission to 0.001 per share::

        import zipline.api as algo
        algo.set_commission(algo.commission.PerShare(cost=0.001))
    """

def set_long_only(on_error: Literal['fail', 'log'] ='fail') -> None:
    """Set a rule specifying that this algorithm cannot take short
    positions.
    """

def set_max_leverage(max_leverage: float) -> None:
    """Set a limit on the maximum leverage of the algorithm.

    Parameters
    ----------
    max_leverage : float
        The maximum leverage for the algorithm. If not provided there will
        be no maximum.
    """

def set_max_order_count(
    max_count: int,
    on_error: Literal['fail', 'log'] = 'fail'
    ) -> None:
    """Set a limit on the number of orders that can be placed in a single
    day.

    Parameters
    ----------
    max_count : int
        The maximum number of orders that can be placed on any single day.
    """

def set_max_order_size(
    asset: Asset = None,
    max_shares: int = None,
    max_notional: float = None,
    on_error: Literal['fail', 'log'] = 'fail'
    ) -> None:
    """Set a limit on the number of shares and/or dollar value of any single
    order placed for `asset`.  Limits are treated as absolute values and are
    enforced at the time that the algo attempts to place an order for sid.

    If an algorithm attempts to place an order that would result in
    exceeding one of these limits, raise a TradingControlException.

    Parameters
    ----------
    asset : Asset, optional
        If provided, this sets the guard only on positions in the given
        asset.
    max_shares : int, optional
        The maximum number of shares that can be ordered at one time.
    max_notional : float, optional
        The maximum value that can be ordered at one time.
    """

def set_max_position_size(
    asset: Asset = None,
    max_shares: int = None,
    max_notional: float = None,
    on_error: Literal['fail', 'log'] = 'fail'
    ) -> None:
    """Set a limit on the number of shares and/or dollar value held for the
    given `asset`. Limits are treated as absolute values and are enforced at
    the time that the algo attempts to place an order for sid. This means
    that it's possible to end up with more than the max number of shares
    due to splits/dividends, and more than the max notional due to price
    improvement.

    If an algorithm attempts to place an order that would result in
    increasing the absolute value of shares/dollar value exceeding one of
    these limits, raise a TradingControlException.

    Parameters
    ----------
    asset : Asset, optional
        If provided, this sets the guard only on positions in the given
        asset.
    max_shares : int, optional
        The maximum number of shares to hold for an asset.
    max_notional : float, optional
        The maximum value to hold for an asset.
    """

def set_min_leverage(
    min_leverage: float,
    grace_period: pd.Timedelta
    ) -> None:
    """Set a limit on the minimum leverage of the algorithm.

    Parameters
    ----------
    min_leverage : float
        The minimum leverage for the algorithm.
    grace_period : pd.Timedelta
        The offset from the start date used to enforce a minimum leverage.
    """

def set_slippage(
    us_equities: slippage.EquitySlippageModel = None,
    us_futures: slippage.FutureSlippageModel = None
    ) -> None:
    """Set the slippage models for the simulation.

    Parameters
    ----------
    us_equities : zipline.api.slippage.EquitySlippageModel
        The slippage model to use for trading US equities.
    us_futures : zipline.api.slippage.FutureSlippageModel
        The slippage model to use for trading US futures.

    Examples
    --------
    Set the equities slippage to 5 basis points::

        import zipline.api as algo
        algo.set_slippage(algo.slippage.FixedBasisPointsSlippage(basis_points=5.0))

    See Also
    --------
    :class:`zipline.api.slippage.SlippageModel`

    Notes
    -----
    This function can only be called during
    :func:`~zipline.api.initialize`.

    Usage Guide:

    * Commissions and slippage: https://qrok.it/dl/z/zipline-commissions-slippage
    """

def set_management_fee(
    rate: float = None,
    date_rule: EventRule = None,
    ) -> None:
    """Set the management fee for the simulation.

    Parameters
    ----------
    rate : float
        The annualized percentage of assets under management (AUM)
        that is charged as a management fee.
    date_rule : EventRule
        The date rule used to determine when the management fee should
        be assessed. By default, management fees are assessed on the
        first trading day of each month.

    Notes
    -----
    This function can only be called during
    :func:`~zipline.api.initialize`.

    Examples
    --------
    Set a "2 and 20" fee model::

        import zipline.api as algo
        algo.set_management_fee(rate=0.02)
        algo.set_performance_fee(rate=0.20)
    """

def set_performance_fee(
    rate: float = None,
    date_rule: EventRule = None,
    ) -> None:
    """Set the performance fee for the simulation.

    Parameters
    ----------
    rate : float
        The percentage of profit (subject to highwater mark) that is
        charged as a performance fee.
    date_rule : EventRule
        The date rule used to determine when the performance fee should
        be assessed. By default, performance fees are assessed on
        the first trading day of the quarter.

    Notes
    -----
    This function can only be called during
    :func:`~zipline.api.initialize`.

    Examples
    --------
    Set a "2 and 20" fee model::

        import zipline.api as algo
        algo.set_management_fee(rate=0.02)
        algo.set_performance_fee(rate=0.20)
    """

def set_margin_interest(interest_rate: float) -> None:
    """Set the margin interest rate for the simulation.

    Parameters
    ----------
    interest_rate : float
        The annualized interest rate charged on margin loans.

    Notes
    -----
    This function can only be called during
    :func:`~zipline.api.initialize`.

    By industry convention, the annualized interest rate is divided
    by 360, not 365, to calculate daily interest.

    Examples
    --------
    Set 5% margin interest::

        import zipline.api as algo
        algo.set_margin_interest(0.05)
    """

def set_borrow_fees_provider(name: Literal['ibkr']) -> None:
    """Set the data provider whose borrow fee data will be used for
    debiting borrow fees on short positions during the simulation.

    Parameters
    ----------
    name : str
        The name of the data provider. The only supported choice is
        'ibkr'.

    Notes
    -----
    This function can only be called during
    :func:`~zipline.api.initialize`.

    By industry convention, the annualized borrow fee is divided
    by 360, not 365, to calculate daily fees. The daily fee rate
    is assessed on a collateral amount that is calculated by
    multiplying the number of shares times the share price (rounded up
    to the nearest dollar) times 102% (by industry convention). For
    example, suppose the annualized borrow fee rate is 3.6%, the share
    price is $9.15, and 1,000 shares are held short. The daily borrow
    fee rate is 0.01% (3.6% / 360), and the collateral amount is $10,200:
    1,000 shares x $10.00/share ($9.15/share rounded up) x 102% = $10,200.
    Consequently, the daily borrow fee is $1.02.

    Borrow fees accrue daily and are debited from the account on the first
    trading day of each month.

    Examples
    --------
    Set Interactive Brokers as the borrow fees data provider::

        import zipline.api as algo
        algo.set_borrow_fees_provider('ibkr')
    """

def sid(sid: str) -> Asset:
    """Lookup an Asset by its unique asset identifier.

    Parameters
    ----------
    sid : str
        The QuantRocket sid that identifies the asset.

    Returns
    -------
    asset : Asset
        The asset with the given ``sid``.

    Raises
    ------
    SidsNotFound
        When a requested ``sid`` does not map to any asset.
    """


def symbol(symbol: str) -> Asset:
    """
    Lookup an Equity by its ticker symbol.

    Ticker symbols can change over time, and this function will raise an
    error if the ticker symbol has been associated with more than one equity.
    For a more robust way to retrieve an equity, use `sid()`.

    Parameters
    ----------
    symbol : str
        The ticker symbol for the equity.

    Returns
    -------
    equity : zipline.assets.Equity
        The equity with the ticker symbol.

    Raises
    ------
    SymbolNotFound
        Raised when the symbol was not held by any equity.
    MultipleSymbolsFound
        Raised when the symbol was held by more than one equity.
    """
