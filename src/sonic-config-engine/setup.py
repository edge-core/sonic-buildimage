#!/usr/bin/env python

from setuptools import setup
import os.path
import unittest
import glob

def get_test_suite():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='*.py')
    return test_suite

setup(
    name = 'sonic-config-engine',
    version = '1.0',
    description = 'Utilities for generating SONiC configuration files',
    author='Taoyu Li',
    author_email='taoyl@microsoft.com',
    url = 'https://github.com/Azure/sonic-buildimage',
    py_modules = [
        'portconfig',
        'minigraph',
        'openconfig_acl',
        'config_samples',
        'redis_bcc',
        'lazy_re',
    ],
    scripts = [
        'sonic-cfggen',
    ],
    install_requires = [
        'future',
        'ipaddr',
        'jinja2>=2.10',
        'lxml',
        'netaddr',
        'pyyaml',
        'pyangbind==0.6.0',
        'sonic-py-common',
    ],
    test_suite = 'setup.get_test_suite',
    data_files = [
        ('/usr/share/sonic/templates', glob.glob('data/*')),
    ],
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*',
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)

