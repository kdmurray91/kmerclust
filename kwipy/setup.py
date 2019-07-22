#!/usr/bin/env python3
# Copyright 2016 Kevin Murray <spam@kdmurray.id.au>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from setuptools import setup
from setuptools.command.test import test as TestCommand
from setuptools.extension import Extension

import numpy
import versioneer

try:
    from Cython.Build import cythonize
    EXT = 'pyx'
except ImportError:
    def cythonize(x): return x
    EXT = 'c'


desc = """
kwip in python
"""

setup_requires = [
    'cython',
    'numpy',
    'pytest-runner',
]

with open('requirements.txt') as fh:
    install_requires = [req.strip() for req in fh]

test_requires = [
    'pytest',
    'pytest-runner',
    'tempdir',
]

command_classes = versioneer.get_cmdclass()
compilerargs = ['-O3', ]

setup(
    name="kwipy",
    packages=['kwipy', ],
    version=versioneer.get_version(),
    # entry_points={
    #     'console_scripts': [
    #         'kwipy-count = kwipy.scripts:count_main',
    #         'kwipy-weight = kwipy.scripts:weight_main',
    #         'kwipy-kernel = kwipy.scripts:kernel_main',
    #         'kwipy-distmat = kwipy.scripts:distmat_main',
    #         'kwipy-kernel-mpi = kwipy.mpiui:kernel_mpi_main [mpi]',
    #         'kwipy-count-mpi = kwipy.mpiui:count_mpi_main [mpi]',
    #         'kwipy-weight-mpi = kwipy.mpiui:weight_mpi_main [mpi]',
    #     ],
    # },
    # extras_require={
    #     "mpi": ["mpi4py", ],
    # },
    ext_modules=cythonize([
        Extension(
            'kwipy._counter',
            ['kwipy/_counter.{}'.format(EXT), ],
            include_dirs=[numpy.get_include(), ],
            extra_compile_args=compilerargs,
            language="c++",
        ),
    ]),
    cmdclass=command_classes,
    install_requires=install_requires,
    tests_require=test_requires,
    setup_requires=setup_requires,
    description=desc,
    author="Kevin Murray",
    author_email="kdmfoss@gmail.com",
    url="https://github.com/kdmurray91/kwip",
    keywords=[
        "bioinformatics",
        "Next-gen Sequencing",
    ],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "License :: OSI Approved :: MIT License",
    ],
)
