from setuptools import setup
from Cython.Build import cythonize

setup(
    name='DirectionOfArrival Module',
    ext_modules=cythonize("direction_of_arrival.pyx"),
    zip_safe=False,
)
