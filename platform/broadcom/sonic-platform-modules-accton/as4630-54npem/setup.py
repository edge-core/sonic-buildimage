#!/usr/bin/env python

import os
from setuptools import setup
os.listdir

setup(
    name='as4630_54npem',
    version='1.0',
    description='Module to initialize Accton AS4630-54NPEM platforms',

    packages=['as4630_54npem'],
    package_dir={'as4630_54npem': 'as4630-54npem/classes'},
)
