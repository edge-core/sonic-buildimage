#!/usr/bin/env python

import os
import sys
from setuptools import setup
os.listdir

setup(
   name='minipack',
   version='1.0',
   description='Module to initialize Accton MiniPack platforms',
   
   packages=['minipack'],
   package_dir={'minipack': 'minipack/classes'},
)

