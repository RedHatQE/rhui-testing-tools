#! /usr/bin/python -tt

import nose

from rhuilib.util import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_repo import *
from rhuilib.rhui_testcase import *


class test_bug_696940(RHUITestcase):
    def _setup(self):
        '''[Bug#696940 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.RHUA)

    def _test(self):
        '''[Bug#696940 test] Create custom repo '''
        RHUIManagerRepo.add_custom_repo(self.rs.RHUA, "custom_repo1", "protected repo1", "/protected/x86_64/os", "1", "y", "/protected/$basearch/os")

    def _cleanup(self):
        '''[Bug#696940 cleanup] Delete custom repo '''
        RHUIManagerRepo.delete_repo(self.rs.RHUA, ["protected repo1"])


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
