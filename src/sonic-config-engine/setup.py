import glob

from setuptools import setup

from tests.common_utils import PY3x

dependencies = [
# Python 2 or 3 dependencies
        'future',
        'ipaddr',
        'lxml',
        'netaddr',
        'pyyaml',
        'sonic-py-common',
    ] + ([
# Python 3 dependencies
# pyangbind v0.8.1 pull down enum43 which causes 're' package to malfunction.
# Python3 has enum module and so pyangbind should be installed outside
# dependencies section of setuptools followed by uninstall of enum43
#        'pyangbind==0.8.1',
        'Jinja2>=2.10',
    ] if PY3x
    else [
# Python 2 dependencies
# Jinja2 v3.0.0+ dropped support for Python 2.7 and causes setuptools to
# malfunction on stretch slave docker.
        'Jinja2<3.0.0',
        'pyangbind==0.6.0',
    ])

setup(
    name = 'sonic-config-engine',
    version = '1.0',
    description = 'Utilities for generating SONiC configuration files',
    author = 'Taoyu Li',
    author_email = 'taoyl@microsoft.com',
    url = 'https://github.com/Azure/sonic-buildimage',
    py_modules = [
        'config_samples',
        'lazy_re',
        'minigraph',
        'openconfig_acl',
        'portconfig',
        'redis_bcc',
    ],
    scripts = [
        'sonic-cfggen',
    ],
    install_requires = dependencies,
    data_files = [
        ('/usr/share/sonic/templates', glob.glob('data/*')),
    ],
    setup_requires= [
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ],
    classifiers = [
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    keywords = 'SONiC sonic-cfggen config-engine PYTHON python'
)

