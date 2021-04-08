from setuptools import setup

setup(
    name = 'sonic-host-services',
    version = '1.0',
    description = 'Python services which run in the SONiC host OS',
    license = 'Apache 2.0',
    author = 'SONiC Team',
    author_email = 'linuxnetdev@microsoft.com',
    url = 'https://github.com/Azure/sonic-buildimage',
    maintainer = 'Joe LeVeque',
    maintainer_email = 'jolevequ@microsoft.com',
    scripts = [
        'scripts/caclmgrd',
        'scripts/hostcfgd',
        'scripts/procdockerstatsd',
        'scripts/determine-reboot-cause',
        'scripts/process-reboot-cause',
    ],
    install_requires = [
        'Jinja2>=2.10',
        'sonic-py-common',
        'swsssdk>=2.0.1',
    ],
    setup_requires = [
        'pytest-runner',
        'wheel'
    ],
    tests_require = [
        'pytest',
        'sonic-py-common'
    ],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.7',
        'Topic :: System',
    ],
    keywords = 'sonic SONiC host services',
    test_suite = 'setup.get_test_suite'
)
