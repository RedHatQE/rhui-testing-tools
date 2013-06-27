#! /usr/bin/python -tt

import nose
import re

from rhuilib.util import *
from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_repo import *
from rhuilib.pulp_admin import *

class test_rhui_tcms90728(RHUITestcase):
    def _setup(self):
        '''[TCMS#90728 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.Instances["RHUA"][0])

        '''[TCMS#90728 setup] Create repos'''
        RHUIManagerRepo.add_custom_repo(self.rs.Instances["RHUA"][0], "repo1")
        RHUIManagerRepo.add_custom_repo(self.rs.Instances["RHUA"][0], "repo2")
        RHUIManagerRepo.add_rh_repo_by_repo(self.rs.Instances["RHUA"][0], ["Red Hat Enterprise Linux 6 Server - Optional Beta from RHUI\(Debug RPMs\) \(6Server-i386\)"])
        
        '''[TCMS#90728 setup] Sync RH repo '''
        self._sync_repo(["Red Hat Enterprise Linux 6 Server - Optional Beta from RHUI\(Debug RPMs\) \(6Server-i386\)"])
        
        '''[TCMS#90728 setup] Upload content'''
        self.rs.Instances["RHUA"][0].sftp.put("/usr/share/rhui-testing-tools/testing-data/custom-signed-rpm-1-0.1.fc17.noarch.rpm", "/root/custom-signed-rpm-1-0.1.fc17.noarch.rpm")
        self.rs.Instances["RHUA"][0].sftp.put("/usr/share/rhui-testing-tools/testing-data/custom-unsigned-rpm-1-0.1.fc17.noarch.rpm", "/root/custom-unsigned-rpm-1-0.1.fc17.noarch.rpm")
        RHUIManagerRepo.upload_content(self.rs.Instances["RHUA"][0], ["repo1"], "/root")

    def _test(self):
        '''[TCMS#90728 test] Check the packages list'''
        nose.tools.assert_equal(RHUIManagerRepo.check_for_package(self.rs.Instances["RHUA"][0], "repo1", ""), ["custom-signed-rpm-1-0.1.fc17.noarch.rpm", "custom-unsigned-rpm-1-0.1.fc17.noarch.rpm"])
        nose.tools.assert_equal(RHUIManagerRepo.check_for_package(self.rs.Instances["RHUA"][0], "repo1", "custom-unsigned"), ["custom-unsigned-rpm-1-0.1.fc17.noarch.rpm"])
        nose.tools.assert_equal(RHUIManagerRepo.check_for_package(self.rs.Instances["RHUA"][0], "repo1", "test"), [])
        nose.tools.assert_equal(RHUIManagerRepo.check_for_package(self.rs.Instances["RHUA"][0], "repo2", ""), [])
        nose.tools.assert_equal(RHUIManagerRepo.check_for_package(self.rs.Instances["RHUA"][0], "Red Hat Enterprise Linux 6 Server - Optional Beta from RHUI\(Debug RPMs\) \(6Server-i386\)", ""), ["Package Count: 124"])

    def _cleanup(self):
        '''[TCMS#90728 cleanup] Remove a repo'''
        RHUIManagerRepo.delete_repo(self.rs.Instances["RHUA"][0], ["repo1"])
        RHUIManagerRepo.delete_repo(self.rs.Instances["RHUA"][0], ["repo2"])
        RHUIManagerRepo.delete_repo(self.rs.Instances["RHUA"][0], ["Red Hat Enterprise Linux 6 Server - Optional Beta from RHUI\(Debug RPMs\) \(6Server-i386\)"])
        
if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
