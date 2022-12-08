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
import six
from toolz import concatv
import zipline.utils.paths as pth


EXTENSIONS_DIR = os.environ.get("ZIPLINE_EXTENSIONS_DIR", "/var/lib/quantrocket/zipline/extensions")

# All of the loaded extensions. We don't want to load an extension twice.
_loaded_extensions = set()


def _load_extensions(default, extensions, strict, environ, reload=False):
    """Load all of the given extensions. Don't use this function directly;
    instead, use load_extensions, below.

    Parameters
    ----------
    default : bool
        Load the default exension (~/.zipline/extension.py)?
    extension : iterable[str]
        The paths to the extensions to load. If the path ends in ``.py`` it is
        treated as a script and executed. If it does not end in ``.py`` it is
        treated as a module to be imported.
    strict : bool
        Should failure to load an extension raise. If this is false it will
        still warn.
    environ : mapping
        The environment to use to find the default extension path.
    reload : bool, optional
        Reload any extensions that have already been loaded.
    """
    if default:
        default_extension_path = pth.default_extension(environ=environ)
        pth.ensure_file(default_extension_path)
        # put the default extension first so other extensions can depend on
        # the order they are loaded
        extensions = concatv([default_extension_path], extensions)

    for ext in extensions:
        if ext in _loaded_extensions and not reload:
            continue
        try:
            # load all of the zipline extensions
            if ext.endswith('.py'):
                with open(ext) as f:
                    ns = {}
                    six.exec_(compile(f.read(), ext, 'exec'), ns, ns)
            else:
                __import__(ext)
        except Exception as e:
            if strict:
                # if `strict` we should raise the actual exception and fail
                raise
            # without `strict` we should just log the failure
            warnings.warn(
                'Failed to load extension: %r\n%s' % (ext, e),
                stacklevel=2
            )
        else:
            _loaded_extensions.add(ext)

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
