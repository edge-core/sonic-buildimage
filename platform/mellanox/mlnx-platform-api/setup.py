from setuptools import setup

setup(
    name='mlnx-platform-api',
    version='1.0',
    description='SONiC platform API implementation on Mellanox platform',
    license='Apache 2.0',
    author='SONiC Team',
    author_email='linuxnetdev@microsoft.com',
    url='https://github.com/Azure/sonic-buildimage',
    maintainer='Kevin Wang',
    maintainer_email='kevinw@mellanox.com',
    packages=[
        'sonic_platform',
        'tests'
    ],
    setup_requires= [
        'pytest-runner'
    ],
    tests_require = [
        'pytest',
        'mock>=2.0.0'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities',
    ],
    keywords='sonic SONiC platform PLATFORM',
    test_suite='setup.get_test_suite'
)

