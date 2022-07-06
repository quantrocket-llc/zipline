#
# Copyright 2015 Quantopian, Inc.
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

"""
Tests for the zipline.assets package
"""
from collections import namedtuple
from datetime import timedelta
from functools import partial
import os
import pickle
import string
import sys
from types import GetSetDescriptorType
from unittest import TestCase
import unittest
import uuid
import warnings

from parameterized import parameterized
import numpy as np
from numpy import full, int32, int64
import pandas as pd
from six import viewkeys
import sqlalchemy as sa

from zipline.assets import (
    Asset,
    ExchangeInfo,
    Equity,
    Future,
    AssetDBWriter,
    AssetFinder,
)
from zipline.assets.assets import OwnershipPeriod
from zipline.assets.synthetic import (
    make_commodity_future_info,
    make_rotating_equity_info,
    make_simple_equity_info,
)
from six import itervalues, integer_types
from toolz import valmap, concat

from zipline.assets.asset_writer import (
    check_version_info,
    write_version_info,
    _futures_defaults,
    SQLITE_MAX_VARIABLE_NUMBER,
)
from zipline.assets.asset_db_schema import ASSET_DB_VERSION
from zipline.errors import (
    EquitiesNotFound,
    FutureContractsNotFound,
    AssetDBVersionError,
    SidsNotFound,
    SymbolNotFound,
)
from zipline.testing import (
    all_subindices,
    empty_assets_db,
    powerset,
    tmp_asset_finder,
)
from zipline.testing.predicates import assert_equal, assert_not_equal
from zipline.testing.fixtures import (
    WithAssetFinder,
    ZiplineTestCase,
    WithTradingCalendars,
    WithTmpDir,
    WithInstanceTmpDir,
)

Case = namedtuple('Case', 'finder inputs as_of country_code expected')

minute = pd.Timedelta(minutes=1)

