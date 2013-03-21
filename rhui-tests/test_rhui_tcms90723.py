#! /usr/bin/python -tt

import nose
import re

from rhuilib.util import *
from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_repo import *
from rhuilib.pulp_admin import *

class test_rhui_tcms90723(RHUITestcase):
    def _setup(self):
        '''[TCMS#90723 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.Instances["RHUA"][0])

        '''[TCMS#90723 setup] Create custom repo'''
        RHUIManagerRepo.add_custom_repo(self.rs.Instances["RHUA"][0], "repo1")

    def _test(self):
        '''[TCMS#90723 test] Check the repo list screen'''
        nose.tools.assert_equal(RHUIManagerRepo.list(self.rs.Instances["RHUA"][0]), ["repo1"])

        '''[TCMS#90723 test] Check pulp-admin and rhui info are the same'''
        res = PulpAdmin.repo_list(self.rs.Instances["RHUA"][0])[0].name
        nose.tools.assert_equal([res], RHUIManagerRepo.list(self.rs.Instances["RHUA"][0]))

    def _cleanup(self):
        '''[TCMS#90723 cleanup] Remove a repo'''
        RHUIManagerRepo.delete_repo(self.rs.Instances["RHUA"][0], ["repo1"])
        
if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
