#! /usr/bin/python -tt

import nose

from rhuilib.util import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_repo import *
from rhuilib.rhui_testcase import *


class test_bug_696940(RHUITestcase):
    def __init__(self):
        RHUITestcase.__init__(self)
        '''[Bug#696940 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.RHUA)

    def test_bug_696940(self):
        '''[Bug#696940 test] Create custom repo '''
        RHUIManagerRepo.add_custom_repo(self.rs.RHUA, "custom_repo1", "protected repo1", "/protected/x86_64/os", "1", "y", "/protected/$basearch/os")

    def __del__(self):
        '''[Bug#696940 cleanup] Delete custom repo '''
        RHUIManagerRepo.delete_repo(self.rs.RHUA, ["protected repo1"])

        RHUITestcase.__del__()


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
