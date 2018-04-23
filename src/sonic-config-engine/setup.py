#!/usr/bin/env python

from setuptools import setup
import os.path
import unittest

def get_test_suite():
      test_loader = unittest.TestLoader()
      test_suite = test_loader.discover('tests', pattern='*.py')
      return test_suite

setup(name='sonic-config-engine',
      version='1.0',
      description='Utilities for generating SONiC configuration files',
      author='Taoyu Li',
      author_email='taoyl@microsoft.com',
      url='https://github.com/Azure/sonic-buildimage',
      py_modules=['portconfig', 'minigraph', 'openconfig_acl', 'sonic_platform'],
      scripts=['sonic-cfggen'],
      install_requires=['lxml', 'jinja2', 'netaddr', 'ipaddr', 'pyyaml', 'pyangbind==0.6.0'],
      test_suite='setup.get_test_suite',
     )
