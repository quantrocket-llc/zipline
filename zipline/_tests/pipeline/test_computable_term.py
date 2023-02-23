"""Tests for common behaviors shared by all ComputableTerms.
"""
import numpy as np

from zipline.lib.labelarray import LabelArray
from zipline.pipeline import Classifier, Factor, Filter, Constant
from zipline._testing import parameter_space
from zipline.utils.numpy_utils import (
    categorical_dtype,
    datetime64ns_dtype,
    float64_dtype,
    int64_dtype,
    NaTns,
)

from .base import BaseUSEquityPipelineTestCase


class Floats(Factor):
    inputs = ()
    window_length = 0
    dtype = float64_dtype
    window_safe = True

class AltFloats(Factor):
    inputs = ()
    window_length = 0
    dtype = float64_dtype


class Dates(Factor):
    inputs = ()
    window_length = 0
    dtype = datetime64ns_dtype


class AltDates(Factor):
    inputs = ()
    window_length = 0
    dtype = datetime64ns_dtype


class Bools(Filter):
    inputs = ()
    window_length = 0


class AltBools(Filter):
    inputs = ()
    window_length = 0


class Strs(Classifier):
    inputs = ()
    window_length = 0
    dtype = categorical_dtype
    missing_value = None
    window_safe = True

class AltStrs(Classifier):
    inputs = ()
    window_length = 0
    dtype = categorical_dtype
    missing_value = None


class Ints(Classifier):
    inputs = ()
    window_length = 0
    dtype = int64_dtype
    missing_value = -1


class AltInts(Classifier):
    inputs = ()
    window_length = 0
    dtype = int64_dtype
    missing_value = -1