class AssetTestCase(TestCase):

    # Dynamically list the Asset properties we want to test.
    asset_attrs = [name for name, value in vars(Asset).items()
                   if isinstance(value, GetSetDescriptorType)]

    # Very wow
    asset = Asset(
        1337,
        real_sid='1337',
        exchange_info=ExchangeInfo('THE MOON', 'MOON', '??'),
        currency='USD',
        symbol="DOGE",
        asset_name="DOGECOIN",
        start_date=pd.Timestamp('2013-12-08 9:31', tz='UTC'),
        end_date=pd.Timestamp('2014-06-25 11:21', tz='UTC'),
        first_traded=pd.Timestamp('2013-12-08 9:31', tz='UTC'),
        auto_close_date=pd.Timestamp('2014-06-26 11:21', tz='UTC'),
    )

    test_exchange = ExchangeInfo('test full', 'test', '??')
    asset3 = Asset(3, real_sid='3', exchange_info=test_exchange, currency='USD')
    asset4 = Asset(4, real_sid='4', exchange_info=test_exchange, currency='USD')
    asset5 = Asset(
        5,
        real_sid='5',
        exchange_info=ExchangeInfo('still testing', 'still testing', '??'),
        currency='USD'
    )

    def test_asset_object(self):
        the_asset = Asset(
            5061,
            real_sid='5061',
            exchange_info=ExchangeInfo('bar', 'bar', '??'),
            currency='USD'
        )

        self.assertEqual({5061: 'foo'}[the_asset], 'foo')
        self.assertEqual(the_asset, 5061)
        self.assertEqual(5061, the_asset)

        self.assertEqual(the_asset, the_asset)
        self.assertEqual(int(the_asset), 5061)

        self.assertEqual(str(the_asset), 'Asset(5061)')

    def test_to_and_from_dict(self):
        asset_from_dict = Asset.from_dict(self.asset.to_dict())
        for attr in self.asset_attrs:
            self.assertEqual(
                getattr(self.asset, attr), getattr(asset_from_dict, attr),
            )

    def test_asset_is_pickleable(self):
        asset_unpickled = pickle.loads(pickle.dumps(self.asset))
        for attr in self.asset_attrs:
            self.assertEqual(
                getattr(self.asset, attr), getattr(asset_unpickled, attr),
            )

    def test_asset_comparisons(self):

        s_23 = Asset(23, real_sid='23', exchange_info=self.test_exchange, currency='USD')
        s_24 = Asset(24, real_sid='24', exchange_info=self.test_exchange, currency='USD')

        self.assertEqual(s_23, s_23)
        self.assertEqual(s_23, 23)
        self.assertEqual(23, s_23)
        self.assertEqual(int32(23), s_23)
        self.assertEqual(int64(23), s_23)
        self.assertEqual(s_23, int32(23))
        self.assertEqual(s_23, int64(23))
        # Check all int types:
        for int_type in integer_types:
            self.assertEqual(int_type(23), s_23)
            self.assertEqual(s_23, int_type(23))

        self.assertNotEqual(s_23, s_24)
        self.assertNotEqual(s_23, 24)
        self.assertNotEqual(s_23, "23")
        self.assertNotEqual(s_23, 23.5)
        self.assertNotEqual(s_23, [])
        self.assertNotEqual(s_23, None)
        # Compare to a value that doesn't fit into a platform int:
        self.assertNotEqual(s_23, sys.maxsize + 1)

        self.assertLess(s_23, s_24)
        self.assertLess(s_23, 24)
        self.assertGreater(24, s_23)
        self.assertGreater(s_24, s_23)

    def test_lt(self):
        self.assertTrue(self.asset3 < self.asset4)
        self.assertFalse(self.asset4 < self.asset4)
        self.assertFalse(self.asset5 < self.asset4)

    def test_le(self):
        self.assertTrue(self.asset3 <= self.asset4)
        self.assertTrue(self.asset4 <= self.asset4)
        self.assertFalse(self.asset5 <= self.asset4)

    def test_eq(self):
        self.assertFalse(self.asset3 == self.asset4)
        self.assertTrue(self.asset4 == self.asset4)
        self.assertFalse(self.asset5 == self.asset4)

    def test_ge(self):
        self.assertFalse(self.asset3 >= self.asset4)
        self.assertTrue(self.asset4 >= self.asset4)
        self.assertTrue(self.asset5 >= self.asset4)

    def test_gt(self):
        self.assertFalse(self.asset3 > self.asset4)
        self.assertFalse(self.asset4 > self.asset4)
        self.assertTrue(self.asset5 > self.asset4)

    def test_type_mismatch(self):
        if sys.version_info.major < 3:
            self.assertIsNotNone(self.asset3 < 'a')
            self.assertIsNotNone('a' < self.asset3)
        else:
            with self.assertRaises(TypeError):
                self.asset3 < 'a'
            with self.assertRaises(TypeError):
                'a' < self.asset3


