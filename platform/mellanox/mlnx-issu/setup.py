from setuptools import setup

setup(
    name='mlnx-issu',
    version='1.0',
    description='MLNX ISSU tool for SONiC on mellanox platform',
    author='SONiC Community',
    url='https://github.com/Azure/sonic-buildimage/',
    maintainer='Stepan Blyschak',
    maintainer_email='stepanb@mellanox.com',
    scripts=[
        'scripts/issu',
        'scripts/ffb',
    ]
)
