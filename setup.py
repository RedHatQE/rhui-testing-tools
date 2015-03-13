#!/usr/bin/env python

from setuptools import setup
import glob
import os

datafiles = []
for topdir in ['testing-data', 'rhui-tests', 'testplans']:
    for dirname, dirnames, filenames in os.walk(topdir):
        datafiles.append(('share/rhui-testing-tools/' + dirname, map(lambda x: dirname + "/" + x, filenames)))

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
    data_files=[('/etc', ['etc/rhui_auto.yaml'])] + datafiles,
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