class TestFuture(WithAssetFinder, ZiplineTestCase):
    @classmethod
    def make_futures_info(cls):
        return pd.DataFrame.from_dict(
            {
                2468: {
                    'symbol': 'OMH15',
                    'root_symbol': 'OM',
                    'real_sid': '2468',
                    'currency': 'USD',
                    'notice_date': pd.Timestamp('2014-01-20', tz='UTC'),
                    'expiration_date': pd.Timestamp('2014-02-20', tz='UTC'),
                    'auto_close_date': pd.Timestamp('2014-01-18', tz='UTC'),
                    'tick_size': .01,
                    'multiplier': 500.0,
                    'exchange': "TEST",
                },
                0: {
                    'symbol': 'CLG06',
                    'root_symbol': 'CL',
                    'real_sid': '0',
                    'currency': 'USD',
                    'start_date': pd.Timestamp('2005-12-01', tz='UTC'),
                    'notice_date': pd.Timestamp('2005-12-20', tz='UTC'),
                    'expiration_date': pd.Timestamp('2006-01-20', tz='UTC'),
                    'multiplier': 1.0,
                    'exchange': 'TEST',
                },
            },
            orient='index',
        )

    @classmethod
    def init_class_fixtures(cls):
        super(TestFuture, cls).init_class_fixtures()
        cls.future = cls.asset_finder.lookup_future_symbol('OMH15')
        cls.future2 = cls.asset_finder.lookup_future_symbol('CLG06')

    def test_repr(self):
        reprd = repr(self.future)
        self.assertEqual("Future(2468 [OMH15])", reprd)

    def test_reduce(self):
        assert_equal(
            pickle.loads(pickle.dumps(self.future)).to_dict(),
            self.future.to_dict(),
        )

    def test_to_and_from_dict(self):
        dictd = self.future.to_dict()
        for field in _futures_defaults.keys():
            self.assertTrue(field in dictd)

        from_dict = Future.from_dict(dictd)
        self.assertTrue(isinstance(from_dict, Future))
        self.assertEqual(self.future, from_dict)

    def test_root_symbol(self):
        self.assertEqual('OM', self.future.root_symbol)

    def test_lookup_future_symbol(self):
        """
        Test the lookup_future_symbol method.
        """
        om = TestFuture.asset_finder.lookup_future_symbol('OMH15')
        self.assertEqual(om.sid, 2468)
        self.assertEqual(om.symbol, 'OMH15')
        self.assertEqual(om.root_symbol, 'OM')
        self.assertEqual(om.notice_date, pd.Timestamp('2014-01-20', tz='UTC'))
        self.assertEqual(om.expiration_date,
                         pd.Timestamp('2014-02-20', tz='UTC'))
        self.assertEqual(om.auto_close_date,
                         pd.Timestamp('2014-01-18', tz='UTC'))

        cl = TestFuture.asset_finder.lookup_future_symbol('CLG06')
        self.assertEqual(cl.sid, 0)
        self.assertEqual(cl.symbol, 'CLG06')
        self.assertEqual(cl.root_symbol, 'CL')
        self.assertEqual(cl.start_date, pd.Timestamp('2005-12-01', tz='UTC'))
        self.assertEqual(cl.notice_date, pd.Timestamp('2005-12-20', tz='UTC'))
        self.assertEqual(cl.expiration_date,
                         pd.Timestamp('2006-01-20', tz='UTC'))

        with self.assertRaises(SymbolNotFound):
            TestFuture.asset_finder.lookup_future_symbol('')

        with self.assertRaises(SymbolNotFound):
            TestFuture.asset_finder.lookup_future_symbol('#&?!')

        with self.assertRaises(SymbolNotFound):
            TestFuture.asset_finder.lookup_future_symbol('FOOBAR')

        with self.assertRaises(SymbolNotFound):
            TestFuture.asset_finder.lookup_future_symbol('XXX99')


