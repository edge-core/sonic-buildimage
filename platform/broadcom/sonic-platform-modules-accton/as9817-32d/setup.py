#!/usr/bin/env python

import os
from setuptools import setup
os.listdir

setup(
    name='as9817_32d',
    version='1.0',
    description='Module to initialize Accton AS9817-32D platforms',

    packages=['as9817_32d'],
    package_dir={'as9817_32d': 'as9817-32d/classes'},
)
