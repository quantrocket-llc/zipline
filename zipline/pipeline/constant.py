# Copyright 2022 QuantRocket LLC - All Rights Reserved
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

from zipline.utils.numpy_utils import float64_dtype, object_dtype, bool_dtype
from zipline.pipeline.factors import Factor
from zipline.pipeline.filters import Filter
from zipline.pipeline.classifiers import Classifier
from zipline.pipeline.mixins import ConstantMixin
from numpy import nan

class Constant:
    """
    Pipeline term that returns a constant value.

    Parameters
    ----------
    const : scalar, required
        the constant value. This can be a float, int, str or bool.

    Examples
    --------
    Create a Pipeline term consisting of ones:

    >>> ones = Constant(1)
    """

    window_length = 0
    inputs = ()

    def __new__(cls, const):
        if isinstance(const, (float, int)):
            term_cls = Factor
            dtype = float64_dtype
            missing_value = nan
        elif isinstance(const, bool):
            term_cls = Filter
            dtype = bool_dtype
            missing_value = False
        elif isinstance(const, str):
            term_cls = Classifier
            dtype = object_dtype
            missing_value = ""
        else:
            raise ValueError("const must be a float or bool or int or str")

        return term_cls._with_mixin(ConstantMixin)(
            const=const,
            inputs=cls.inputs,
            window_length=cls.window_length,
            dtype=dtype,
            missing_value=missing_value
        )
