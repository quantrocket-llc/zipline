import os

from parameterized import parameterized
import pandas as pd
from toolz import valmap
import toolz.curried.operator as op
from exchange_calendars import ExchangeCalendar
from zipline.utils.calendar_utils import get_calendar

from zipline.assets.synthetic import make_simple_equity_info
from zipline.data.bundles import UnknownBundle
from zipline.data.bundles.core import _make_bundle_core
from zipline.lib.adjustment import Float64Multiply
from zipline.pipeline.loaders.synthetic import (
    make_bar_data,
    expected_bar_values_2d,
)
from zipline._testing import (
    subtest,
    str_to_seconds,
)
from zipline._testing.fixtures import WithInstanceTmpDir, ZiplineTestCase, \
    WithDefaultDateBounds
from zipline._testing.predicates import assert_equal
from zipline.utils.cache import dataframe_cache
from zipline.utils.functional import apply
import zipline.utils.paths as pth


_1_ns = pd.Timedelta(1, unit='ns')


class BundleCoreTestCase(WithInstanceTmpDir,
                         WithDefaultDateBounds,
                         ZiplineTestCase):

    START_DATE = pd.Timestamp('2014-01-06')
    END_DATE = pd.Timestamp('2014-01-10')

    def init_instance_fixtures(self):
        super(BundleCoreTestCase, self).init_instance_fixtures()
        (self.bundles,
         self.register,
         self.unregister,
         self.ingest,
         self.load) = _make_bundle_core()
        self.environ = {'ZIPLINE_ROOT': self.instance_tmpdir.path}

    def test_register_decorator(self):
        @apply
        @subtest(((c,) for c in 'abcde'), 'name')
        def _(name):
            @self.register(name)
            def ingest(*args):
                pass

            self.assertIn(name, self.bundles)
            self.assertIs(self.bundles[name].ingest, ingest)

        self._check_bundles(set('abcde'))

    def test_register_call(self):
        def ingest(*args):
            pass

        @apply
        @subtest(((c,) for c in 'abcde'), 'name')
        def _(name):
            self.register(name, ingest)
            self.assertIn(name, self.bundles)
            self.assertIs(self.bundles[name].ingest, ingest)

        assert_equal(
            valmap(op.attrgetter('ingest'), self.bundles),
            {k: ingest for k in 'abcde'},
        )
        self._check_bundles(set('abcde'))

    def _check_bundles(self, names):
        assert_equal(set(self.bundles.keys()), names)

        for name in names:
            self.unregister(name)

        self.assertFalse(self.bundles)

    def test_register_no_create(self):
        called = [False]

        @self.register('bundle', create_writers=False)
        def bundle_ingest(environ,
                          asset_db_writer,
                          minute_bar_writer,
                          daily_bar_writer,
                          adjustment_writer,
                          calendar,
                          start_session,
                          end_session,
                          cache,
                          output_dir):
            self.assertIsNone(asset_db_writer)
            self.assertIsNone(minute_bar_writer)
            self.assertIsNone(daily_bar_writer)
            self.assertIsNone(adjustment_writer)
            called[0] = True

        self.ingest('bundle', self.environ)
        self.assertTrue(called[0])

    def test_ingest(self):
        calendar = get_calendar('XNYS')
        sessions = calendar.sessions_in_range(self.START_DATE, self.END_DATE)
        minutes = calendar.sessions_minutes(
            self.START_DATE, self.END_DATE,
        )

        sids = tuple(range(3))
        equities = make_simple_equity_info(
            sids,
            self.START_DATE,
            self.END_DATE,
        )

        daily_bar_data = make_bar_data(equities, sessions)
        minute_bar_data = make_bar_data(equities, minutes)
        first_split_ratio = 0.5
        second_split_ratio = 0.1
        splits = pd.DataFrame.from_records([
            {
                'effective_date': str_to_seconds('2014-01-08'),
                'ratio': first_split_ratio,
                'sid': 0,
            },
            {
                'effective_date': str_to_seconds('2014-01-09'),
                'ratio': second_split_ratio,
                'sid': 1,
            },
        ])

        @self.register(
            'bundle',
            calendar_name='NYSE',
            start_session=self.START_DATE,
            end_session=self.END_DATE,
        )
        def bundle_ingest(environ,
                          asset_db_writer,
                          minute_bar_writer,
                          daily_bar_writer,
                          adjustment_writer,
                          calendar,
                          start_session,
                          end_session,
                          cache,
                          output_dir):
            self.assertIs(environ, self.environ)

            asset_db_writer.write(equities=equities)
            minute_bar_writer.write(minute_bar_data)
            daily_bar_writer.write(daily_bar_data)
            adjustment_writer.write(splits=splits)

            self.assertIsInstance(calendar, ExchangeCalendar)
            self.assertIsInstance(cache, dataframe_cache)

        self.ingest('bundle', environ=self.environ)
        bundle = self.load('bundle', environ=self.environ)

        assert_equal(set(bundle.asset_finder.sids), set(sids))

        columns = 'open', 'high', 'low', 'close', 'volume'

        actual = bundle.equity_minute_bar_reader.load_raw_arrays(
            columns,
            minutes[0],
            minutes[-1],
            sids,
        )

        for actual_column, colname in zip(actual, columns):
            assert_equal(
                actual_column,
                expected_bar_values_2d(minutes, sids, equities, colname),
                msg=colname,
            )

        actual = bundle.equity_daily_bar_reader.load_raw_arrays(
            columns,
            self.START_DATE,
            self.END_DATE,
            sids,
        )
        for actual_column, colname in zip(actual, columns):
            assert_equal(
                actual_column,
                expected_bar_values_2d(sessions, sids, equities, colname),
                msg=colname,
            )
        adjs_for_cols = bundle.adjustment_reader.load_pricing_adjustments(
            columns,
            sessions,
            pd.Index(sids),
        )
        for column, adjustments in zip(columns, adjs_for_cols[:-1]):
            # iterate over all the adjustments but `volume`
            assert_equal(
                adjustments,
                {
                    2: [Float64Multiply(
                        first_row=0,
                        last_row=2,
                        first_col=0,
                        last_col=0,
                        value=first_split_ratio,
                    )],
                    3: [Float64Multiply(
                        first_row=0,
                        last_row=3,
                        first_col=1,
                        last_col=1,
                        value=second_split_ratio,
                    )],
                },
                msg=column,
            )

        # check the volume, the value should be 1/ratio
        assert_equal(
            adjs_for_cols[-1],
            {
                2: [Float64Multiply(
                    first_row=0,
                    last_row=2,
                    first_col=0,
                    last_col=0,
                    value=1 / first_split_ratio,
                )],
                3: [Float64Multiply(
                    first_row=0,
                    last_row=3,
                    first_col=1,
                    last_col=1,
                    value=1 / second_split_ratio,
                )],
            },
            msg='volume',
        )

    @parameterized.expand([('load',),])
    def test_bundle_doesnt_exist(self, fnname):
        with self.assertRaises(UnknownBundle) as e:
            getattr(self, fnname)('ayy', environ=self.environ)

        assert_equal(e.exception.name, 'ayy')

    def test_load_no_data(self):
        # register but do not ingest data
        self.register('bundle', lambda *args: None)

        ts = pd.Timestamp('2014')

        with self.assertRaises(ValueError) as e:
            self.load('bundle', timestamp=ts, environ=self.environ)

        self.assertIn(
            "no data for bundle 'bundle' on or before %s" % ts,
            str(e.exception),
        )

    def _list_bundle(self):
        return {
            os.path.join(pth.data_path(['bundle', d], environ=self.environ))
            for d in os.listdir(
                pth.data_path(['bundle'], environ=self.environ),
            )
        }

    def _empty_ingest(self, _wrote_to=[]):
        """Run the nth empty ingest.

        Returns
        -------
        wrote_to : str
            The timestr of the bundle written.
        """
        if not self.bundles:
            @self.register('bundle',
                           calendar_name='NYSE',
                           start_session=pd.Timestamp('2014'),
                           end_session=pd.Timestamp('2014'))
            def _(environ,
                  asset_db_writer,
                  minute_bar_writer,
                  daily_bar_writer,
                  adjustment_writer,
                  calendar,
                  start_session,
                  end_session,
                  cache,
                  output_dir):
                _wrote_to.append(output_dir)

        _wrote_to[:] = []
        self.ingest('bundle', environ=self.environ)
        assert_equal(len(_wrote_to), 1, msg='ingest was called more than once')
        ingestions = self._list_bundle()
        self.assertIn(
            _wrote_to[0],
            ingestions,
            msg='output_dir was not in the bundle directory',
        )
        return _wrote_to[0]
