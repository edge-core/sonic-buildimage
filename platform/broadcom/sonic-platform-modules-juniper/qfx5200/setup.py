#!/usr/bin/env python

import os
from setuptools import setup
os.listdir

setup(
   name='sonic_platform',
   version='1.0',
   description='Module to initialize Juniper QFX5200-32C-S platforms',
   
   packages=['sonic_platform'],
   package_dir={'sonic_platform': 'qfx5200/sonic_platform'},
)

