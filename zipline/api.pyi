from typing import Union, Callable
import collections
import pandas as pd
from zipline.algorithm import TradingAlgorithm
from zipline.assets import Asset, Equity, Future, ContinuousFuture
from zipline.finance.asset_restrictions import Restrictions
from zipline.finance.cancel_policy import CancelPolicy
from zipline.finance.execution import ExecutionStyle
from zipline.finance.commission import EquityCommissionModel, FutureCommissionModel
from zipline.finance.slippage import EquitySlippageModel, FutureSlippageModel
from zipline.pipeline import Pipeline
from zipline.protocol import Order
from zipline._protocol import BarData
from zipline.utils.events import EventRule
from trading_calendars import TradingCalendar

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

    See Also
    --------
    :func:`zipline.api.pipeline_output`
    """

def batch_market_order(share_counts: pd.Series) -> pd.Index:
    """Place a batch market order for multiple assets.

    Parameters
    ----------
    share_counts : pd.Series[Asset -> int]
        Map from asset to number of shares to order for that asset.

    Returns
    -------
    order_ids : pd.Index[str]
        Index of ids for newly-created orders.
    """

def cancel_order(order_param: Union[str, Order]) -> None:
    """Cancel an open order.

    Parameters
    ----------
    order_param : str or Order
        The order_id or order object to cancel.
    """

def continuous_future(
    root_symbol_str: str,
    offset: int = 0,
    roll: str = 'volume',
    adjustment: str = 'mul'
    ) -> ContinuousFuture:
    """Create a specifier for a continuous contract.

    Parameters
    ----------
    root_symbol_str : str
        The root symbol for the future chain.

    offset : int, optional
        The distance from the primary contract. Default is 0.

    roll_style : str, optional
        How rolls are determined. Default is 'volume'.

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
Returns the current simulation datetime.

Parameters
----------
tz : tzinfo or str, optional
    The timezone to return the datetime in. This defaults to utc.

Returns
-------
dt : datetime
    The current simulation datetime converted to ``tz``.
    """

def get_environment(field: str = 'platform') -> Union[str, pd.Timestamp]:
    """Query the execution environment.

    Parameters
    ----------
    field : {'platform', 'arena', 'data_frequency', 'start', 'end', 'capital_base', 'platform', '*'}
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
    Only perform a certain action in live trading:

    >>> import zipline.api as algo
    >>> if algo.get_environment("arena") == "trade":    # doctest: +SKIP
    >>>     ...                                         # doctest: +SKIP
    """

def get_open_orders(
    asset: Asset = None
    ) -> Union[list[Order], dict[Asset, list[Order]]]:
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
    """

