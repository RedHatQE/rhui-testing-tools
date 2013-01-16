#!/usr/bin/env python

from setuptools import setup
import glob

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
             ('share/rhui-testing-tools/cfn', glob.glob('cfn/*.json')),
             ('share/rhui-testing-tools/testing-data', glob.glob('testing-data/*.key') + glob.glob('testing-data/*.rpm')),
             ('share/rhui-testing-tools/rhui-tests', glob.glob('rhui-tests/*.py')),
             ('share/rhui-testing-tools/testplans/tcms6606', glob.glob('testplans/tcms6606/*.py')),
             ('share/rhui-testing-tools/testplans/tcms6610', glob.glob('testplans/tcms6610/*.py')),
             ('share/rhui-testing-tools/testplans/tcms6870', glob.glob('testplans/tcms6870/*.py')),
             ('share/rhui-testing-tools/testplans/bugs', glob.glob('testplans/bugs/*.py')),
             ('/etc', ['etc/rhui-testing.cfg'])
    ],
    classifiers=[
            'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
            'Programming Language :: Python',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Operating System :: POSIX',
            'Intended Audience :: Developers',
            'Development Status :: 4 - Beta'
    ],
    scripts=glob.glob('scripts/*.py') + glob.glob('scripts/*.sh')
)
