from zipline.assets import Asset, Future, ContinuousFuture
from typing import Union, overload, Any, Literal, Sequence
import pandas as pd

class check_parameters(object):
    """
    Asserts that the keywords passed into the wrapped function are included
    in those passed into this decorator. If not, raise a TypeError with a
    meaningful message, unlike the one Cython returns by default.

    Also asserts that the arguments passed into the wrapped function are
    consistent with the types passed into this decorator. If not, raise a
    TypeError with a meaningful message.
    """
    ...

def handle_non_market_minutes(bar_data): ...

# the methods are summarized in the class docstring so that users hovering
# over the data object in algorithms can see the methods
class BarData:
    """
    Provides methods for accessing minutely and daily price/volume data from
    Algorithm API functions.

    Also provides utility methods to determine if an asset is alive, and if it
    has recent trade data.

    An instance of this object is passed as ``data`` to
    :func:`~zipline.api.handle_data` and
    :func:`~zipline.api.before_trading_start`.

    Methods:

    current(assets, field)
        Returns the "current" value of the given fields for the given assets
        at the current simulation time.

    history(assets, fields, bar_count, frequency)
        Returns a trailing window of length ``bar_count`` containing data for
        the given assets, fields, and frequency.

    can_trade(assets)
        Returns True if the asset is alive, the exchange is open, and there is a
        known last prices.

    is_stale(assets)
        Returns True if the asset is alive but the last price is stale.

    current_chain(continuous_future)
        Returns the current futures chain as of the simulation date.

    See the individual methods for more details.

    Notes
    -----
    Usage Guide:

    * BarData: https://qrok.it/dl/z/zipline-bardata
    """
    ...

    def __init__(self, data_portal, simulation_dt_func, data_frequency,
                 trading_calendar, restrictions): ...

    def _get_current_minute(self):
        """
        Internal utility method to get the current simulation time.

        Possible answers are:
        - whatever the algorithm's get_datetime() method returns (this is what
            `self.simulation_dt_func()` points to)
        - sometimes we're knowingly not in a market minute, like if we're in
            before_trading_start.  In that case, `self._adjust_minutes` is
            True, and we get the previous market minute.
        - if we're in daily mode, get the session label for this minute.
        """
        ...

    @overload
    def current(
        self,
        assets: Asset,
        fields: Literal['open', 'high', 'low', 'close', 'volume', 'price']
        ) -> float:
        ...

    @overload
    def current(
        self,
        assets: Asset,
        fields: Literal['last_traded']
        ) -> pd.Timestamp:
        ...

    @overload
    def current(
        self,
        assets: Sequence[Asset],
        fields: Literal['open', 'high', 'low', 'close', 'volume', 'price', 'last_traded']
        ) -> 'pd.Series[Union[float, pd.Timestamp]]':
        ...

    @overload
    def current(
        self,
        assets: Asset,
        fields: Sequence[
          Literal[
            'open', 'high', 'low', 'close', 'volume', 'price', 'last_traded']]
        ) -> 'pd.Series[Union[float, pd.Timestamp]]':
        ...

    @overload
    def current(
        self,
        assets: Sequence[Asset],
        fields: Sequence[
          Literal[
            'open',
            'high',
            'low',
            'close',
            'volume',
            'price',
            'last_traded']]
        ) -> pd.DataFrame:
        ...

    def current(self, assets, fields):
        """
        Returns the "current" value of the given fields for the given assets
        at the current simulation time.

        Parameters
        ----------
        assets : zipline.assets.Asset or iterable of zipline.assets.Asset
            The asset(s) for which data is requested.
        fields : str or iterable[str].
            Requested data field(s). Valid field names are: "price",
            "last_traded", "open", "high", "low", "close", and "volume".

        Returns
        -------
        current_value : Scalar, pandas Series, or pandas DataFrame.
            See notes below.

        Notes
        -----
        The return type of this function depends on the types of its inputs:

        - If a single asset and a single field are requested, the returned
          value is a scalar (either a float or a ``pd.Timestamp`` depending on
          the field).

        - If a single asset and a list of fields are requested, the returned
          value is a :class:`pd.Series` whose indices are the requested fields.

        - If a list of assets and a single field are requested, the returned
          value is a :class:`pd.Series` whose indices are the assets.

        - If a list of assets and a list of fields are requested, the returned
          value is a :class:`pd.DataFrame`.  The columns of the returned frame
          will be the requested fields, and the index of the frame will be the
          requested assets.

        The values produced for ``fields`` are as follows:

        - Requesting "price" produces the last known close price for the asset,
          forward-filled from an earlier minute if there is no trade this
          minute. If there is no last known value (either because the asset
          has never traded, or because it has delisted) NaN is returned. If a
          value is found, and we had to cross an adjustment boundary (split,
          dividend, etc) to get it, the value is adjusted to the current
          simulation time before being returned.

        - Requesting "open", "high", "low", or "close" produces the open, high,
          low, or close for the current minute. If no trades occurred this
          minute, ``NaN`` is returned.

        - Requesting "volume" produces the trade volume for the current
          minute. If no trades occurred this minute, 0 is returned.

        - Requesting "last_traded" produces the datetime of the last minute in
          which the asset traded, even if the asset has stopped trading. If
          there is no last known value, ``pd.NaT`` is returned.

        If the current simulation time is not a valid market time for an asset,
        we use the most recent market close instead.

        Examples
        --------
        Get the latest price for AAPL (returns a scalar):

        >>> aapl = algo.sid("FIBBG000B9XRY4")
        >>> current_price = data.current(aapl, "price")
        """
        ...

    def current_chain(
        self,
        continuous_future: ContinuousFuture
        ) -> list[Future]:
        """
        Returns the current futures chain as of the simulation date.

        Parameters
        ----------
        continuous_future : zipline.assets.ContinuousFuture
            the continuous future for which to provide the current chain

        Returns
        -------
        future_chain : list of zipline.assets.Future
            A list of active futures, where the first index is the current
            contract specified by the continuous future definition, the second
            is the next upcoming contract and so on.
        """
        ...

    @overload
    def can_trade(
        self,
        assets: Asset
        ) -> bool:
        ...

    @overload
    def can_trade(
        self,
        assets: list[Asset]
        ) -> 'pd.Series[bool]':
        ...

    def can_trade(self, assets):
        """
        For the given asset or iterable of assets, returns True if all of the
        following are true:

        1. The asset is alive for the session of the current simulation time
           (if current simulation time is not a market minute, we use the next
           session).
        2. The asset's exchange is open at the current simulation time or at
           the simulation calendar's next market minute.
        3. There is a known last price for the asset.

        Parameters
        ----------
        assets: zipline.assets.Asset or iterable of zipline.assets.Asset
            Asset(s) for which tradability should be determined.

        Notes
        -----
        The second condition above warrants some further explanation:

        - If the asset's exchange calendar is identical to the simulation
          calendar, then this condition always returns True.
        - If there are market minutes in the simulation calendar outside of
          this asset's exchange's trading hours (for example, if the simulation
          is running on the CMES calendar but the asset is MSFT, which trades
          on the NYSE), during those minutes, this condition will return False
          (for example, 3:15 am Eastern on a weekday, during which the CMES is
          open but the NYSE is closed).

        Returns
        -------
        can_trade : bool or pd.Series[bool]
            Bool or series of bools indicating whether the requested asset(s)
            can be traded in the current minute.
        """
        ...

    def _can_trade_for_asset(self, asset, dt, adjusted_dt, data_portal): ...

    @overload
    def is_stale(
        self,
        assets: Asset
        ) -> bool:
        ...

    @overload
    def is_stale(
        self,
        assets: list[Asset]
        ) -> 'pd.Series[bool]':
        ...

    def is_stale(self, assets):
        """
        For the given asset or iterable of assets, returns True if the asset
        is alive and there is no trade data for the current simulation time.

        If the asset has never traded, returns False.

        If the current simulation time is not a valid market time, we use the
        current time to check if the asset is alive, but we use the last
        market minute/day for the trade data check.

        Parameters
        ----------
        assets: zipline.assets.Asset or iterable of zipline.assets.Asset
            Asset(s) for which staleness should be determined.

        Returns
        -------
        is_stale : bool or pd.Series[bool]
            Bool or series of bools indicating whether the requested asset(s)
            are stale.
        """
        ...

    def _is_stale_for_asset(self, asset, dt, adjusted_dt, data_portal):
        ...

    @overload
    def history(
        self,
        assets: Asset,
        fields: Literal['open', 'high', 'low', 'close', 'volume', 'price', 'last_traded'],
        bar_count: int,
        frequency: Literal['1d', '1m']
        ) -> 'pd.Series[Union[float, pd.Timestamp]]':
        ...

    @overload
    def history(
        self,
        assets: Asset,
        fields: Sequence[
          Literal[
            'open',
            'high',
            'low',
            'close',
            'volume',
            'price',
            'last_traded']],
        bar_count: int,
        frequency: Literal['1d', '1m']
        ) -> pd.DataFrame:
        ...

    @overload
    def history(
        self,
        assets: Sequence[Asset],
        fields: Union[
          Literal[
            'open',
            'high',
            'low',
            'close',
            'volume',
            'price',
            'last_traded'],
          Sequence[
            Literal[
              'open',
              'high',
              'low',
              'close',
              'volume',
              'price',
              'last_traded']]],
        bar_count: int,
        frequency: Literal['1d', '1m']
        ) -> pd.DataFrame:
        ...

    def history(self, assets, fields, bar_count, frequency):
        """
        Returns a trailing window of length ``bar_count`` containing data for
        the given assets, fields, and frequency.

        Returned data is adjusted for splits, dividends, and mergers as of the
        current simulation time.

        The semantics for missing data are identical to the ones described in
        the notes for :meth:`current`.

        Parameters
        ----------
        assets: zipline.assets.Asset or iterable of zipline.assets.Asset
            The asset(s) for which data is requested.
        fields: string or iterable of string.
            Requested data field(s). Valid field names are: "price",
            "last_traded", "open", "high", "low", "close", and "volume".
        bar_count: int
            Number of data observations requested.
        frequency: str
            String indicating whether to load daily or minutely data
            observations. Pass '1m' for minutely data, '1d' for daily data.

        Returns
        -------
        history : pd.Series or pd.DataFrame
            See notes below.

        Notes
        -----
        The return type of this function depends on the types of ``assets`` and
        ``fields``:

        - If a single asset and a single field are requested, the returned
          value is a :class:`pd.Series` of length ``bar_count`` whose index is
          :class:`pd.DatetimeIndex`.

        - If a single asset and multiple fields are requested, the returned
          value is a :class:`pd.DataFrame` with shape
          ``(bar_count, len(fields))``. The frame's index will be a
          :class:`pd.DatetimeIndex`, and its columns will be ``fields``.

        - If multiple assets and a single field are requested, the returned
          value is a :class:`pd.DataFrame` with shape
          ``(bar_count, len(assets))``. The frame's index will be a
          :class:`pd.DatetimeIndex`, and its columns will be ``assets``.

        - If multiple assets and multiple fields are requested, the returned
          value is a :class:`pd.DataFrame` with shape
          ``(len(fields) * bar_count, len(assets))``. The frame's index will
          have be a :class:`pd.MultiIndex` in which level 0 will contain
          ``fields`` level 1 will be a :class:`pd.DatetimeIndex`. The columns
          will be ``assets``.

        If the current simulation time is not a valid market time, we use the
        last market close instead.

        Examples
        --------
        Get prices for the past 30 minutes for multiple assets (returns
        a DataFrame):

        >>> minute_closes = data.history(assets, "close", 30, "1m")

        Get the previous session's closing price for a single asset:

        >>> spy = algo.sid("FIBBG000BDTBL9")
        >>> spy_prior_close = data.history(spy, "close", 2, "1d").iloc[0]
        """
        ...

class InnerPosition:
    """The real values of a position.

    This exists to be owned by both a
    :class:`zipline.finance.position.Position` and a
    :class:`zipline.protocol.Position` at the same time without a cycle.
    """
    ...
