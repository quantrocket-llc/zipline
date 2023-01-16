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

from abc import ABCMeta
import array
import binascii
from collections import deque, namedtuple
from functools import partial
from numbers import Integral
from operator import itemgetter, attrgetter
import struct

import numpy as np
import pandas as pd
from pandas import isnull
from six import with_metaclass, string_types, viewkeys, iteritems
import sqlalchemy as sa
from toolz import (
    compose,
    concat,
    concatv,
    curry,
    groupby,
    merge,
    partition_all,
    sliding_window,
    valmap,
)

from zipline.errors import (
    EquitiesNotFound,
    FutureContractsNotFound,
    SidsNotFound,
    SymbolNotFound,
)
from ._assets import (
    Asset, Equity, Future,
)
from .continuous_futures import (
    ADJUSTMENT_STYLES,
    ContinuousFuture,
    OrderedContracts,
)
from .asset_writer import (
    check_version_info,
    split_delimited_symbol,
    asset_db_table_names,
    symbol_columns,
    SQLITE_MAX_VARIABLE_NUMBER,
)
from .asset_db_schema import (
    ASSET_DB_VERSION
)
from .exchange_info import ExchangeInfo
from zipline.utils.functional import invert
from zipline.utils.memoize import lazyval
from zipline.utils.numpy_utils import as_column
from zipline.utils.preprocess import preprocess
from zipline.utils.sqlite_utils import group_into_chunks, coerce_string_to_eng

# A set of fields that need to be converted to strings before building an
# Asset to avoid unicode fields
_asset_str_fields = frozenset({
    'symbol',
    'asset_name',
    'exchange',
})

# A set of fields that need to be converted to timestamps in UTC
_asset_timestamp_fields = frozenset({
    'start_date',
    'end_date',
    'first_traded',
    'notice_date',
    'expiration_date',
    'auto_close_date',
    'rollover_date',
})

OwnershipPeriod = namedtuple('OwnershipPeriod', 'start end sid value')


def merge_ownership_periods(mappings):
    """
    Given a dict of mappings where the values are lists of
    OwnershipPeriod objects, returns a dict with the same structure with
    new OwnershipPeriod objects adjusted so that the periods have no
    gaps.

    Orders the periods chronologically, and pushes forward the end date
    of each period to match the start date of the following period. The
    end date of the last period pushed forward to the max Timestamp.
    """
    return valmap(
        lambda v: tuple(
            OwnershipPeriod(
                a.start,
                b.start,
                a.sid,
                a.value,
            ) for a, b in sliding_window(
                2,
                concatv(
                    sorted(v),
                    # concat with a fake ownership object to make the last
                    # end date be max timestamp
                    [OwnershipPeriod(
                        pd.Timestamp.max.tz_localize('utc'),
                        None,
                        None,
                        None,
                    )],
                ),
            )
        ),
        mappings,
    )


def _build_ownership_map_from_rows(rows, key_from_row, value_from_row):
    mappings = {}
    for row in rows:
        mappings.setdefault(
            key_from_row(row),
            [],
        ).append(
            OwnershipPeriod(
                pd.Timestamp(row.start_date, unit='ns', tz='utc'),
                pd.Timestamp(row.end_date, unit='ns', tz='utc'),
                row.sid,
                value_from_row(row),
            ),
        )

    return merge_ownership_periods(mappings)


def build_ownership_map(table, key_from_row, value_from_row):
    """
    Builds a dict mapping to lists of OwnershipPeriods, from a db table.
    """
    return _build_ownership_map_from_rows(
        sa.select(table.c).execute().fetchall(),
        key_from_row,
        value_from_row,
    )


def build_grouped_ownership_map(table,
                                key_from_row,
                                value_from_row,
                                group_key):
    """
    Builds a dict mapping group keys to maps of keys to to lists of
    OwnershipPeriods, from a db table.
    """
    grouped_rows = groupby(
        group_key,
        sa.select(table.c).execute().fetchall(),
    )
    return {
        key: _build_ownership_map_from_rows(
            rows,
            key_from_row,
            value_from_row,
        )
        for key, rows in grouped_rows.items()
    }


