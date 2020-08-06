#!/usr/bin/env python

import os
from setuptools import setup
os.listdir

setup(
   name='24x2c',
   version='1.1',
   description='Module to initialize centec e530-24x2c platforms',
   
   packages=['24x2c'],
   package_dir={'24x2c': '24x2c/classes'},
)

