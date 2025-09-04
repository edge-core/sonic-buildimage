#!/usr/bin/env python

import os
import sys
from setuptools import setup
os.listdir

setup(
   name='as9647_32d',
   version='1.0',
   description='Module to initialize Accton AS9647_32D platforms',

   packages=['as9647_32d'],
   package_dir={'as9647_32d': 'as9647-32d/classes'},
)

