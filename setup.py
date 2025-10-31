from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy

def window_specialization(name):
    return Extension(
        f"zipline.lib._{name}window",
        [f"zipline/lib/_{name}window.pyx"],
        depends=["zipline/lib/_windowtemplate.pxi"],
        include_dirs=[numpy.get_include()],
    )

common_includes = [numpy.get_include()]

ext_modules = [
    Extension("zipline.assets._assets", ["zipline/assets/_assets.pyx"], include_dirs=common_includes),
    Extension("zipline.assets.continuous_futures", ["zipline/assets/continuous_futures.pyx"], include_dirs=common_includes),
    Extension("zipline.lib.adjustment", ["zipline/lib/adjustment.pyx"], include_dirs=common_includes),
    Extension("zipline.lib._factorize", ["zipline/lib/_factorize.pyx"], include_dirs=common_includes),
    window_specialization("float64"),
    window_specialization("int64"),
    window_specialization("uint8"),
    window_specialization("label"),
    Extension("zipline.lib.rank", ["zipline/lib/rank.pyx"], include_dirs=common_includes),
    Extension("zipline.data._equities", ["zipline/data/_equities.pyx"], include_dirs=common_includes),
    Extension("zipline.data._adjustments", ["zipline/data/_adjustments.pyx"], include_dirs=common_includes),
    Extension("zipline._protocol", ["zipline/_protocol.pyx"], include_dirs=common_includes),
    Extension("zipline.finance._finance_ext", ["zipline/finance/_finance_ext.pyx"], include_dirs=common_includes),
    Extension("zipline.gens.sim_engine", ["zipline/gens/sim_engine.pyx"], include_dirs=common_includes),
    Extension("zipline.data._minute_bar_internal", ["zipline/data/_minute_bar_internal.pyx"], include_dirs=common_includes),
    Extension("zipline.data._resample", ["zipline/data/_resample.pyx"], include_dirs=common_includes),
]

setup(
    ext_modules=cythonize(ext_modules),
)