class AssetFinderTestCase(WithTradingCalendars, ZiplineTestCase):
    asset_finder_type = AssetFinder

    def write_assets(self, **kwargs):
        self._asset_writer.write(**kwargs)

    def init_instance_fixtures(self):
        super(AssetFinderTestCase, self).init_instance_fixtures()

        conn = self.enter_instance_context(empty_assets_db())
        self._asset_writer = AssetDBWriter(conn)
        self.asset_finder = self.asset_finder_type(conn)

    def test_dont_trigger_max_variables_error(self):
        # we will try to query for more variables than sqlite supports
        # to make sure we are properly chunking on the client side
        as_of = pd.Timestamp('2013-01-01', tz='UTC')
        # we need more sids than we can query from sqlite
        nsids = SQLITE_MAX_VARIABLE_NUMBER + 10
        sids = range(nsids)
        frame = pd.DataFrame.from_records(
            [
                {
                    'sid': sid,
                    'real_sid': str(sid),
                    'currency': 'USD',
                    'symbol':  'TEST.%d' % sid,
                    'start_date': as_of.value,
                    'end_date': as_of.value,
                    'exchange': uuid.uuid4().hex
                }
                for sid in sids
            ]
        )
        self.write_assets(equities=frame)
        assets = self.asset_finder.retrieve_equities(sids)
        assert_equal(viewkeys(assets), set(sids))

    def test_compute_lifetimes(self):
        assets_per_exchange = 4
        trading_day = self.trading_calendar.day
        first_start = pd.Timestamp('2015-04-01', tz='UTC')

        equities = pd.concat(
            [
                make_rotating_equity_info(
                    num_assets=assets_per_exchange,
                    first_start=first_start,
                    frequency=trading_day,
                    periods_between_starts=3,
                    asset_lifetime=5,
                    exchange=exchange,
                )
                for exchange in (
                    'US_EXCHANGE_1',
                    'US_EXCHANGE_2',
                    'CA_EXCHANGE',
                    'JP_EXCHANGE',
                )
            ],
            ignore_index=True,
        )
        # make every symbol unique
        equities['symbol'] = list(string.ascii_uppercase[:len(equities)])
        equities['real_sid'] = equities['symbol']

        # shuffle up the sids so they are not contiguous per exchange
        sids = np.arange(len(equities))
        np.random.RandomState(1337).shuffle(sids)
        equities.index = sids
        permute_sid = dict(zip(sids, range(len(sids)))).__getitem__

        exchanges = pd.DataFrame.from_records([
            {'exchange': 'US_EXCHANGE_1', 'country_code': 'US'},
            {'exchange': 'US_EXCHANGE_2', 'country_code': 'US'},
            {'exchange': 'CA_EXCHANGE', 'country_code': 'CA'},
            {'exchange': 'JP_EXCHANGE', 'country_code': 'JP'},
        ])
        sids_by_country = {
            'US': equities.index[:2 * assets_per_exchange],
            'CA': equities.index[
                2 * assets_per_exchange:3 * assets_per_exchange
            ],
            'JP': equities.index[3 * assets_per_exchange:],
        }

        self.write_assets(equities=equities, exchanges=exchanges)
        finder = self.asset_finder

        all_dates = pd.date_range(
            start=first_start,
            end=equities.end_date.max(),
            freq=trading_day,
        )

        for dates in all_subindices(all_dates):
            expected_with_start_raw = full(
                shape=(len(dates), assets_per_exchange),
                fill_value=False,
                dtype=bool,
            )
            expected_no_start_raw = full(
                shape=(len(dates), assets_per_exchange),
                fill_value=False,
                dtype=bool,
            )

            for i, date in enumerate(dates):
                it = equities.iloc[:4][['start_date', 'end_date']].itertuples(
                    index=False,
                )
                for j, (start, end) in enumerate(it):
                    # This way of doing the checks is redundant, but very
                    # clear.
                    if start <= date <= end:
                        expected_with_start_raw[i, j] = True
                        if start < date:
                            expected_no_start_raw[i, j] = True

            for country_codes in powerset(exchanges.country_code.unique()):
                expected_sids = pd.Int64Index(sorted(concat(
                    sids_by_country[country_code]
                    for country_code in country_codes
                )))
                permuted_sids = [
                    sid for sid in sorted(expected_sids, key=permute_sid)
                ]
                tile_count = len(country_codes) + ('US' in country_codes)
                expected_with_start = pd.DataFrame(
                    data=np.tile(
                        expected_with_start_raw,
                        tile_count,
                    ),
                    index=dates,
                    columns=pd.Int64Index(permuted_sids),
                )
                result = finder.lifetimes(
                    dates,
                    include_start_date=True,
                    country_codes=country_codes,
                )
                assert_equal(result.columns, expected_sids)
                result = result[permuted_sids]
                assert_equal(result, expected_with_start)

                expected_no_start = pd.DataFrame(
                    data=np.tile(
                        expected_no_start_raw,
                        tile_count,
                    ),
                    index=dates,
                    columns=pd.Int64Index(permuted_sids),
                )
                result = finder.lifetimes(
                    dates,
                    include_start_date=False,
                    country_codes=country_codes,
                )
                assert_equal(result.columns, expected_sids)
                result = result[permuted_sids]
                assert_equal(result, expected_no_start)

    def test_sids(self):
        # Ensure that the sids property of the AssetFinder is functioning
        self.write_assets(equities=make_simple_equity_info(
            [0, 1, 2],
            pd.Timestamp('2014-01-01'),
            pd.Timestamp('2014-01-02'),
        ))
        self.assertEqual({0, 1, 2}, set(self.asset_finder.sids))

    def test_group_by_type(self):
        equities = make_simple_equity_info(
            range(5),
            start_date=pd.Timestamp('2014-01-01'),
            end_date=pd.Timestamp('2015-01-01'),
        )
        futures = make_commodity_future_info(
            first_sid=6,
            root_symbols=['CL'],
            years=[2014],
        )
        # Intersecting sid queries, to exercise loading of partially-cached
        # results.
        queries = [
            ([0, 1, 3], [6, 7]),
            ([0, 2, 3], [7, 10]),
            (list(equities.index), list(futures.index)),
        ]
        self.write_assets(
            equities=equities,
            futures=futures,
        )
        finder = self.asset_finder
        for equity_sids, future_sids in queries:
            results = finder.group_by_type(equity_sids + future_sids)
            self.assertEqual(
                results,
                {'equity': set(equity_sids), 'future': set(future_sids)},
            )

    @parameterized.expand([
        (Equity, 'retrieve_equities', EquitiesNotFound),
        (Future, 'retrieve_futures_contracts', FutureContractsNotFound),
    ])
    def test_retrieve_specific_type(self, type_, lookup_name, failure_type):
        equities = make_simple_equity_info(
            range(5),
            start_date=pd.Timestamp('2014-01-01'),
            end_date=pd.Timestamp('2015-01-01'),
        )
        max_equity = equities.index.max()
        futures = make_commodity_future_info(
            first_sid=max_equity + 1,
            root_symbols=['CL'],
            years=[2014],
        )
        equity_sids = [0, 1]
        future_sids = [max_equity + 1, max_equity + 2, max_equity + 3]
        if type_ == Equity:
            success_sids = equity_sids
            fail_sids = future_sids
        else:
            fail_sids = equity_sids
            success_sids = future_sids

        self.write_assets(
            equities=equities,
            futures=futures,
        )
        finder = self.asset_finder
        # Run twice to exercise caching.
        lookup = getattr(finder, lookup_name)
        for _ in range(2):
            results = lookup(success_sids)
            self.assertIsInstance(results, dict)
            self.assertEqual(set(results.keys()), set(success_sids))
            self.assertEqual(
                valmap(int, results),
                dict(zip(success_sids, success_sids)),
            )
            self.assertEqual(
                {type_},
                {type(asset) for asset in itervalues(results)},
            )
            with self.assertRaises(failure_type):
                lookup(fail_sids)
            with self.assertRaises(failure_type):
                # Should fail if **any** of the assets are bad.
                lookup([success_sids[0], fail_sids[0]])

    def test_retrieve_all(self):
        equities = make_simple_equity_info(
            range(5),
            start_date=pd.Timestamp('2014-01-01'),
            end_date=pd.Timestamp('2015-01-01'),
        )
        max_equity = equities.index.max()
        futures = make_commodity_future_info(
            first_sid=max_equity + 1,
            root_symbols=['CL'],
            years=[2014],
        )
        self.write_assets(
            equities=equities,
            futures=futures,
        )
        finder = self.asset_finder
        all_sids = finder.sids
        self.assertEqual(len(all_sids), len(equities) + len(futures))
        queries = [
            # Empty Query.
            (),
            # Only Equities.
            tuple(equities.index[:2]),
            # Only Futures.
            tuple(futures.index[:3]),
            # Mixed, all cache misses.
            tuple(equities.index[2:]) + tuple(futures.index[3:]),
            # Mixed, all cache hits.
            tuple(equities.index[2:]) + tuple(futures.index[3:]),
            # Everything.
            all_sids,
            all_sids,
        ]
        for sids in queries:
            equity_sids = [i for i in sids if i <= max_equity]
            future_sids = [i for i in sids if i > max_equity]
            results = finder.retrieve_all(sids)
            self.assertEqual(sids, tuple(map(int, results)))

            self.assertEqual(
                [Equity for _ in equity_sids] +
                [Future for _ in future_sids],
                list(map(type, results)),
            )
            self.assertEqual(
                (
                    list(equities.symbol.loc[equity_sids]) +
                    list(futures.symbol.loc[future_sids])
                ),
                list(asset.symbol for asset in results),
            )

    @parameterized.expand([
        (EquitiesNotFound, 'equity', 'equities'),
        (FutureContractsNotFound, 'future contract', 'future contracts'),
        (SidsNotFound, 'asset', 'assets'),
    ])
    def test_error_message_plurality(self,
                                     error_type,
                                     singular,
                                     plural):
        try:
            raise error_type(sids=[1])
        except error_type as e:
            self.assertEqual(
                str(e),
                "No {singular} found for sid: 1.".format(singular=singular)
            )
        try:
            raise error_type(sids=[1, 2])
        except error_type as e:
            self.assertEqual(
                str(e),
                "No {plural} found for sids: [1, 2].".format(plural=plural)
            )


