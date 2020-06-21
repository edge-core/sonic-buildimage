#!/usr/bin/env python

from setuptools import setup

setup(name='sonic-bgpcfgd',
      version='1.0',
      description='Utility to dynamically generate BGP configuration for FRR',
      author='Pavel Shirshov',
      author_email='pavelsh@microsoft.com',
      url='https://github.com/Azure/sonic-buildimage',
      scripts=['bgpcfgd'],
      install_requires=['jinja2>=2.10', 'netaddr', 'pyyaml'],
      setup_requires=['pytest-runner', 'pytest'],
)
