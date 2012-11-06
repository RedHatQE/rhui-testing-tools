#! /usr/bin/python -tt

import argparse
import nose

from rhuilib.util import *
from rhuilib.rhuisetup import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_repo import *


class test_bug_696940(object):
    def __init__(self):
        argparser = argparse.ArgumentParser(description='RHUI bug 696940')
        args = argparser.parse_args()
        self.rs = RHUIsetup()
        self.rs.setup_from_yamlfile()

    def __del__(self):
        self.rs.__del__()

    def test_01_initial_run(self):
        ''' Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.RHUA)

    def test_02_add_custom_repos(self):
        ''' Create custom repo '''
        RHUIManagerRepo.add_custom_repo(self.rs.RHUA, "custom_repo1", "protected repo1", "/protected/x86_64/os", "1", "y", "/protected/$basearch/os")

    def test_03_delete_custom_repo(self):
        ''' Delete custom repo '''
        RHUIManagerRepo.delete_repo(self.rs.RHUA, ["protected repo1"])


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