class FillNATestCase(BaseUSEquityPipelineTestCase):

    @parameter_space(
        null_locs=[
            # No NaNs.
            np.zeros((4, 4), dtype=bool),
            # All NaNs.
            np.ones((4, 4), dtype=bool),
            # NaNs on Diagonal
            np.eye(4, dtype=bool),
            # Nans every third element.
            (np.arange(16).reshape(4, 4) % 3) == 0,
        ]
    )
    def test_fillna_with_scalar(self, null_locs):
        shape = (4, 4)
        num_cells = shape[0] * shape[1]

        floats = np.arange(num_cells, dtype=float).reshape(shape)
        floats[null_locs] = np.nan
        float_fillval = 999.0
        float_expected = np.where(null_locs, float_fillval, floats)
        float_expected_zero = np.where(null_locs, 0.0, floats)

        dates = (np.arange(num_cells, dtype='i8')
                 .view('M8[D]')
                 .astype('M8[ns]')
                 .reshape(shape))
        dates[null_locs] = NaTns
        date_fillval = np.datetime64('2014-01-02', 'ns')
        date_expected = np.where(null_locs, date_fillval, dates)

        strs = np.arange(num_cells).astype(str).astype(object).reshape(shape)
        strs[null_locs] = None
        str_fillval = "filled"
        str_expected = np.where(null_locs, str_fillval, strs)

        ints = np.arange(num_cells, dtype='i8').reshape(shape)
        ints[null_locs] = -1
        int_fillval = 777
        int_expected = np.where(null_locs, int_fillval, ints)

        terms = {
            'floats': Floats().fillna(float_fillval),
            # Make sure we accept integer as a fill value on float-dtype
            # factors.
            'floats_fill_zero': Floats().fillna(0),
            'dates': Dates().fillna(date_fillval),
            'strs': Strs().fillna(str_fillval),
            'ints': Ints().fillna(int_fillval),
        }

        expected = {
            'floats': float_expected,
            'floats_fill_zero': float_expected_zero,
            'dates': date_expected,
            'strs': self.make_labelarray(str_expected),
            'ints': int_expected,
        }

        self.check_terms(
            terms,
            expected,
            initial_workspace={
                Floats(): floats,
                Dates(): dates,
                Strs(): self.make_labelarray(strs),
                Ints(): ints,
            },
            mask=self.build_mask(self.ones_mask(shape=(4, 4))),
        )

    @parameter_space(
        null_locs=[
            # No NaNs.
            np.zeros((4, 4), dtype=bool),
            # # All NaNs.
            np.ones((4, 4), dtype=bool),
            # NaNs on Diagonal
            np.eye(4, dtype=bool),
            # Nans every third element.
            (np.arange(16).reshape((4, 4)) % 3) == 0,
        ]
    )
    def test_fillna_with_expression(self, null_locs):
        shape = (4, 4)
        mask = self.build_mask(self.ones_mask(shape=(4, 4)))
        state = np.random.RandomState(4)
        assets = self.asset_finder.retrieve_all(mask.columns)

        def rand_vals(dtype):
            return state.randint(1, 100, shape).astype(dtype)

        floats = np.arange(16, dtype=float).reshape(shape)
        floats[null_locs] = np.nan
        float_fillval = rand_vals(float)
        float_expected = np.where(null_locs, float_fillval, floats)
        float_expected_1d = np.where(null_locs, float_fillval[:, [0]], floats)

        dates = (np.arange(16, dtype='i8')
                 .view('M8[D]')
                 .astype('M8[ns]').
                 reshape(shape))
        dates[null_locs] = NaTns
        date_fillval = rand_vals('M8[D]').astype('M8[ns]')
        date_expected = np.where(null_locs, date_fillval, dates)
        date_expected_1d = np.where(null_locs, date_fillval[:, [1]], dates)

        strs = np.arange(16).astype(str).astype(object).reshape(shape)
        strs[null_locs] = None
        str_fillval = rand_vals(str)
        str_expected = np.where(null_locs, str_fillval, strs)
        str_expected_1d = np.where(null_locs, str_fillval[:, [2]], strs)

        ints = np.arange(16).reshape(shape)
        ints[null_locs] = -1
        int_fillval = rand_vals(int64_dtype)
        int_expected = np.where(null_locs, int_fillval, ints)
        int_expected_1d = np.where(null_locs, int_fillval[:, [3]], ints)

        terms = {
            'floats': Floats().fillna(AltFloats()),
            'floats_1d': Floats().fillna(AltFloats()[assets[0]]),

            'dates': Dates().fillna(AltDates()),
            'dates_1d': Dates().fillna(AltDates()[assets[1]]),

            'strs': Strs().fillna(AltStrs()),
            'strs_1d': Strs().fillna(AltStrs()[assets[2]]),

            'ints': Ints().fillna(AltInts()),
            'ints_1d': Ints().fillna(AltInts()[assets[3]]),
        }

        expected = {
            'floats': float_expected,
            'floats_1d': float_expected_1d,
            'dates': date_expected,
            'dates_1d': date_expected_1d,
            'strs': self.make_labelarray(str_expected),
            'strs_1d': self.make_labelarray(str_expected_1d),
            'ints': int_expected,
            'ints_1d': int_expected_1d,
        }

        self.check_terms(
            terms,
            expected,
            initial_workspace={
                Floats(): floats,
                Dates(): dates,
                Strs(): self.make_labelarray(strs),
                Ints(): ints,

                AltFloats(): float_fillval,
                AltDates(): date_fillval,
                AltStrs(): self.make_labelarray(str_fillval),
                AltInts(): int_fillval,
            },
            mask=mask,
        )

    def should_error(self, f, exc_type, expected_message):
        with self.assertRaises(exc_type) as e:
            f()

        message = str(e.exception)
        self.assertEqual(message, expected_message)

    def test_bad_inputs(self):
        def dtype_for(o):
            return np.array([o]).dtype

        self.should_error(
            lambda: Floats().fillna('3.0'),
            TypeError,
            "Fill value '3.0' is not a valid choice for term Floats with"
            " dtype float64.\n\n"
            "Coercion attempt failed with: Cannot cast array data from {!r}"
            " to {!r} according to the rule 'same_kind'"
            .format(dtype_for('3.0'), np.dtype(float))
        )

        self.should_error(
            lambda: Dates().fillna('2014-01-02'),
            TypeError,
            "Fill value '2014-01-02' is not a valid choice for term Dates with"
            " dtype datetime64[ns].\n\n"
            "Coercion attempt failed with: Cannot cast array data from {!r}"
            " to {!r} according to the rule 'same_kind'"
            .format(dtype_for('2014-01-02'), np.dtype('M8[ns]'))
        )

        self.should_error(
            lambda: Ints().fillna('300'),
            TypeError,
            "Fill value '300' is not a valid choice for term Ints with"
            " dtype int64.\n\n"
            "Coercion attempt failed with: Cannot cast array data from {!r}"
            " to {!r} according to the rule 'same_kind'"
            .format(dtype_for('300'), np.dtype('i8')),
        )

        self.should_error(
            lambda: Strs().fillna(10.0),
            TypeError,
            "Fill value 10.0 is not a valid choice for term Strs with dtype"
            " object.\n\n"
            "Coercion attempt failed with: "
            "String-dtype classifiers can only produce strings or None but got 10.0"

        )

    def make_labelarray(self, strs):
        return LabelArray(strs, missing_value=None)

