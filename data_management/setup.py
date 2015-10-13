from __future__ import print_function

from distutils.core import setup
from distutils.extension import Extension

setup(
    author = 'Francesco De Carlo, Argonne National Laboratory',
    description = 'IMG data manamgement toolbox',
    py_modules = ['scheduling', 'globus'],
    name = 'data_management',
    requires = (
        'python',
        ),
    version = '0.1',
)
