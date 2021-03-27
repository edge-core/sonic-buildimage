import glob
import sys

from setuptools import setup

# Common dependencies for Python 2 and 3
dependencies = [
    'bitarray==1.5.3',
    'ipaddress==1.0.23',
    'lxml==4.6.3',
    'netaddr==0.8.0',
    'pyyaml==5.4.1',
    'sonic-py-common',
]

if sys.version_info.major == 3:
    # Python 3-only dependencies
    dependencies += [
        # pyangbind v0.8.1 pull down enum43 which causes 're' package to malfunction.
        # Python3 has enum module and so pyangbind should be installed outside
        # dependencies section of setuptools followed by uninstall of enum43
        # 'pyangbind==0.8.1',
        'Jinja2>=2.10'
    ]
else:
    # Python 2-only dependencies
    dependencies += [
        # Jinja2 v3.0.0+ dropped support for Python 2.7 and causes setuptools to
        # malfunction on stretch slave docker.
        'future',
        'Jinja2<3.0.0',
        'pyangbind==0.6.0',
        'zipp==1.2.0',  # importlib-resources needs zipp and seems to have a bug where it will try to install too new of a version for Python 2
        'importlib-resources==3.3.1'  # importlib-resources v4.0.0 was released 2020-12-23 and drops support for Python 2
    ]


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
        'wheel'
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
