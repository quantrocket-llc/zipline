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

import io
import pandas as pd
import numpy as np
from zipline.pipeline.filters import CustomFilter, Filter
from quantrocket.master import download_master_file
from zipline.pipeline.data.master import SecuritiesMaster

class Universe(CustomFilter):
    """
    A filter limiting to assets that are members of a universe.

    Parameters
    ----------
    code : str, required
        the universe code

    Examples
    --------
    Limit to a universe of energy stocks:

    >>> from zipline_extensions.pipeline.filters import Universe
    >>> pipe = Pipeline(screen=Universe("energy-stk"))
    """
    inputs = [SecuritiesMaster.Sid]
    window_length = 1
    params = ("code",)

    def __new__(cls, code):
        return super(Universe, cls).__new__(cls, code=code)

    def _init(self, *args, **kwargs):
        # not sure why I have to use this awkward convention to get the param
        code = kwargs["params"][0][1]
        f = io.StringIO()
        download_master_file(f, universes=code, fields="Sid")
        self._real_sids = pd.read_csv(f).Sid.tolist()
        return super(Universe, self)._init(*args, **kwargs)

    def compute(self, today, assets, out, real_sids, **params):
        out[:] = np.array([item in self._real_sids for item in real_sids[-1]])
