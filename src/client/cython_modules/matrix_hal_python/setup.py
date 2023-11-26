from setuptools import setup, Extension, find_packages
from Cython.Build import cythonize
import numpy as np
import os

# Define the extension module
extensions = [
    Extension(
        name="matrix_hal_python",
        sources=["matrix_hal_python.pyx"],
        include_dirs=[
            np.get_include(),
            "/usr/include/matrix_hal",
        ],
        libraries=["matrix_creator_hal"],
        library_dirs=["/usr/local/lib/"],
        language="c++",
        extra_compile_args=["-std=c++11", "-O3"],
    )
]

# Read contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="matrix_hal_python",
    version="0.0.8",
    author="MATRIX",
    author_email="qnlbnsl@gmail.com",
    packages=find_packages(),
    url="https://github.com/qnlbnsl/matrix-lite-py",
    description="A wrapper for MATRIX HAL Microphones in Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    ext_modules=cythonize(extensions),
    zip_safe=False,
)
