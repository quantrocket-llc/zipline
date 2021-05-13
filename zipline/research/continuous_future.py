#
# Copyright 2020 QuantRocket LLC
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

import os
import pandas as pd
from zipline.data import bundles
from zipline.utils.extensions import load_extensions
from zipline.research.exceptions import ValidationError
from zipline.research._asset import asset_finder_cache
from quantrocket.zipline import get_default_bundle

def continuous_future(root_symbol_str, offset=0, roll="volume", adjustment="mul", bundle=None):
    """
    Return a ContinuousFuture object for the specified root symbol in the specified bundle
    (or default bundle).

    Parameters
    ----------
    root_symbol_str : str
        The root symbol for the future chain.

    offset : int, optional
        The distance from the primary contract. Default is 0.

    roll : str, optional
        How rolls are determined. Possible choices: 'volume',
        (roll when back contract volume exceeds front contract
        volume), or 'calendar' (roll on rollover date). Default
        is 'volume'.

    adjustment : str, optional
        Method for adjusting lookback prices between rolls. Possible choices:
        'mul', 'add', None. Default is 'mul'.

    bundle : str, optional
        the bundle code. If omitted, the default bundle will be used (and must be set).

    Returns
    -------
    asset : zipline.assets.ContinuousFuture

    Examples
    --------
    Get the continuous future object for ES and get the current chain as of
    2020-09-18:

    >>> es = continuous_future("ES", roll="volume", bundle="es-1min")    # doctest: +SKIP
    >>> data = get_data("2020-09-18 10:00:00", bundle="es-1min")         # doctest: +SKIP
    >>> print(data.current_chain(es))                                    # doctest: +SKIP
    """
    if not bundle:
        bundle = get_default_bundle()
        if not bundle:
            raise ValidationError("you must specify a bundle or set a default bundle")
        bundle = bundle["default_bundle"]

    load_extensions(code=bundle)

    bundle_data = bundles.load(
        bundle,
        os.environ,
        pd.Timestamp.utcnow(),
    )
    asset_finder = asset_finder_cache.get(bundle, bundle_data.asset_finder)
    asset_finder_cache[bundle] = asset_finder

    continuous_future = asset_finder.create_continuous_future(
        root_symbol_str,
        offset,
        roll,
        adjustment,
    )

    return continuous_future
