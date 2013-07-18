#! /usr/bin/python -tt

import nose
import re

from rhuilib.util import *
from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_repo import *
from rhuilib.pulp_admin import *

class test_rhui_tcms90726(RHUITestcase):
    def _setup(self):
        '''[TCMS#90726 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.Instances["RHUA"][0])
        
        '''[TCMS#90726 setup] Upload RH content certificate'''
        RHUIManagerEntitlements.upload_content_cert(self.rs.Instances["RHUA"][0], self.cert)

        '''[TCMS#90726 setup] Create repos'''
        RHUIManagerRepo.add_custom_repo(self.rs.Instances["RHUA"][0], "repo1", "repo1", "repo1", "1", "n", "", "n")
        RHUIManagerRepo.add_rh_repo_by_repo(self.rs.Instances["RHUA"][0], ["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])

    def _test(self):
        '''[TCMS#90726 test] Check the repo info'''
        nose.tools.assert_equal(RHUIManagerRepo.info(self.rs.Instances["RHUA"][0], ["repo1", "Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"]),["Name:", "repo1", "Type:", "Custom", "Relative Path:", "repo1", "GPG Check:", "No", "Package Count:", "0", "Name:", "Red Hat Update Infrastructure 2 (RPMs) (6Server-x86_64)", "Type:", "Red Hat", "Relative Path:", "rh_repo", "Package Count:", "rh_repo", "Last Sync:", "rh_repo", "Next Sync:", "rh_repo"])

    def _cleanup(self):
        '''[TCMS#90726 cleanup] Remove repos'''
        RHUIManagerRepo.delete_repo(self.rs.Instances["RHUA"][0], ["repo1"])
        RHUIManagerRepo.delete_repo(self.rs.Instances["RHUA"][0], ["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])
        
        '''[TCMS#90726 cleanup] Remove RH certificate from RHUI'''
        RHUIManager.remove_rh_certs(self.rs.Instances["RHUA"][0])
        
if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
