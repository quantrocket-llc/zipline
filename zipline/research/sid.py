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
from zipline.assets import Asset
from zipline.utils.extensions import load_extensions
from zipline.research.exceptions import ValidationError
from zipline.research._asset import asset_finder_cache
from zipline.research.bundle import _get_bundle
from quantrocket.zipline import get_default_bundle

def sid(sid: str, bundle: str = None) -> Asset:
    """
    Lookup an Asset by its unique sid in the specified bundle (or default
    bundle).

    Parameters
    ----------
    sid : str, required
        The sid to retrieve.

    bundle : str, optional
        the bundle code. If omitted, the currently active bundle (as set with
        `zipline.research.use_bundle`) will be used, or if that has not been set,
        the default bundle (as set with `quantrocket.zipline.set_default_bundle`).

    Returns
    -------
    asset : zipline.assets.Asset

    Notes
    -----
    Each asset is specific to the bundle from which it came. An
    Asset object for AAPL from bundle A cannot be used to retrieve
    AAPL data from bundle B, even if AAPL data is present in bundle
    B.

    Examples
    --------
    Get the asset object for AAPL::

        aapl = sid("FIBBG000B9XRY4", bundle="usstock-1min")
    """
    if not bundle:
        bundle = _get_bundle()
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

    zipline_sid = asset_finder.engine.execute(
        """
        SELECT
            sid
        FROM
            equities
        WHERE
            real_sid = ?
        UNION
        SELECT
            sid
        FROM
            futures_contracts
        WHERE
            real_sid = ?
        """, (sid, sid)).scalar()

    if zipline_sid is None:
        raise ValidationError(
            f"No such sid {sid} in {bundle} bundle")

    asset = asset_finder.retrieve_asset(zipline_sid)

    return asset

def symbol(symbol: str, bundle: str = None) -> Asset:
    """
    Lookup an Equity by its ticker symbol in the specified bundle
    (or default bundle).

    Ticker symbols can change over time, and this function will raise an
    error if the ticker symbol has been associated with more than one equity.
    For a more robust way to retrieve an equity, use `sid()`.

    Parameters
    ----------
    symbol : str, required
        The ticker symbol for the equity.

    bundle : str, optional
        the bundle code. If omitted, the currently active bundle (as set with
        `zipline.research.use_bundle`) will be used, or if that has not been set,
        the default bundle (as set with `quantrocket.zipline.set_default_bundle`).

    Returns
    -------
    equity : zipline.assets.Equity
        The equity with the ticker symbol.

    Raises
    ------
    SymbolNotFound
        Raised when the symbol was not held by any equity.
    MultipleSymbolsFound
        Raised when the symbol was held by more than one equity.

    Notes
    -----
    Each asset is specific to the bundle from which it came. An
    Asset object for AAPL from bundle A cannot be used to retrieve
    AAPL data from bundle B, even if AAPL data is present in bundle
    B.

    Examples
    --------
    Get the asset object for AAPL::

        aapl = symbol("AAPL", bundle="usstock-1min")
    """
    if not bundle:
        bundle = _get_bundle()
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

    asset = asset_finder.lookup_symbol(symbol.upper())

    return asset
