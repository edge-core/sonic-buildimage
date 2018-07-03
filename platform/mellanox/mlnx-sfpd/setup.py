from setuptools import setup

setup(
    name='mlnx-sfpd',
    version='1.0',
    description='SFP event mmonitoring daemon for SONiC on mellanox platform',
    license='Apache 2.0',
    author='SONiC Community',
    url='https://github.com/Azure/sonic-buildimage/',
    maintainer='Kebo Liu',
    maintainer_email='kebol@mellanox.com',
    scripts=[
        'scripts/mlnx-sfpd',
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
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Hardware',
    ],
    keywords='sonic SONiC SFP sfp MELLANOX mellanox daemon SFPD sfpd',
)
