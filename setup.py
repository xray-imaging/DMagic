from __future__ import print_function

from distutils.core import setup
from distutils.extension import Extension

setup(
    author = 'Francesco De Carlo, Argonne National Laboratory',
    description = 'IMG data manamgement toolbox',
    py_modules = ['data_management/scheduling', 'data_management/globus'],
    name = 'DMagic',
    requires = (
        'python',
        ),
    version = '0.1',
)
