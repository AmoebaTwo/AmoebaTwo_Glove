#!/usr/bin/env python3
from distutils.core import setup

setup(
    name='amoebatwo_glove',
    version='0.1',
    description='AmoebaTwo HTTP server',
    author='Chris Alexander',
    author_email='chris@chris-alexander.co.uk',
    license='MIT',
    url='https://github.com/chrisalexander/AmoebaTwo_Glove',
    py_modules=['amoebatwo_glove'],
    requires=['amoebatwo', 'tornado'],
)