def order(
    asset: Asset,
    amount: int,
    limit_price: float = None,
    stop_price: float = None,
    style: ExecutionStyle = None
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
    style : ExecutionStyle, optional
        The execution style for the order.

    Returns
    -------
    order_id : str or None
        The unique identifier for this order, or None if no order was
        placed.

    Notes
    -----
    The ``limit_price`` and ``stop_price`` arguments provide shorthands for
    passing common execution styles. Passing ``limit_price=N`` is
    equivalent to ``style=LimitOrder(N)``. Similarly, passing
    ``stop_price=M`` is equivalent to ``style=StopOrder(M)``, and passing
    ``limit_price=N`` and ``stop_price=M`` is equivalent to
    ``style=StopLimitOrder(N, M)``. It is an error to pass both a ``style``
    and ``limit_price`` or ``stop_price``.

    See Also
    --------
    :class:`zipline.finance.execution.MarketOrder`
    :class:`zipline.finance.execution.LimitOrder`
    :class:`zipline.finance.execution.StopOrder`
    :class:`zipline.finance.execution.StopLimitOrder`
    :func:`zipline.api.order_value`
    :func:`zipline.api.order_percent`
    :func:`zipline.api.order_target`
    :func:`zipline.api.order_target_value`
    :func:`zipline.api.order_target_percent`
    """

def order_percent(
    asset: Asset,
    percent: float,
    limit_price: float = None,
    stop_price: float = None,
    style: ExecutionStyle = None
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
    style : ExecutionStyle
        The execution style for the order.

    Returns
    -------
    order_id : str
        The unique identifier for this order.

    Notes
    -----
    See :func:`zipline.api.order` for more information about
    ``limit_price``, ``stop_price``, and ``style``

    See Also
    --------
    :class:`zipline.finance.execution.MarketOrder`
    :class:`zipline.finance.execution.LimitOrder`
    :class:`zipline.finance.execution.StopOrder`
    :class:`zipline.finance.execution.StopLimitOrder`
    :func:`zipline.api.order_value`
    :func:`zipline.api.order`
    :func:`zipline.api.order_target`
    :func:`zipline.api.order_target_value`
    :func:`zipline.api.order_target_percent`
    """

def order_target(
    asset: Asset,
    target: int,
    limit_price: float = None,
    stop_price: float = None,
    style: ExecutionStyle = None
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
    style : ExecutionStyle
        The execution style for the order.

    Returns
    -------
    order_id : str
        The unique identifier for this order.


    Notes
    -----
    ``order_target`` does not take into account any open orders. For
    example:

    .. code-block:: python

       order_target(sid(0), 10)
       order_target(sid(0), 10)

    This code will result in 20 shares of ``sid(0)`` because the first
    call to ``order_target`` will not have been filled when the second
    ``order_target`` call is made.

    See :func:`zipline.api.order` for more information about
    ``limit_price``, ``stop_price``, and ``style``

    See Also
    --------
    :class:`zipline.finance.execution.MarketOrder`
    :class:`zipline.finance.execution.LimitOrder`
    :class:`zipline.finance.execution.StopOrder`
    :class:`zipline.finance.execution.StopLimitOrder`
    :func:`zipline.api.order_value`
    :func:`zipline.api.order`
    :func:`zipline.api.order_percent`
    :func:`zipline.api.order_target_value`
    :func:`zipline.api.order_target_percent`
    """

def order_target_percent(
    asset: Asset,
    target: float,
    limit_price: float = None,
    stop_price: float = None,
    style: ExecutionStyle = None
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
    style : ExecutionStyle
        The execution style for the order.

    Returns
    -------
    order_id : str
        The unique identifier for this order.

    Notes
    -----
    ``order_target_value`` does not take into account any open orders. For
    example:

    .. code-block:: python

       order_target_percent(sid(0), 10)
       order_target_percent(sid(0), 10)

    This code will result in 20% of the portfolio being allocated to sid(0)
    because the first call to ``order_target_percent`` will not have been
    filled when the second ``order_target_percent`` call is made.

    See :func:`zipline.api.order` for more information about
    ``limit_price``, ``stop_price``, and ``style``

    See Also
    --------
    :class:`zipline.finance.execution.MarketOrder`
    :class:`zipline.finance.execution.LimitOrder`
    :class:`zipline.finance.execution.StopOrder`
    :class:`zipline.finance.execution.StopLimitOrder`
    :func:`zipline.api.order_value`
    :func:`zipline.api.order`
    :func:`zipline.api.order_percent`
    :func:`zipline.api.order_target`
    :func:`zipline.api.order_target_value`
    """

def order_target_value(
    asset: Asset,
    target: float,
    limit_price: float = None,
    stop_price: float = None,
    style: ExecutionStyle = None
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
    style : ExecutionStyle
        The execution style for the order.

    Returns
    -------
    order_id : str
        The unique identifier for this order.

    Notes
    -----
    ``order_target_value`` does not take into account any open orders. For
    example:

    .. code-block:: python

       order_target_value(sid(0), 10)
       order_target_value(sid(0), 10)

    This code will result in 20 dollars of ``sid(0)`` because the first
    call to ``order_target_value`` will not have been filled when the
    second ``order_target_value`` call is made.

    See :func:`zipline.api.order` for more information about
    ``limit_price``, ``stop_price``, and ``style``

    See Also
    --------
    :class:`zipline.finance.execution.MarketOrder`
    :class:`zipline.finance.execution.LimitOrder`
    :class:`zipline.finance.execution.StopOrder`
    :class:`zipline.finance.execution.StopLimitOrder`
    :func:`zipline.api.order_value`
    :func:`zipline.api.order`
    :func:`zipline.api.order_percent`
    :func:`zipline.api.order_target`
    :func:`zipline.api.order_target_percent`
    """

def order_value(
    asset: Asset,
    value: float,
    limit_price: float = None,
    stop_price: float = None,
    style: ExecutionStyle = None
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
    style : ExecutionStyle
        The execution style for the order.

    Returns
    -------
    order_id : str
        The unique identifier for this order.

    Notes
    -----
    See :func:`zipline.api.order` for more information about
    ``limit_price``, ``stop_price``, and ``style``

    See Also
    --------
    :class:`zipline.finance.execution.MarketOrder`
    :class:`zipline.finance.execution.LimitOrder`
    :class:`zipline.finance.execution.StopOrder`
    :class:`zipline.finance.execution.StopLimitOrder`
    :func:`zipline.api.order`
    :func:`zipline.api.order_percent`
    :func:`zipline.api.order_target`
    :func:`zipline.api.order_target_value`
    :func:`zipline.api.order_target_percent`
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
    """

def record(self, *args, **kwargs) -> None:
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
    Sets the realtime database to use for querying up-to-date minute bars in
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

    Examples
    --------
    Set the realtime database and map fields:

    >>> algo.set_realtime_db(                 # doctest: +SKIP
            "us-stk-tick-1min",
            fields={
                "close": "LastPriceClose",
                "open": "LastPriceOpen",
                "high": "LastPriceHigh",
                "low": "LastPriceLow",
                "volume": "LastSizeSum"})
    """
    ...

def schedule_function(
    self,
    func: Callable[[TradingAlgorithm, BarData], None],
    date_rule: EventRule = None,
    time_rule: EventRule = None,
    half_days: bool = True,
    calendar: TradingCalendar = None
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
    calendar : Sentinel, optional
        Calendar used to compute rules that depend on the trading calendar.

    Examples
    --------
    Schedule a function called rebalance to run every trading day 30 minutes
    after the open:

    >>> import zipline.api as algo
    >>> algo.schedule_function(                          # doctest: +SKIP
            rebalance,
            algo.date_rules.every_day(),
            algo.time_rules.market_open(minutes=30))

    See Also
    --------
    :class:`zipline.api.date_rules`
    :class:`zipline.api.time_rules`
    """

class date_rules:
    """
    Factories for date-based :func:`~zipline.api.schedule_function` rules.

    See Also
    --------
    :func:`~zipline.api.schedule_function`
    """

    def every_day() -> EventRule:
        """Create a rule that triggers every day.

        Returns
        -------
        rule : zipline.utils.events.EventRule
        """
        ...

    def month_start(days_offset: int = 0) -> EventRule:
        """
        Create a rule that triggers a fixed number of trading days after the
        start of each month.

        Parameters
        ----------
        days_offset : int, optional
            Number of trading days to wait before triggering each
            month. Default is 0, i.e., trigger on the first trading day of the
            month.

        Returns
        -------
        rule : zipline.utils.events.EventRule
        """
        ...

    def month_end(days_offset: int = 0) -> EventRule:
        """
        Create a rule that triggers a fixed number of trading days before the
        end of each month.

        Parameters
        ----------
        days_offset : int, optional
            Number of trading days prior to month end to trigger. Default is 0,
            i.e., trigger on the last day of the month.

        Returns
        -------
        rule : zipline.utils.events.EventRule
        """
        ...

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
    """

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

    def every_minute() -> EventRule:
        """
        Create a rule that always triggers.
        """
        ...

def set_asset_restrictions(
    restrictions: Restrictions,
    on_error: str = 'fail'
    ) -> None:
    """Set a restriction on which assets can be ordered.

    Parameters
    ----------
    restricted_list : Restrictions
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
    Set the benchmark to SPY:

    >>> import zipline.api as algo
    >>> spy = algo.sid("FIBBG000BDTBL9")    # doctest: +SKIP
    >>> algo.set_benchmark(spy)             # doctest: +SKIP

    Notes
    -----
    Any dividends payed out for that new benchmark asset will be
    automatically reinvested.
    """

def set_cancel_policy(cancel_policy: CancelPolicy) -> None:
    """Sets the order cancellation policy for the simulation.

    Parameters
    ----------
    cancel_policy : CancelPolicy
        The cancellation policy to use.

    See Also
    --------
    :class:`zipline.api.EODCancel`
    :class:`zipline.api.NeverCancel`
    """

class EODCancel:
    """
    This policy cancels open orders at the end of the day. This is the default
    policy and does not need to be explicitly set. In live trading, this cancel
    policy will cause orders to be submitted with a Tif (time-in-force) of DAY.

    Parameters
    ----------
    warn_on_cancel : bool, optional
        Should a warning be raised if this causes an order to be cancelled?
    """
    def __init__(self, warn_on_cancel: bool =True):
        ...

class NeverCancel:
    """
    With this policy, orders are never automatically canceled. In live trading, this
    cancel policy will cause orders to be submitted with a Tif (time-in-force) of GTC
    (Good-till-canceled).

    Examples
    --------
    Set the cancel policy to NeverCancel:

    >>> from zipline.api import set_cancel_policy, cancel_policy    # doctest: +SKIP
    >>> def initialize(context):                                    # doctest: +SKIP
            set_cancel_policy(cancel_policy.NeverCancel())
    """
    ...

def set_commission(
    us_equities: EquityCommissionModel = None,
    us_futures: FutureCommissionModel = None
    ) -> None:
    """Sets the commission models for the simulation.

    Parameters
    ----------
    us_equities : EquityCommissionModel
        The commission model to use for trading US equities.
    us_futures : FutureCommissionModel
        The commission model to use for trading US futures.

    Notes
    -----
    This function can only be called during
    :func:`~zipline.api.initialize`.

    Examples
    --------
    Set the equities commission to 0.001 per share:

    >>> import zipline.api as algo
    >>> from zipline.finance import commission
    >>> algo.set_commission(commission.PerShare(cost=0.001))    # doctest: +SKIP

    See Also
    --------
    :class:`zipline.finance.commission.PerShare`
    :class:`zipline.finance.commission.PerTrade`
    :class:`zipline.finance.commission.PerDollar`
    """

def set_long_only(on_error: str ='fail') -> None:
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
    on_error: str = 'fail'
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
    on_error: str = 'fail'
    ) -> None:
    """Set a limit on the number of shares and/or dollar value of any single
    order placed for sid.  Limits are treated as absolute values and are
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
    on_error: str = 'fail'
    ) -> None:
    """Set a limit on the number of shares and/or dollar value held for the
    given sid. Limits are treated as absolute values and are enforced at
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
    us_equities: EquitySlippageModel = None,
    us_futures: FutureSlippageModel = None
    ) -> None:
    """Set the slippage models for the simulation.

    Parameters
    ----------
    us_equities : EquitySlippageModel
        The slippage model to use for trading US equities.
    us_futures : FutureSlippageModel
        The slippage model to use for trading US futures.

    Examples
    --------
    Set the equities slippage to 5 basis points:

    >>> import zipline.api as algo
    >>> from zipline.finance import slippage
    >>> algo.set_slippage(slippage.FixedBasisPointsSlippage(basis_points=5.0))    # doctest: +SKIP

    Notes
    -----
    This function can only be called during
    :func:`~zipline.api.initialize`.

    See Also
    --------
    :class:`zipline.finance.slippage.SlippageModel`
    """

def sid(sid: Union[str, int]) -> Asset:
    """Lookup an Asset by its unique asset identifier.

    Parameters
    ----------
    sid : int
        The unique integer that identifies an asset.

    Returns
    -------
    asset : Asset
        The asset with the given ``sid``.

    Raises
    ------
    SidsNotFound
        When a requested ``sid`` does not map to any asset.
    """
