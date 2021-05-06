#!/usr/bin/env python
#
# Copyright 2014 Quantopian, Inc.
# Modifications Copyright 2021 QuantRocket LLC
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
from setuptools import (
    Extension,
    find_packages,
    setup,
)

import versioneer

class LazyBuildExtCommandClass(dict):
    """
    Lazy command class that defers operations requiring Cython and numpy until
    they've actually been downloaded and installed by setup_requires.
    """
    def __contains__(self, key):
        return (
            key == 'build_ext'
            or super(LazyBuildExtCommandClass, self).__contains__(key)
        )

    def __setitem__(self, key, value):
        if key == 'build_ext':
            raise AssertionError("build_ext overridden!")
        super(LazyBuildExtCommandClass, self).__setitem__(key, value)

    def __getitem__(self, key):
        if key != 'build_ext':
            return super(LazyBuildExtCommandClass, self).__getitem__(key)

        from Cython.Distutils import build_ext as cython_build_ext
        import numpy

        class build_ext(cython_build_ext):
            """
            Custom build_ext command that lazily adds numpy's include_dir to
            extensions.
            """
            def build_extensions(self):
                """
                Lazily append numpy's include directory to Extension includes.

                This is done here rather than at module scope because setup.py
                may be run before numpy has been installed, in which case
                importing numpy and calling `numpy.get_include()` will fail.
                """
                numpy_incl = numpy.get_include()
                for ext in self.extensions:
                    ext.include_dirs.append(numpy_incl)

                super(build_ext, self).build_extensions()
        return build_ext


def window_specialization(typename):
    """Make an extension for an AdjustedArrayWindow specialization."""
    return Extension(
        'zipline.lib._{name}window'.format(name=typename),
        ['zipline/lib/_{name}window.pyx'.format(name=typename)],
        depends=['zipline/lib/_windowtemplate.pxi'],
    )

ext_modules = [
    Extension('zipline.assets._assets', ['zipline/assets/_assets.pyx']),
    Extension('zipline.assets.continuous_futures',
              ['zipline/assets/continuous_futures.pyx']),
    Extension('zipline.lib.adjustment', ['zipline/lib/adjustment.pyx']),
    Extension('zipline.lib._factorize', ['zipline/lib/_factorize.pyx']),
    window_specialization('float64'),
    window_specialization('int64'),
    window_specialization('int64'),
    window_specialization('uint8'),
    window_specialization('label'),
    Extension('zipline.lib.rank', ['zipline/lib/rank.pyx']),
    Extension('zipline.data._equities', ['zipline/data/_equities.pyx']),
    Extension('zipline.data._adjustments', ['zipline/data/_adjustments.pyx']),
    Extension('zipline._protocol', ['zipline/_protocol.pyx']),
    Extension(
        'zipline.finance._finance_ext',
        ['zipline/finance/_finance_ext.pyx'],
    ),
    Extension('zipline.gens.sim_engine', ['zipline/gens/sim_engine.pyx']),
    Extension(
        'zipline.data._minute_bar_internal',
        ['zipline/data/_minute_bar_internal.pyx']
    ),
    Extension(
        'zipline.data._resample',
        ['zipline/data/_resample.pyx']
    ),
]

def get_package_data():
    data = {
        root.replace(os.sep, '.'):
        # .csv and .zip are for test fixtures
        ['*.pyi', '*.pyx', '*.pxi', '*.pxd', '*.csv', '*.zip']
        for root, dirnames, filenames in os.walk('zipline')
        if '__pycache__' not in root
    }
    data.update({
        f'zipline.resources.security_lists.leveraged_etf_list.20020103.{directory}':
        ['add', 'delete']
        for directory in os.listdir('zipline/resources/security_lists/leveraged_etf_list/20020103/')
        if '__pycache__' not in directory
    })
    return data

setup(
    name='zipline',
    version=versioneer.get_version(),
    cmdclass=LazyBuildExtCommandClass(versioneer.get_cmdclass()),
    description='A backtester for financial algorithms.',
    packages=find_packages(include=['zipline', 'zipline.*']),
    ext_modules=ext_modules,
    include_package_data=True,
    package_data=get_package_data(),
    license='Apache 2.0',
)