class AssetFinderMultipleCountries(WithTradingCalendars, ZiplineTestCase):
    def write_assets(self, **kwargs):
        self._asset_writer.write(**kwargs)

    def init_instance_fixtures(self):
        super(AssetFinderMultipleCountries, self).init_instance_fixtures()

        conn = self.enter_instance_context(empty_assets_db())
        self._asset_writer = AssetDBWriter(conn)
        self.asset_finder = AssetFinder(conn)

    @staticmethod
    def country_code(n):
        return 'A' + chr(ord('A') + n)

class TestAssetDBVersioning(ZiplineTestCase):

    def init_instance_fixtures(self):
        super(TestAssetDBVersioning, self).init_instance_fixtures()
        self.engine = eng = self.enter_instance_context(empty_assets_db())
        self.metadata = sa.MetaData(eng)
        self.metadata.reflect()

    def test_check_version(self):
        version_table = self.metadata.tables['version_info']

        # This should not raise an error
        check_version_info(self.engine, version_table, ASSET_DB_VERSION)

        # This should fail because the version is too low
        with self.assertRaises(AssetDBVersionError):
            check_version_info(
                self.engine,
                version_table,
                ASSET_DB_VERSION - 1,
            )

        # This should fail because the version is too high
        with self.assertRaises(AssetDBVersionError):
            check_version_info(
                self.engine,
                version_table,
                ASSET_DB_VERSION + 1,
            )

    def test_write_version(self):
        version_table = self.metadata.tables['version_info']
        version_table.delete().execute()

        # Assert that the version is not present in the table
        self.assertIsNone(sa.select((version_table.c.version,)).scalar())

        # This should fail because the table has no version info and is,
        # therefore, consdered v0
        with self.assertRaises(AssetDBVersionError):
            check_version_info(self.engine, version_table, -2)

        # This should not raise an error because the version has been written
        write_version_info(self.engine, version_table, -2)
        check_version_info(self.engine, version_table, -2)

        # Assert that the version is in the table and correct
        self.assertEqual(sa.select((version_table.c.version,)).scalar(), -2)

        # Assert that trying to overwrite the version fails
        with self.assertRaises(sa.exc.IntegrityError):
            write_version_info(self.engine, version_table, -3)

    def test_finder_checks_version(self):
        version_table = self.metadata.tables['version_info']
        version_table.delete().execute()
        write_version_info(self.engine, version_table, -2)
        check_version_info(self.engine, version_table, -2)

        # Assert that trying to build a finder with a bad db raises an error
        with self.assertRaises(AssetDBVersionError):
            AssetFinder(engine=self.engine)

        # Change the version number of the db to the correct version
        version_table.delete().execute()
        write_version_info(self.engine, version_table, ASSET_DB_VERSION)
        check_version_info(self.engine, version_table, ASSET_DB_VERSION)

        # Now that the versions match, this Finder should succeed
        AssetFinder(engine=self.engine)

