#! /usr/bin/python -tt

import nose

from rhuilib.util import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_repo import *
from rhuilib.rhui_testcase import *


class test_tcms_240397(RHUITestcase):
    def _setup(self):
        '''[TCMS#240397 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.Instances["RHUA"][0])

    def _test(self):
        '''[TCMS#240397 test] Create custom repos '''
        RHUIManagerRepo.add_custom_repo(self.rs.Instances["RHUA"][0], "custom-i386-x86_64", "", "custom/i386/x86_64", "1", "y")
        RHUIManagerRepo.add_custom_repo(self.rs.Instances["RHUA"][0], "custom-x86_64-x86_64", "", "custom/x86_64/x86_64", "1", "y")
        RHUIManagerRepo.add_custom_repo(self.rs.Instances["RHUA"][0], "custom-i386-i386", "", "custom/i386/i386", "1", "y")

    def _cleanup(self):
        '''[TCMS#240397 cleanup] Delete custom repos '''
        RHUIManagerRepo.delete_repo(self.rs.Instances["RHUA"][0], ["custom-i386-x86_64"])
        RHUIManagerRepo.delete_repo(self.rs.Instances["RHUA"][0], ["custom-x86_64-x86_64"])
        RHUIManagerRepo.delete_repo(self.rs.Instances["RHUA"][0], ["custom-i386-i386"])


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
