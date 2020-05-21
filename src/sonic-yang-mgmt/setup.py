#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages
from setuptools.command.build_py import build_py
from os import system, environ
from sys import exit
import pytest

# find path of pkgs from os environment vars
prefix = '../../'; debs = environ["IMAGE_DISTRO_DEBS_PATH"]
wheels = environ["PYTHON_WHEELS_PATH"]
wheels_path = '{}/{}'.format(prefix, wheels)
deps_path = '{}/{}'.format(prefix, debs)
# dependencies
libyang = '{}/{}'.format(deps_path, environ["LIBYANG"])
libyangCpp = '{}/{}'.format(deps_path, environ["LIBYANG_CPP"])
libyangPy2 = '{}/{}'.format(deps_path, environ["LIBYANG_PY2"])
libyangPy3 = '{}/{}'.format(deps_path, environ["LIBYANG_PY3"])
sonicYangModels = '{}/{}'.format(wheels_path, environ["SONIC_YANG_MODELS_PY3"])

# important reuirements parameters
build_requirements = [libyang, libyangCpp, libyangPy2, libyangPy3, sonicYangModels,]

setup_requirements = ['pytest-runner']

test_requirements = ['pytest>=3']

# read me
with open('README.rst') as readme_file:
    readme = readme_file.read()

# class for prerequisites to build this package
class pkgBuild(build_py):
    """Custom Build PLY"""

    def run (self):
        #  install libyang and sonic_yang_models
        for req in build_requirements:
            if '.deb' in req:
                pkg_install_cmd = "sudo dpkg -i {}".format(req)
                if (system(pkg_install_cmd)):
                    print("{} installation failed".format(req))
                    exit(1)
                else:
                    print("{} installed".format(req))
            elif '.whl' in req:
                pkg_install_cmd = "pip3 install {}".format(req)
                if (system(pkg_install_cmd)):
                    print("{} installation failed".format(req))
                    exit(1)
                else:
                    print("{} installed".format(req))

        # run pytest for libyang python APIs
        self.pytest_args = []
        errno = pytest.main(self.pytest_args)
        if (errno):
            exit(errno)

        # Continue usual build steps
        build_py.run(self)

setup(
    cmdclass={
        'build_py': pkgBuild,
    },
    author="lnos-coders",
    author_email='lnos-coders@linkedin.com',
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Package contains Python Library for YANG for sonic.",
    tests_require = test_requirements,
    license="GNU General Public License v3",
    long_description=readme + '\n\n',
    include_package_data=True,
    keywords='sonic_yang_mgmt',
    name='sonic_yang_mgmt',
    py_modules=['sonic_yang', 'sonic_yang_ext'],
    packages=find_packages(),
    setup_requires=setup_requirements,
    version='1.0',
    zip_safe=False,
)
