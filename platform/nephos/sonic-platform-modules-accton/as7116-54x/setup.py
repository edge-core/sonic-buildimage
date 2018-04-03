#!/usr/bin/env python

import os
import sys
from setuptools import setup
os.listdir

setup(
       name='as7116-54x',
       version='1.0.0',
       description='Module to initialize Accton AS7116-54X platforms',

       packages=['as7116-54x'],
       package_dir={'as7116-54x': 'as7116-54x/classes'},
    )
