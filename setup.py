#!/usr/bin/env python

from setuptools import setup

setup(name='rhuilib',
    version='0.1',
    description='RHUI Testing library',
    author='Vitaly Kuznetsov',
    author_email='vitty@redhat.com',
    url='https://github.com/RedHatQE/rhui-testing-tools',
    license="GPLv3+",
    packages=[
        'rhuilib'
        ],
    data_files=[
             ('share/rhui-testing-tools/cfn', ['cfn/rhui_with_1cds_1cli.json']),
             ('share/rhui-testing-tools/testing-data', ['testing-data/private.key', 'testing-data/public.key']),
             ('share/rhui-testing-tools/rhui-tests', ['rhui-tests/test-rhui-workflow-simple.py', 'rhui-tests/test-rhui-bug860117.py', 'rhui-tests/test-rhui-cds-management-screen.py']),
    ],
    classifiers=[
            'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
            'Programming Language :: Python',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Operating System :: POSIX',
            'Intended Audience :: Developers',
            'Development Status :: 4 - Beta'
    ],
    scripts=[
            'scripts/create-cf-stack.py',
            'scripts/remote-rhui-installer.sh',
            'scripts/rhui-installer.py'
    ]
)
