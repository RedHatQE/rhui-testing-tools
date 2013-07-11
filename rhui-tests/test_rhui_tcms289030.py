#! /usr/bin/python -tt

import nose
import re

from rhuilib.util import *
from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_repo import *
from rhuilib.rhuimanager_entitlements import *
from rhuilib.pulp_admin import *

class test_rhui_tcms289030(RHUITestcase, RHUI_has_RH_cert):
    def _setup(self):
        '''[TCMS#289030 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.Instances["RHUA"][0])

        '''[TCMS#289030 setup] Upload RH content certificate '''
        RHUIManagerEntitlements.upload_content_cert(self.rs.Instances["RHUA"][0], self.cert)

        '''[TCMS#289030 setup] Create custom repos'''
        RHUIManagerRepo.add_custom_repo(self.rs.Instances["RHUA"][0], "repo1")
        RHUIManagerRepo.add_custom_repo(self.rs.Instances["RHUA"][0], "repo2")
        RHUIManagerRepo.add_custom_repo(self.rs.Instances["RHUA"][0], "repo3")
        
        '''[TCMS#289030 setup] Create RH repos'''
        RHUIManagerRepo.add_rh_repo_by_repo(self.rs.Instances["RHUA"][0], ["Red Hat Enterprise Linux 6 Server - Supplementary from RHUI \(Source RPMs\) \(6Server-i386\)"])
        RHUIManagerRepo.add_rh_repo_by_repo(self.rs.Instances["RHUA"][0], ["Red Hat Enterprise Linux 6 Server - Supplementary from RHUI \(Source RPMs\) \(6Server-x86_64\)"]) 

        '''[TCMS#289030 setup] Remove repos'''
        RHUIManagerRepo.delete_repo(self.rs.Instances["RHUA"][0], ["repo2"])
        RHUIManagerRepo.delete_repo(self.rs.Instances["RHUA"][0], ["Red Hat Enterprise Linux 6 Server - Supplementary from RHUI \(Source RPMs\) \(6Server-i386\)"])
        
    def _test(self):
        '''[TCMS#289030 test] Check the repo list screen'''
        nose.tools.assert_equal(RHUIManagerRepo.list(self.rs.Instances["RHUA"][0]), ["repo1", "repo3", "Red Hat Enterprise Linux 6 Server - Supplementary from RHUI (Source RPMs) (6Server-x86_64)"])

    def _cleanup(self):
        '''[TCMS#289030 cleanup] Remove remaining repos'''
        RHUIManagerRepo.delete_repo(self.rs.Instances["RHUA"][0], ["repo1"])
        RHUIManagerRepo.delete_repo(self.rs.Instances["RHUA"][0], ["repo3"])
        RHUIManagerRepo.delete_repo(self.rs.Instances["RHUA"][0], ["Red Hat Enterprise Linux 6 Server - Supplementary from RHUI \(Source RPMs\) \(6Server-x86_64\)"])
        
        '''[TCMS#289030 cleanup] Remove RH certificate from RHUI'''
        RHUIManager.remove_rh_certs(self.rs.Instances["RHUA"][0])
        
if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