@curry
def _filter_kwargs(names, dict_):
    """Filter out kwargs from a dictionary.

    Parameters
    ----------
    names : set[str]
        The names to select from ``dict_``.
    dict_ : dict[str, any]
        The dictionary to select from.

    Returns
    -------
    kwargs : dict[str, any]
        ``dict_`` where the keys intersect with ``names`` and the values are
        not None.
    """
    return {k: v for k, v in dict_.items() if k in names and v is not None}


_filter_future_kwargs = _filter_kwargs(Future._kwargnames)
_filter_equity_kwargs = _filter_kwargs(Equity._kwargnames)


def _convert_asset_timestamp_fields(dict_):
    """
    Takes in a dict of Asset init args and converts dates to pd.Timestamps
    """
    for key in _asset_timestamp_fields & viewkeys(dict_):
        value = pd.Timestamp(dict_[key], tz='UTC')
        dict_[key] = None if isnull(value) else value
    return dict_


SID_TYPE_IDS = {
    # Asset would be 0,
    ContinuousFuture: 1,
}

CONTINUOUS_FUTURE_ROLL_STYLE_IDS = {
    'calendar': 0,
    'volume': 1,
}

CONTINUOUS_FUTURE_ADJUSTMENT_STYLE_IDS = {
    None: 0,
    'div': 1,
    'add': 2,
}


def _encode_continuous_future_sid(root_symbol,
                                  offset,
                                  roll_style,
                                  adjustment_style):
    s = struct.Struct("B 2B B B B 2B")
    # B - sid type
    # 2B - root symbol
    # B - offset (could be packed smaller since offsets of greater than 12 are
    #             probably unneeded.)
    # B - roll type
    # B - adjustment
    # 2B - empty space left for parameterized roll types

    # The root symbol currently supports 2 characters.  If 3 char root symbols
    # are needed, the size of the root symbol does not need to change, however
    # writing the string directly will need to change to a scheme of writing
    # the A-Z values in 5-bit chunks.
    a = array.array('B', [0] * s.size)
    rs = bytearray(root_symbol, 'ascii')
    values = (SID_TYPE_IDS[ContinuousFuture],
              rs[0],
              rs[1],
              offset,
              CONTINUOUS_FUTURE_ROLL_STYLE_IDS[roll_style],
              CONTINUOUS_FUTURE_ADJUSTMENT_STYLE_IDS[adjustment_style],
              0, 0)
    s.pack_into(a, 0, *values)
    return int(binascii.hexlify(a), 16)


Lifetimes = namedtuple('Lifetimes', 'sid start end')


