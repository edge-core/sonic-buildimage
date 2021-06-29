from setuptools import setup, find_packages

# read me
with open('README.rst') as readme_file:
    readme = readme_file.read()

setup(
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
    description="Package contains YANG models for sonic.",
    license="GNU General Public License v3",
    long_description=readme + '\n\n',
    install_requires = [
    ],
    tests_require = [
        'pytest',
        'ijson==2.6.1'
    ],
    setup_requires = [
        'pytest-runner',
        'wheel'
    ],
    include_package_data=True,
    keywords='sonic-yang-models',
    name='sonic-yang-models',
    py_modules=[],
    packages=find_packages(),
    version='1.0',
    data_files=[
        ('yang-models', ['./yang-models/sonic-acl.yang',
                         './yang-models/sonic-bgp-common.yang',
                         './yang-models/sonic-bgp-global.yang',
                         './yang-models/sonic-bgp-neighbor.yang',
                         './yang-models/sonic-bgp-peergroup.yang',
                         './yang-models/sonic-breakout_cfg.yang',
                         './yang-models/sonic-copp.yang',
                         './yang-models/sonic-crm.yang',
                         './yang-models/sonic-device_metadata.yang',
                         './yang-models/sonic-device_neighbor.yang',
                         './yang-models/sonic-extension.yang',
                         './yang-models/sonic-flex_counter.yang',
                         './yang-models/sonic-interface.yang',
                         './yang-models/sonic-loopback-interface.yang',
                         './yang-models/sonic-mgmt_interface.yang',
                         './yang-models/sonic-mgmt_port.yang',
                         './yang-models/sonic-mgmt_vrf.yang',
                         './yang-models/sonic-ntp.yang',
                         './yang-models/sonic-nat.yang',
                         './yang-models/sonic-port.yang',
                         './yang-models/sonic-portchannel.yang',
                         './yang-models/sonic-route-common.yang',
                         './yang-models/sonic-route-map.yang',
                         './yang-models/sonic-routing-policy-sets.yang',
                         './yang-models/sonic-system-aaa.yang',
                         './yang-models/sonic-system-tacacs.yang',
                         './yang-models/sonic-types.yang',
                         './yang-models/sonic-versions.yang',
                         './yang-models/sonic-vlan.yang',
                         './yang-models/sonic-vrf.yang',
                         './yang-models/sonic_yang_tree']),
    ],
    zip_safe=False,
)