class WhereTestCase(BaseUSEquityPipelineTestCase):


    def test_where_with_no_fill_value(self):
        shape = (4, 4)
        num_cells = shape[0] * shape[1]

        floats = np.arange(num_cells, dtype=float).reshape(shape)
        float_expected = np.where(floats < 5, floats, np.nan)

        strs = np.arange(num_cells).astype(str).astype(object).reshape(shape)
        str_expected = np.where(strs != "5", strs, None)

        ints = np.arange(num_cells, dtype='i8').reshape(shape)
        int_expected = np.where(np.isin(ints, [5, 7]), -1, ints)

        terms = {
            'floats': Floats().where(Floats() < 5),
            'strs': Strs().where(Strs() != "5"),
            'ints': Ints().where(~Ints().isin([5,7])),
        }

        expected = {
            'floats': float_expected,
            'strs': self.make_labelarray(str_expected),
            'ints': int_expected,
        }

        self.check_terms(
            terms,
            expected,
            initial_workspace={
                Floats(): floats,
                Strs(): self.make_labelarray(strs),
                Ints(): ints,
            },
            mask=self.build_mask(self.ones_mask(shape=(4, 4))),
        )

    def test_where_fill_with_scalar(self):
        shape = (4, 4)
        num_cells = shape[0] * shape[1]

        floats = np.arange(num_cells, dtype=float).reshape(shape)
        float_fillval = 999.0
        float_expected = np.where(floats < 5, floats, float_fillval)
        float_expected_zero = np.where(floats < 5, floats, 0.0)

        strs = np.arange(num_cells).astype(str).astype(object).reshape(shape)
        str_fillval = "filled"
        str_expected = np.where(strs != "5", strs, str_fillval)

        ints = np.arange(num_cells, dtype='i8').reshape(shape)
        int_fillval = 777
        int_expected = np.where(np.isin(ints, [5, 7]), int_fillval, ints)

        terms = {
            'floats': Floats().where(Floats() < 5, float_fillval),
            # Make sure we accept integer as a fill value on float-dtype
            # factors.
            'floats_fill_zero': Floats().where(Floats() < 5, 0),
            'strs': Strs().where(Strs() != "5", str_fillval),
            'ints': Ints().where(~Ints().isin([5,7]), int_fillval),
        }

        expected = {
            'floats': float_expected,
            'floats_fill_zero': float_expected_zero,
            'strs': self.make_labelarray(str_expected),
            'ints': int_expected,
        }

        self.check_terms(
            terms,
            expected,
            initial_workspace={
                Floats(): floats,
                Strs(): self.make_labelarray(strs),
                Ints(): ints,
            },
            mask=self.build_mask(self.ones_mask(shape=(4, 4))),
        )

    def test_where_fill_with_expression(self):
        shape = (4, 4)
        mask = self.build_mask(self.ones_mask(shape=(4, 4)))
        state = np.random.RandomState(4)
        assets = self.asset_finder.retrieve_all(mask.columns)

        def rand_vals(dtype):
            return state.randint(1, 100, shape).astype(dtype)

        floats = np.arange(16, dtype=float).reshape(shape)
        float_fillval = rand_vals(float)
        float_expected = np.where(floats < 5, floats, float_fillval)
        float_expected_1d = np.where(floats < 5, floats, float_fillval[:, [0]])

        strs = np.arange(16).astype(str).astype(object).reshape(shape)
        str_fillval = rand_vals(str)
        str_expected = np.where(strs != "5", strs, str_fillval)
        str_expected_1d = np.where(strs != "5", strs, str_fillval[:, [2]])

        ints = np.arange(16).reshape(shape)
        int_fillval = rand_vals(int64_dtype)
        int_expected = np.where(np.isin(ints, [5,7]), int_fillval, ints)
        int_expected_1d = np.where(np.isin(ints, [5,7]), int_fillval[:, [3]], ints)

        terms = {
            'floats': Floats().where(Floats() < 5, AltFloats()),
            'floats_1d': Floats().where(Floats() < 5, AltFloats()[assets[0]]),

            'strs': Strs().where(Strs() != "5", AltStrs()),
            'strs_1d': Strs().where(Strs() != "5", AltStrs()[assets[2]]),

            'ints': Ints().where(~Ints().isin([5,7]), AltInts()),
            'ints_1d': Ints().where(~Ints().isin([5,7]), AltInts()[assets[3]]),
        }

        expected = {
            'floats': float_expected,
            'floats_1d': float_expected_1d,
            'strs': self.make_labelarray(str_expected),
            'strs_1d': self.make_labelarray(str_expected_1d),
            'ints': int_expected,
            'ints_1d': int_expected_1d,
        }

        self.check_terms(
            terms,
            expected,
            initial_workspace={
                Floats(): floats,
                Strs(): self.make_labelarray(strs),
                Ints(): ints,

                AltFloats(): float_fillval,
                AltStrs(): self.make_labelarray(str_fillval),
                AltInts(): int_fillval,
            },
            mask=mask,
        )

    def test_bad_inputs(self):

        with self.assertRaises(TypeError) as cm:
            Floats().where(1)

        message = str(cm.exception)
        self.assertEqual(message, "condition argument must be a Filter")

        with self.assertRaises(TypeError) as cm:
            Floats().where(Floats())

        message = str(cm.exception)
        self.assertEqual(message, "condition argument must be a Filter")

        with self.assertRaises(AttributeError) as cm:
            Bools().where(Bools())

        message = str(cm.exception)
        self.assertEqual(message, "'Bools' object has no attribute 'where'")

    def make_labelarray(self, strs):
        return LabelArray(strs, missing_value=None)

