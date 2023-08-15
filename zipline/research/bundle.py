#
# Copyright 2023 QuantRocket LLC
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

from zipline.utils.extensions import load_extensions

_bundle = None

def _get_bundle() -> str:
    global _bundle
    return _bundle

def use_bundle(bundle: str) -> None:
    """
    Temporarily set the default bundle to use for subsequent research calls.

    This function should typically be used at the start of a notebook to set
    the default bundle to use for the duration of the notebook. The bundle
    you set is applicable to any subsequent `zipline.research` function in the
    notebook that accepts a `bundle` parameter.

    This function differs from the `quantrocket.zipline.set_default_bundle` function
    in that it sets the default bundle temporarily and applies to research functions
    defined in the `zipline.research` package, where `quantrocket.zipline.set_default_bundle`
    sets the default bundle persistently and applies to backtesting and
    trading functions defined in the `quantrocket.zipline` package as well as the
    `zipline.research` package. It is not necessary to use this function if you have
    already set a default bundle via `quantrocket.zipline.set_default_bundle` and
    want to use that bundle. If both functions have been used to set a bundle, this
    function takes precedence.

    Parameters
    ----------
    bundle : str, required
        the bundle code

    Examples
    --------
    Set the bundle to use for subsequent research calls:

    >>> use_bundle("usstock-1min")

    See Also
    --------
    quantrocket.zipline.set_default_bundle : Set the default bundle to use for backtesting and trading.
    """
    load_extensions(code=bundle)

    global _bundle
    _bundle = bundle
