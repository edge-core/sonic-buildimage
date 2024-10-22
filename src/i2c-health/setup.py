from setuptools import setup

dependencies = [
    'natsort',
    'sonic_py_common',
    'docker'
]

setup(
    name='i2c-health',
    version='1.0',
    description='SONiC i2c health package',
    license='Apache 2.0',
    author='Edgecore SW Team',
    author_email='charlie_chen@edge-core.com',
    url='https://github.com/edge-core/sonic-buildimage/',
    maintainer='Mark Hsieh',
    maintainer_email='mark_hsieh@edge-core.com',
    install_requires=dependencies,
    packages=[
        'i2c_health_mgr',
        'tests'
    ],
    scripts=[
        'scripts/i2chealthd',
        'scripts/launch_i2c_service',
    ],
    setup_requires=[
        'pytest-runner'
    ],
    tests_require=[
        'pytest',
        'mock>=2.0.0'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: No Input/Output (Daemon)',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.7',
        'Topic :: System :: Hardware',
    ],
    keywords='SONiC sonic I2C i2c HEALTH health',
    test_suite='setup.get_test_suite'
)