class AssetFinder(object):
    """
    An AssetFinder is an interface to a database of Asset metadata written by
    an ``AssetDBWriter``.

    This class provides methods for looking up assets by unique integer id or
    by symbol.  For historical reasons, we refer to these unique ids as 'sids'.

    Parameters
    ----------
    engine : str or SQLAlchemy.engine
        An engine with a connection to the asset database to use, or a string
        that can be parsed by SQLAlchemy as a URI.
    future_chain_predicates : dict
        A dict mapping future root symbol to a predicate function which accepts
        a contract as a parameter and returns whether or not the contract should be
        included in the chain.

    See Also
    --------
    :class:`zipline.assets.AssetDBWriter`
    """
    @preprocess(engine=coerce_string_to_eng(require_exists=True))
    def __init__(self, engine, future_chain_predicates=None):
        self.engine = engine
        metadata = sa.MetaData(bind=engine)
        metadata.reflect(only=asset_db_table_names)
        for table_name in asset_db_table_names:
            setattr(self, table_name, metadata.tables[table_name])

        # Check the version info of the db for compatibility
        check_version_info(engine, self.version_info, ASSET_DB_VERSION)

        # Cache for lookup of assets by sid, the objects in the asset lookup
        # may be shared with the results from equity and future lookup caches.
        #
        # The top level cache exists to minimize lookups on the asset type
        # routing.
        #
        # The caches are read through, i.e. accessing an asset through
        # retrieve_asset will populate the cache on first retrieval.
        self._asset_cache = {}
        self._asset_type_cache = {}
        self._caches = (self._asset_cache, self._asset_type_cache)

        self._future_chain_predicates = future_chain_predicates \
            if future_chain_predicates is not None else {}
        self._ordered_contracts = {}

        # Populated on first call to `lifetimes`.
        self._asset_lifetimes = {}

        # Stores the max end_date of the bundle
        self._bundle_end_date = None

    @lazyval
    def exchange_info(self):
        es = sa.select(self.exchanges.c).execute().fetchall()
        return {
            name: ExchangeInfo(name, canonical_name, country_code)
            for name, canonical_name, country_code in es
        }

    @lazyval
    def symbol_ownership_map(self):
        out = {}
        for mappings in self.symbol_ownership_maps_by_country_code.values():
            for key, ownership_periods in mappings.items():
                out.setdefault(key, []).extend(ownership_periods)

        return out

    @lazyval
    def symbol_ownership_maps_by_country_code(self):
        sid_to_country_code = dict(
            sa.select((
                self.equities.c.sid,
                self.exchanges.c.country_code,
            )).where(
                self.equities.c.exchange == self.exchanges.c.exchange
            ).execute().fetchall(),
        )

        return build_grouped_ownership_map(
            table=self.equity_symbol_mappings,
            key_from_row=(
                lambda row: (row.company_symbol, row.share_class_symbol)
            ),
            value_from_row=lambda row: row.symbol,
            group_key=lambda row: sid_to_country_code[row.sid],
        )

    @lazyval
    def country_codes(self):
        return tuple(self.symbol_ownership_maps_by_country_code)

    def lookup_asset_types(self, sids):
        """
        Retrieve asset types for a list of sids.

        Parameters
        ----------
        sids : list[int]

        Returns
        -------
        types : dict[sid -> str or None]
            Asset types for the provided sids.
        """
        found = {}
        missing = set()

        for sid in sids:
            try:
                found[sid] = self._asset_type_cache[sid]
            except KeyError:
                missing.add(sid)

        if not missing:
            return found

        router_cols = self.asset_router.c

        for assets in group_into_chunks(missing):
            query = sa.select((router_cols.sid, router_cols.asset_type)).where(
                self.asset_router.c.sid.in_(map(int, assets))
            )
            for sid, type_ in query.execute().fetchall():
                missing.remove(sid)
                found[sid] = self._asset_type_cache[sid] = type_

            for sid in missing:
                found[sid] = self._asset_type_cache[sid] = None

        return found

    def group_by_type(self, sids):
        """
        Group a list of sids by asset type.

        Parameters
        ----------
        sids : list[int]

        Returns
        -------
        types : dict[str or None -> list[int]]
            A dict mapping unique asset types to lists of sids drawn from sids.
            If we fail to look up an asset, we assign it a key of None.
        """
        return invert(self.lookup_asset_types(sids))

    def retrieve_asset(self, sid, default_none=False):
        """
        Retrieve the Asset for a given sid.
        """
        try:
            asset = self._asset_cache[sid]
            if asset is None and not default_none:
                raise SidsNotFound(sids=[sid])
            return asset
        except KeyError:
            return self.retrieve_all((sid,), default_none=default_none)[0]

    def retrieve_all(self, sids, default_none=False):
        """
        Retrieve all assets in `sids`.

        Parameters
        ----------
        sids : iterable of int
            Assets to retrieve.
        default_none : bool
            If True, return None for failed lookups.
            If False, raise `SidsNotFound`.

        Returns
        -------
        assets : list[Asset or None]
            A list of the same length as `sids` containing Assets (or Nones)
            corresponding to the requested sids.

        Raises
        ------
        SidsNotFound
            When a requested sid is not found and default_none=False.
        """
        sids = list(sids)
        hits, missing, failures = {}, set(), []
        for sid in sids:
            try:
                asset = self._asset_cache[sid]
                if not default_none and asset is None:
                    # Bail early if we've already cached that we don't know
                    # about an asset.
                    raise SidsNotFound(sids=[sid])
                hits[sid] = asset
            except KeyError:
                missing.add(sid)

        # All requests were cache hits.  Return requested sids in order.
        if not missing:
            return [hits[sid] for sid in sids]

        update_hits = hits.update

        # Look up cache misses by type.
        type_to_assets = self.group_by_type(missing)

        # Handle failures
        failures = {failure: None for failure in type_to_assets.pop(None, ())}
        update_hits(failures)
        self._asset_cache.update(failures)

        if failures and not default_none:
            raise SidsNotFound(sids=list(failures))

        # We don't update the asset cache here because it should already be
        # updated by `self.retrieve_equities`.
        update_hits(self.retrieve_equities(type_to_assets.pop('equity', ())))
        update_hits(
            self.retrieve_futures_contracts(type_to_assets.pop('future', ()))
        )

        # We shouldn't know about any other asset types.
        if type_to_assets:
            raise AssertionError(
                "Found asset types: %s" % list(type_to_assets.keys())
            )

        return [hits[sid] for sid in sids]

    def retrieve_equities(self, sids):
        """
        Retrieve Equity objects for a list of sids.

        Users generally shouldn't need to this method (instead, they should
        prefer the more general/friendly `retrieve_assets`), but it has a
        documented interface and tests because it's used upstream.

        Parameters
        ----------
        sids : iterable[int]

        Returns
        -------
        equities : dict[int -> Equity]

        Raises
        ------
        EquitiesNotFound
            When any requested asset isn't found.
        """
        return self._retrieve_assets(sids, self.equities, Equity)

    def _retrieve_equity(self, sid):
        return self.retrieve_equities((sid,))[sid]

    def retrieve_futures_contracts(self, sids):
        """
        Retrieve Future objects for an iterable of sids.

        Users generally shouldn't need to this method (instead, they should
        prefer the more general/friendly `retrieve_assets`), but it has a
        documented interface and tests because it's used upstream.

        Parameters
        ----------
        sids : iterable[int]

        Returns
        -------
        equities : dict[int -> Equity]

        Raises
        ------
        EquitiesNotFound
            When any requested asset isn't found.
        """
        return self._retrieve_assets(sids, self.futures_contracts, Future)

    @staticmethod
    def _select_assets_by_sid(asset_tbl, sids):
        return sa.select([asset_tbl]).where(
            asset_tbl.c.sid.in_(map(int, sids))
        )

    @staticmethod
    def _select_asset_by_symbol(asset_tbl, symbol):
        return sa.select([asset_tbl]).where(asset_tbl.c.symbol == symbol)

    def _select_most_recent_symbols_chunk(self, sid_group):
        """Retrieve the most recent symbol for a set of sids.

        Parameters
        ----------
        sid_group : iterable[int]
            The sids to lookup. The length of this sequence must be less than
            or equal to SQLITE_MAX_VARIABLE_NUMBER because the sids will be
            passed in as sql bind params.

        Returns
        -------
        sel : Selectable
            The sqlalchemy selectable that will query for the most recent
            symbol for each sid.

        Notes
        -----
        This is implemented as an inner select of the columns of interest
        ordered by the end date of the (sid, symbol) mapping. We then group
        that inner select on the sid with no aggregations to select the last
        row per group which gives us the most recently active symbol for all
        of the sids.
        """
        cols = self.equity_symbol_mappings.c

        # These are the columns we actually want.
        data_cols = (cols.sid,) + tuple(cols[name] for name in symbol_columns)

        # Also select the max of end_date so that all non-grouped fields take
        # on the value associated with the max end_date. The SQLite docs say
        # this:
        #
        # When the min() or max() aggregate functions are used in an aggregate
        # query, all bare columns in the result set take values from the input
        # row which also contains the minimum or maximum. Only the built-in
        # min() and max() functions work this way.
        #
        # See https://www.sqlite.org/lang_select.html#resultset, for more info.
        to_select = data_cols + (sa.func.max(cols.end_date),)

        return sa.select(
            to_select,
        ).where(
            cols.sid.in_(map(int, sid_group))
        ).group_by(
            cols.sid,
        )

    def _lookup_most_recent_symbols(self, sids):
        return {
            row.sid: {c: row[c] for c in symbol_columns}
            for row in concat(
                self.engine.execute(
                    self._select_most_recent_symbols_chunk(sid_group),
                ).fetchall()
                for sid_group in partition_all(
                    SQLITE_MAX_VARIABLE_NUMBER,
                    sids
                )
            )
        }

    def _retrieve_asset_dicts(self, sids, asset_tbl, querying_equities):
        if not sids:
            return

        if querying_equities:
            def mkdict(row,
                       exchanges=self.exchange_info,
                       symbols=self._lookup_most_recent_symbols(sids)):
                d = dict(row)
                d['exchange_info'] = exchanges[d.pop('exchange')]
                # we are not required to have a symbol for every asset, if
                # we don't have any symbols we will just use the empty string
                return merge(d, symbols.get(row['sid'], {}))
        else:
            def mkdict(row, exchanges=self.exchange_info):
                d = dict(row)
                d['exchange_info'] = exchanges[d.pop('exchange')]
                return d

        for assets in group_into_chunks(sids):
            # Load misses from the db.
            query = self._select_assets_by_sid(asset_tbl, assets)

            for row in query.execute().fetchall():
                yield _convert_asset_timestamp_fields(mkdict(row))

    def _retrieve_assets(self, sids, asset_tbl, asset_type):
        """
        Internal function for loading assets from a table.

        This should be the only method of `AssetFinder` that writes Assets into
        self._asset_cache.

        Parameters
        ---------
        sids : iterable of int
            Asset ids to look up.
        asset_tbl : sqlalchemy.Table
            Table from which to query assets.
        asset_type : type
            Type of asset to be constructed.

        Returns
        -------
        assets : dict[int -> Asset]
            Dict mapping requested sids to the retrieved assets.
        """
        # Fastpath for empty request.
        if not sids:
            return {}

        cache = self._asset_cache
        hits = {}

        querying_equities = issubclass(asset_type, Equity)
        filter_kwargs = (
            _filter_equity_kwargs
            if querying_equities else
            _filter_future_kwargs
        )

        rows = self._retrieve_asset_dicts(sids, asset_tbl, querying_equities)
        for row in rows:
            sid = row['sid']
            asset = asset_type(**filter_kwargs(row))
            hits[sid] = cache[sid] = asset

        # If we get here, it means something in our code thought that a
        # particular sid was an equity/future and called this function with a
        # concrete type, but we couldn't actually resolve the asset.  This is
        # an error in our code, not a user-input error.
        misses = tuple(set(sids) - viewkeys(hits))
        if misses:
            if querying_equities:
                raise EquitiesNotFound(sids=misses)
            else:
                raise FutureContractsNotFound(sids=misses)
        return hits

    def _choose_symbol_ownership_map(self, country_code):
        if country_code is None:
            return self.symbol_ownership_map

        return self.symbol_ownership_maps_by_country_code.get(country_code)



    def lookup_future_symbol(self, symbol):
        """Lookup a future contract by symbol.

        Parameters
        ----------
        symbol : str
            The symbol of the desired contract.

        Returns
        -------
        future : Future
            The future contract referenced by ``symbol``.

        Raises
        ------
        SymbolNotFound
            Raised when no contract named 'symbol' is found.

        """

        data = self._select_asset_by_symbol(self.futures_contracts, symbol)\
                   .execute().fetchone()

        # If no data found, raise an exception
        if not data:
            raise SymbolNotFound(symbol=symbol)
        return self.retrieve_asset(data['sid'])

    def _get_contract_sids(self, root_symbol):
        fc_cols = self.futures_contracts.c

        return [r.sid for r in
                list(sa.select((fc_cols.sid,)).where(
                    (fc_cols.root_symbol == root_symbol) &
                    (pd.notnull(fc_cols.start_date))).order_by(
                        fc_cols.auto_close_date).execute().fetchall())]

    def _get_root_symbol_exchange(self, root_symbol):
        fc_cols = self.futures_root_symbols.c

        fields = (fc_cols.exchange,)

        exchange = sa.select(fields).where(
            fc_cols.root_symbol == root_symbol).execute().scalar()

        if exchange is not None:
            return exchange
        else:
            raise SymbolNotFound(symbol=root_symbol)

    def get_ordered_contracts(self, root_symbol):
        try:
            return self._ordered_contracts[root_symbol]
        except KeyError:
            contract_sids = self._get_contract_sids(root_symbol)
            contracts = deque(self.retrieve_all(contract_sids))
            chain_predicate = self._future_chain_predicates.get(root_symbol,
                                                                None)
            oc = OrderedContracts(root_symbol, contracts, chain_predicate)
            self._ordered_contracts[root_symbol] = oc
            return oc

    def create_continuous_future(self,
                                 root_symbol,
                                 offset,
                                 roll_style,
                                 adjustment):
        if adjustment not in ADJUSTMENT_STYLES:
            raise ValueError(
                'Invalid adjustment style {!r}. Allowed adjustment styles are '
                '{}.'.format(adjustment, list(ADJUSTMENT_STYLES))
            )

        oc = self.get_ordered_contracts(root_symbol)
        exchange = self._get_root_symbol_exchange(root_symbol)

        sid = _encode_continuous_future_sid(root_symbol, offset,
                                            roll_style,
                                            None)
        mul_sid = _encode_continuous_future_sid(root_symbol, offset,
                                                roll_style,
                                                'div')
        add_sid = _encode_continuous_future_sid(root_symbol, offset,
                                                roll_style,
                                                'add')

        cf_template = partial(
            ContinuousFuture,
            root_symbol=root_symbol,
            offset=offset,
            roll_style=roll_style,
            start_date=oc.start_date,
            end_date=oc.end_date,
            exchange_info=self.exchange_info[exchange],
        )

        cf = cf_template(sid=sid)
        mul_cf = cf_template(sid=mul_sid, adjustment='mul')
        add_cf = cf_template(sid=add_sid, adjustment='add')

        self._asset_cache[cf.sid] = cf
        self._asset_cache[mul_cf.sid] = mul_cf
        self._asset_cache[add_cf.sid] = add_cf

        return {None: cf, 'mul': mul_cf, 'add': add_cf}[adjustment]

    def _make_sids(tblattr):
        def _(self):
            return tuple(map(
                itemgetter('sid'),
                sa.select((
                    getattr(self, tblattr).c.sid,
                )).execute().fetchall(),
            ))

        return _

    sids = property(
        _make_sids('asset_router'),
        doc='All the sids in the asset finder.',
    )
    equities_sids = property(
        _make_sids('equities'),
        doc='All of the sids for equities in the asset finder.',
    )
    futures_sids = property(
        _make_sids('futures_contracts'),
        doc='All of the sids for futures contracts in the asset finder.',
    )
    del _make_sids

    def get_bundle_end_date(self):
        """
        Returns the max end_date of the bundle, which can be considered the date
        through which the bundle has been updated.
        """
        if not self._bundle_end_date:
            max_date = self.engine.execute(
                """
                SELECT
                    MAX(end_date)
                FROM (
                    SELECT
                        end_date
                    FROM
                        equities
                    UNION
                    SELECT
                        end_date
                    FROM
                        futures_contracts
                )
                """
                ).scalar()
            self._bundle_end_date = pd.Timestamp(max_date, tz="UTC")

        return self._bundle_end_date

    def _compute_asset_lifetimes(self, country_codes):
        """
        Compute and cache a recarray of asset lifetimes.
        """
        sids = starts = ends = []
        equities_cols = self.equities.c
        futures_cols = self.futures_contracts.c
        if country_codes:
            equities_query = sa.select((
                equities_cols.sid,
                equities_cols.start_date,
                equities_cols.auto_close_date,
            )).where(
                (self.exchanges.c.exchange == equities_cols.exchange) &
                (self.exchanges.c.country_code.in_(country_codes))
            )
            futures_query = sa.select((
                futures_cols.sid,
                futures_cols.start_date,
                futures_cols.auto_close_date,
            )).where(
                (self.exchanges.c.exchange == futures_cols.exchange) &
                (self.exchanges.c.country_code.in_(country_codes))
            )
            results = equities_query.union(futures_query).execute().fetchall()
            if results:
                sids, starts, ends = zip(*results)

        sid = np.array(sids, dtype='i8')
        start = np.array(starts, dtype='f8')
        end = np.array(ends, dtype='f8')
        start[np.isnan(start)] = 0  # convert missing starts to 0
        end[end==np.datetime64('NaT').view('i8')] = np.iinfo(int).max  # convert missing end to INTMAX
        return Lifetimes(sid, start.astype('i8'), end.astype('i8'))

    def lifetimes(self, dates, include_start_date, country_codes):
        """
        Compute a DataFrame representing asset lifetimes for the specified date
        range.

        Parameters
        ----------
        dates : pd.DatetimeIndex
            The dates for which to compute lifetimes.
        include_start_date : bool
            Whether or not to count the asset as alive on its start_date.

            This is useful in a backtesting context where `lifetimes` is being
            used to signify "do I have data for this asset as of the morning of
            this date?"  For many financial metrics, (e.g. daily close), data
            isn't available for an asset until the end of the asset's first
            day.
        country_codes : iterable[str]
            The country codes to get lifetimes for.

        Returns
        -------
        lifetimes : pd.DataFrame
            A frame of dtype bool with `dates` as index and an Int64Index of
            assets as columns.  The value at `lifetimes.loc[date, asset]` will
            be True iff `asset` existed on `date`.  If `include_start_date` is
            False, then lifetimes.loc[date, asset] will be false when date ==
            asset.start_date.

        See Also
        --------
        numpy.putmask
        zipline.pipeline.engine.SimplePipelineEngine._compute_root_mask
        """
        if isinstance(country_codes, string_types):
            raise TypeError(
                "Got string {!r} instead of an iterable of strings in "
                "AssetFinder.lifetimes.".format(country_codes),
            )

        # normalize to a cache-key so that we can memoize results.
        country_codes = frozenset(country_codes)

        lifetimes = self._asset_lifetimes.get(country_codes)
        if lifetimes is None:
            self._asset_lifetimes[country_codes] = lifetimes = (
                self._compute_asset_lifetimes(country_codes)
            )

        raw_dates = as_column(dates.asi8)
        if include_start_date:
            mask = lifetimes.start <= raw_dates
        else:
            mask = lifetimes.start < raw_dates
        mask &= (raw_dates <= lifetimes.end)

        return pd.DataFrame(mask, index=dates, columns=lifetimes.sid)

    def equities_sids_for_country_code(self, country_code):
        """Return all of the sids for a given country.

        Parameters
        ----------
        country_code : str
            An ISO 3166 alpha-2 country code.

        Returns
        -------
        tuple[int]
            The sids whose exchanges are in this country.
        """
        sids = self._compute_asset_lifetimes([country_code]).sid
        return tuple(sids.tolist())


class AssetConvertible(with_metaclass(ABCMeta)):
    """
    ABC for types that are convertible to integer-representations of
    Assets.

    Includes Asset, six.string_types, and Integral
    """
    pass


AssetConvertible.register(Asset)


class NotAssetConvertible(ValueError):
    pass


class PricingDataAssociable(with_metaclass(ABCMeta)):
    """
    ABC for types that can be associated with pricing data.

    Includes Asset, Future, ContinuousFuture
    """
    pass


PricingDataAssociable.register(Asset)
PricingDataAssociable.register(Future)
PricingDataAssociable.register(ContinuousFuture)