class TestVectorizedSymbolLookup(WithAssetFinder, ZiplineTestCase):

    @classmethod
    def make_equity_info(cls):
        T = partial(pd.Timestamp, tz='UTC')

        def asset(sid, symbol, start_date, end_date):
            return dict(
                sid=sid,
                real_sid=str(sid),
                currency='USD',
                symbol=symbol,
                start_date=T(start_date),
                end_date=T(end_date),
                exchange='NYSE',
            )

        records = [
            asset(1, 'A', '2014-01-02', '2014-01-31'),
            asset(2, 'A', '2014-02-03', '2015-01-02'),
            asset(3, 'B', '2014-01-02', '2014-01-15'),
            asset(4, 'B', '2014-01-17', '2015-01-02'),
            asset(5, 'C', '2001-01-02', '2015-01-02'),
            asset(6, 'D', '2001-01-02', '2015-01-02'),
            asset(7, 'FUZZY', '2001-01-02', '2015-01-02'),
        ]
        return pd.DataFrame.from_records(records)

class TestAssetFinderPreprocessors(WithTmpDir, ZiplineTestCase):

    def test_asset_finder_doesnt_silently_create_useless_empty_files(self):
        nonexistent_path = self.tmpdir.getpath(self.id() + '__nothing_here')

        with self.assertRaises(ValueError) as e:
            AssetFinder(nonexistent_path)
        expected = "SQLite file {!r} doesn't exist.".format(nonexistent_path)
        self.assertEqual(str(e.exception), expected)

        # sqlite3.connect will create an empty file if you connect somewhere
        # nonexistent. Test that we don't do that.
        self.assertFalse(os.path.exists(nonexistent_path))


