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
import glob
import zipline
import warnings
from zipline.utils.run_algo import load_extensions as _load_extensions

EXTENSIONS_DIR = os.environ.get("ZIPLINE_EXTENSIONS_DIR", "/var/lib/quantrocket/zipline/extensions")

def create_extension_file(code, file_contents):
    """
    Writes a .py file to the extensions dir that defines and registers a
    bundle.
    """
    if not os.path.exists(EXTENSIONS_DIR):
        os.makedirs(EXTENSIONS_DIR, exist_ok=True)

    filepath = "{0}/bundle.{1}.py".format(EXTENSIONS_DIR, code)

    with open(filepath, "w") as f:
        f.write(file_contents)

def delete_extension_file(code):
    """
    Deletes the extension file if it exists. Returns True if it was deleted,
    False if it didn't exist.
    """
    filepath = "{0}/bundle.{1}.py".format(EXTENSIONS_DIR, code)

    if os.path.exists(filepath):
        os.remove(filepath)
        return True

    return False

def load_extensions(code=None):

    warnings.filterwarnings("ignore", "Overwriting bundle with name", UserWarning)

    extensions = glob.glob("{0}/bundle.{1}.py".format(
        EXTENSIONS_DIR, code if code else "*"))

    # In case a bundle was previously registered then the configuration
    # was removed, unload it from Zipline
    if code:
        codes = [code]
    else:
        codes = list(zipline.data.bundles.bundles.keys())

    for code in codes:

        extension_path = "{0}/bundle.{1}.py".format(EXTENSIONS_DIR, code)
        if extension_path not in extensions and code in zipline.data.bundles.bundles:
            zipline.data.bundles.unregister(code)

    _load_extensions(
        default=True,
        extensions=extensions,
        strict=True,
        environ=os.environ,
        reload=True # reload in case configuration changed since last loaded
    )