class ShiftTestCase(BaseUSEquityPipelineTestCase):

    @parameter_space(periods=[1, 2, 3])
    def test_shift(self, periods):
        shape = (4, 4)
        num_cells = shape[0] * shape[1]

        floats = np.arange(num_cells, dtype=float).reshape(shape)
        strs = np.arange(num_cells).astype(str).astype(object).reshape(shape)
        bools = floats % 3 == 0

        terms = {
            'floats': Floats().shift(periods),
            'strs': Strs().shift(periods),
            'bools': Bools().shift(periods),
        }

        expected = {
            'floats': floats[:-periods],
            'strs': self.make_labelarray(strs[:-periods]),
            'bools': bools[:-periods],
        }

        self.check_terms(
            terms,
            expected,
            initial_workspace={
                Floats(): floats,
                Strs(): self.make_labelarray(strs),
                Bools(): bools,
            },
            mask=self.build_mask(self.ones_mask(shape=(4, 4))),
        )

    def make_labelarray(self, strs):
        return LabelArray(strs, missing_value=None)

class ConstantTestCase(BaseUSEquityPipelineTestCase):

    def test_constants(self):
        shape = (4, 4)
        mask = self.build_mask(self.ones_mask(shape=(4, 4)))
        state = np.random.RandomState(4)
        assets = self.asset_finder.retrieve_all(mask.columns)

        def rand_vals(dtype):
            return state.randint(1, 100, shape).astype(dtype)

        floats = np.arange(16, dtype=float).reshape(shape)
        float_expected = np.where(floats < 5, 1.0, 2.0)

        strs = np.arange(16).astype(str).astype(object).reshape(shape)
        str_expected = np.where(strs != "5", 'dog', 'cat')

        constant_float_expected = np.array([1.0]*16, dtype=float).reshape(shape)
        constant_str_expected = np.array(['fish']*16, dtype=object).reshape(shape)
        constant_bool_expected = np.array([0.0]*16, dtype=float).reshape(shape)

        terms = {
            'floats': Constant(1).where(Floats() < 5, Constant(2.0)),
            'strs': Constant('dog').where(Strs() != "5", Constant('cat')),
            'constant_floats': Constant(1),
            'constant_strs': Constant('fish'),
            'constant_bool': Constant(False),
        }

        expected = {
            'floats': float_expected,
            'strs': self.make_labelarray(str_expected),
            'constant_floats': constant_float_expected,
            'constant_strs':  self.make_labelarray(constant_str_expected),
            'constant_bool': constant_bool_expected
        }

        self.check_terms(
            terms,
            expected,
            initial_workspace={
                Floats(): floats,
                Strs(): self.make_labelarray(strs),
            },
            mask=mask,
        )

    def make_labelarray(self, strs):
        return LabelArray(strs, missing_value=None)
