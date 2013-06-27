#! /usr/bin/python -tt

import nose
import re

from rhuilib.util import *
from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_repo import *
from rhuilib.pulp_admin import *

class test_rhui_tcms90727(RHUITestcase):
    def _setup(self):
        '''[TCMS#90727 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.Instances["RHUA"][0])

        '''[TCMS#90727 setup] Create custom repo'''
        RHUIManagerRepo.add_custom_repo(self.rs.Instances["RHUA"][0], "repo1")
        
        """[TCMS#90727 setup] Create rpm and non-rpm files"""
        Expect.enter(self.rs.Instances["RHUA"][0], "touch /root/test && echo SUCCESS")
        self.rs.Instances["RHUA"][0].sftp.put("/usr/share/rhui-testing-tools/testing-data/custom-signed-rpm-1-0.1.fc17.noarch.rpm", "/root/custom-signed-rpm-1-0.1.fc17.noarch.rpm")
        self.rs.Instances["RHUA"][0].sftp.put("/usr/share/rhui-testing-tools/testing-data/custom-unsigned-rpm-1-0.1.fc17.noarch.rpm", "/root/custom-unsigned-rpm-1-0.1.fc17.noarch.rpm")
        
        '''[TCMS#90727 setup] Upload content'''
        RHUIManagerRepo.upload_content(self.rs.Instances["RHUA"][0], ["repo1"], "/root")

    def _test(self):
        '''[TCMS#90727 test] Check the packages list'''
        nose.tools.assert_equal(RHUIManagerRepo.check_for_package(self.rs.Instances["RHUA"][0], "repo1", ""), ["custom-signed-rpm-1-0.1.fc17.noarch.rpm", "custom-unsigned-rpm-1-0.1.fc17.noarch.rpm"])

    def _cleanup(self):
        '''[TCMS#90727 cleanup] Remove a repo'''
        RHUIManagerRepo.delete_repo(self.rs.Instances["RHUA"][0], ["repo1"])
        
if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '--with-outputsave'])
