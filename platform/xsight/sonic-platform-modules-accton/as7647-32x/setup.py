#!/usr/bin/env python

import os
import sys
from setuptools import setup
os.listdir

setup(
   name='as7647_32x',
   version='1.0',
   description='Module to initialize Accton AS7647_32X platforms',

   packages=['as7647_32x'],
   package_dir={'as7647_32x': 'as7647-32x/classes'},
)

