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

import pandas as pd
from zipline.utils.numpy_utils import float64_dtype
from zipline.pipeline.data import Column, DataSetFamily

class ShortableShares(DataSetFamily):
    """
    DataSetFamily representing IBKR shortable shares. In order to use
    the data in a pipeline, it must first be sliced to generate a regular
    pipeline DataSet.

    ShortableShares can be sliced along one dimension:

    - `time` : the time of day (in the bundle timezone) as of which shortable
      shares should be returned, formatted as HH:MM:SS, for example 08:45:00.

    Attributes
    ----------
    shares : float
        number of shortable shares

    Examples
    --------
    Get shortable shares as of 8:45 AM:

    >>> shares = ibkr.ShortableShares.slice(time="08:45:00").shares.latest    # doctest: +SKIP
    """
    extra_dims = [
        ('time', set(pd.date_range(
                    start=pd.Timestamp.today().normalize().replace(hour=0, minute=0),
                    end=pd.Timestamp.today().normalize().replace(hour=23, minute=59),
                    freq="1min"
                ).strftime("%H:%M:%S")))
    ]

    shares = Column(float64_dtype)
