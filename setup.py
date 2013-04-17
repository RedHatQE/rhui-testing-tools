#!/usr/bin/env python

from setuptools import setup
import glob
import os

def walk_topdirs(dest, topdirs):
    # dest: where to store the walked files e.g. 'share/rhui-testing-tools'
    # topdirs: what to walk e.g. ['testing-data', 'rhui-tests', ...]
    datafiles = []
    for topdir in topdirs:
        for dirname, dirnames, filenames in os.walk(topdir):
            datafiles.append(
                (
                    os.path.join(dest, dirname),
                    map(lambda x: os.path.join(dirname, x), filenames)
                )
            )
    return datafiles

setup(name='rhuilib',
    version='0.1.1',
    description='RHUI Testing library',
    author='Vitaly Kuznetsov',
    author_email='vitty@redhat.com',
    url='https://github.com/RedHatQE/rhui-testing-tools',
    license="GPLv3+",
    packages=[
        'splicelib',
        'rhuilib'
        ],
    data_files=\
        walk_topdirs('share/rhui-testing-tools', ['testing-data', 'rhui-tests', 'splice-tests', 'testplans']) + \
        walk_topdirs('/', ['lib/systemd']) + \
        walk_topdirs('/', ['etc']),
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