class TestExchangeInfo(ZiplineTestCase):
    def test_equality(self):
        a = ExchangeInfo('FULL NAME', 'E', 'US')
        b = ExchangeInfo('FULL NAME', 'E', 'US')

        assert_equal(a, b)

        # same full name but different canonical name
        c = ExchangeInfo('FULL NAME', 'NOT E', 'US')
        assert_not_equal(c, a)

        # same canonical name but different full name
        d = ExchangeInfo('DIFFERENT FULL NAME', 'E', 'US')
        assert_not_equal(d, a)

        # same names but different country

        e = ExchangeInfo('FULL NAME', 'E', 'JP')
        assert_not_equal(e, a)

    def test_repr(self):
        e = ExchangeInfo('FULL NAME', 'E', 'US')
        assert_equal(repr(e), "ExchangeInfo('FULL NAME', 'E', 'US')")

    def test_read_from_asset_finder(self):
        sids = list(range(8))
        exchange_names = [
            'NEW YORK STOCK EXCHANGE',
            'NEW YORK STOCK EXCHANGE',
            'NASDAQ STOCK MARKET',
            'NASDAQ STOCK MARKET',
            'TOKYO STOCK EXCHANGE',
            'TOKYO STOCK EXCHANGE',
            'OSAKA STOCK EXCHANGE',
            'OSAKA STOCK EXCHANGE',
        ]
        equities = pd.DataFrame({
            'sid': sids,
            'real_sid': [str(sid) for sid in sids],
            'currency': ['USD'] * len(sids),
            'exchange': exchange_names,
            'symbol': [chr(65 + sid) for sid in sids],
        })
        exchange_infos = [
            ExchangeInfo('NEW YORK STOCK EXCHANGE', 'NYSE', 'US'),
            ExchangeInfo('NASDAQ STOCK MARKET', 'NYSE', 'US'),
            ExchangeInfo('TOKYO STOCK EXCHANGE', 'JPX', 'JP'),
            ExchangeInfo('OSAKA STOCK EXCHANGE', 'JPX', 'JP'),
        ]
        exchange_info_table = pd.DataFrame(
            [
                (info.name, info.canonical_name, info.country_code)
                for info in exchange_infos
            ],
            columns=['exchange', 'canonical_name', 'country_code'],
        )
        expected_exchange_info_map = {
            info.name: info for info in exchange_infos
        }

        ctx = tmp_asset_finder(
            equities=equities,
            exchanges=exchange_info_table,
        )
        with ctx as af:
            actual_exchange_info_map = af.exchange_info
            assets = af.retrieve_all(sids)

        assert_equal(actual_exchange_info_map, expected_exchange_info_map)

        for asset in assets:
            expected_exchange_info = expected_exchange_info_map[
                exchange_names[asset.sid]
            ]
            assert_equal(asset.exchange_info, expected_exchange_info)


