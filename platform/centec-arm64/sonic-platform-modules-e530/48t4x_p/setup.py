#!/usr/bin/env python

import os
from setuptools import setup
os.listdir

setup(
   name='48t4x_p',
   version='1.1',
   description='Module to initialize centec e530-48t4x-p platforms',
   
   packages=['48t4x_p'],
   package_dir={'48t4x_p': '48t4x_p/classes'},
)

