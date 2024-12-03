#!/usr/bin/env python

import os
from setuptools import setup
os.listdir

setup(
    name='as9817_32o',
    version='1.0',
    description='Module to initialize Accton AS9817-32O platforms',

    packages=['as9817_32o'],
    package_dir={'as9817_32o': 'as9817-32o/classes'},
)