class TestWrite(WithInstanceTmpDir, ZiplineTestCase):
    def init_instance_fixtures(self):
        super(TestWrite, self).init_instance_fixtures()
        self.assets_db_path = path = os.path.join(
            self.instance_tmpdir.path,
            'assets.db',
        )
        self.writer = AssetDBWriter(path)

    def new_asset_finder(self):
        return AssetFinder(self.assets_db_path)

    def test_write_multiple_exchanges(self):
        # Incrementing by two so that start and end dates for each
        # generated Asset don't overlap (each Asset's end_date is the
        # day after its start date).
        dates = pd.date_range('2013-01-01', freq='2D', periods=5, tz='UTC')
        sids = list(range(5))
        df = pd.DataFrame.from_records(
            [
                {
                    'sid': sid,
                    'real_sid': str(sid),
                    'currency': 'USD',
                    'symbol':  str(sid),
                    'start_date': date.value,
                    'end_date': (date + timedelta(days=1)).value,

                    # Change the exchange with each mapping period. We don't
                    # currently support point in time exchange information,
                    # so we just take the most recent by end date.
                    'exchange': 'EXCHANGE-%d-%d' % (sid, n),
                }
                for n, date in enumerate(dates)
                for sid in sids
            ]
        )
        self.writer.write(equities=df)

        reader = self.new_asset_finder()
        equities = reader.retrieve_all(reader.sids)

        for eq in equities:
            expected_exchange = 'EXCHANGE-%d-%d' % (eq.sid, len(dates) - 1)
            assert_equal(eq.exchange, expected_exchange)

    def test_write_direct(self):
        # don't include anything with a default to test that those work.
        equities = pd.DataFrame({
            'sid': [0, 1],
            'real_sid': ['0', '1'],
            'currency': ['USD', 'CAD'],
            'asset_name': ['Ayy Inc.', 'Lmao LP'],
            # the full exchange name
            'exchange': ['NYSE', 'TSE'],
        })
        equity_symbol_mappings = pd.DataFrame({
            'sid': [0, 1],
            'symbol': ['AYY', 'LMAO'],
            'company_symbol':  ['AYY', 'LMAO'],
            'share_class_symbol': ['', ''],
        })
        exchanges = pd.DataFrame({
            'exchange': ['NYSE', 'TSE'],
            'country_code': ['US', 'JP'],
        })

        self.writer.write_direct(
            equities=equities,
            equity_symbol_mappings=equity_symbol_mappings,
            exchanges=exchanges,
        )

        reader = self.new_asset_finder()

        equities = reader.retrieve_all(reader.sids)
        expected_equities = [
            Equity(
                0,
                '0',
                ExchangeInfo('NYSE', 'NYSE', 'US'),
                currency='USD',
                symbol='AYY',
                asset_name='Ayy Inc.',
                start_date=pd.Timestamp(0, tz='UTC'),
                end_date=pd.Timestamp.max.tz_localize('UTC'),
                first_traded=None,
                auto_close_date=None,
                tick_size=0.01,
                multiplier=1.0,
            ),
            Equity(
                1,
                '1',
                ExchangeInfo('TSE', 'TSE', 'JP'),
                currency='CAD',
                symbol='LMAO',
                asset_name='Lmao LP',
                start_date=pd.Timestamp(0, tz='UTC'),
                end_date=pd.Timestamp.max.tz_localize('UTC'),
                first_traded=None,
                auto_close_date=None,
                tick_size=0.01,
                multiplier=1.0,
            )
        ]
        assert_equal(equities, expected_equities)

        exchange_info = reader.exchange_info
        expected_exchange_info = {
            'NYSE': ExchangeInfo('NYSE', 'NYSE', 'US'),
            'TSE': ExchangeInfo('TSE', 'TSE', 'JP'),
        }
        assert_equal(exchange_info, expected_exchange_info)
