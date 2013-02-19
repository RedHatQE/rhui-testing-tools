#! /usr/bin/python -tt

import nose

from rhuilib.util import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_repo import *
from rhuilib.rhui_testcase import *


class test_tcms_240428(RHUITestcase):
    def _setup(self):
        '''[TCMS#240428 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.Instances["RHUA"][0])

    def _test(self):
        '''[TCMS#240428 test] Create custom repos '''
        RHUIManagerRepo.add_custom_repo(self.rs.Instances["RHUA"][0], "prefix", "", "prefix", "1", "y")
        RHUIManagerRepo.add_custom_repo(self.rs.Instances["RHUA"][0], "prefix-1", "", "prefix-1/x86_64", "1", "y")

    def _cleanup(self):
        '''[TCMS#240428 cleanup] Delete custom repos '''
        RHUIManagerRepo.delete_repo(self.rs.Instances["RHUA"][0], ["prefix"])
        RHUIManagerRepo.delete_repo(self.rs.Instances["RHUA"][0], ["prefix-1"])


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
