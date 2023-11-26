from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy

extensions = [
    Extension(
        "_matrix_hal",
        ["matrix_hal.pyx"],
        include_dirs=[numpy.get_include()],  # Add this line
        libraries=[],  # Add your libraries here
        library_dirs=[],
    ),  # Add your library directories here
]

setup(
    name="Matrix HAL Wrapper",
    ext_modules=cythonize(extensions),
)


# sudo apt-get install libopenblas-dev
