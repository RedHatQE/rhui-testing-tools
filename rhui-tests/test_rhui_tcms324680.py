#! /usr/bin/python -tt

import nose

from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_repo import *
from rhuilib.rhuimanager_entitlements import *


class test_tcms324680(RHUITestcase):
    ''' for more ditails see bz 957128
     try toupload fake rpms and signed rpm from a directory in cli mode
     fake rpm sould not be uploaded
     signed and unsigned rpm should be uploaded'''

    def _setup(self):
        """[TCMS#324680 setup] Do initial rhui-manager run"""
        RHUIManager.initial_run(self.rs.Instances["RHUA"][0])

        '''[TCMS#324680 setup] Create custom repo '''
        RHUIManagerRepo.add_custom_repo(self.rs.Instances["RHUA"][0], "repo324680")

        """[TCMS#324680 setup] Create fake rpm"""
        Expect.enter(self.rs.Instances["RHUA"][0], "touch /root/fake.rpm && echo SUCCESS")

        """[TCMS#324680 setup] Create rpm files"""
        self.rs.Instances["RHUA"][0].sftp.put("/usr/share/rhui-testing-tools/testing-data/custom-signed-rpm-1-0.1.fc17.noarch.rpm", "/root/custom-signed-rpm-1-0.1.fc17.noarch.rpm")
        self.rs.Instances["RHUA"][0].sftp.put("/usr/share/rhui-testing-tools/testing-data/custom-unsigned-rpm-1-0.1.fc17.noarch.rpm", "/root/custom-unsigned-rpm-1-0.1.fc17.noarch.rpm")

        '''[TCMS#324680 setup] Upload content to custom repo324680 in cli mode'''
        Expect.ping_pong(self.rs.Instances["RHUA"][0], "rhui-manager packages upload --repo_id repo324680 --packages /root && echo SUCCESS", "[^ ]SUCCESS", 10)

    def _test(self):
        '''[TCMS#324680 test] Check the packages list for repo324680'''
        nose.tools.assert_equal(RHUIManagerRepo.check_for_package(self.rs.Instances["RHUA"][0], "repo_xxx", ""), ["custom-signed-rpm-1-0.1.fc17.noarch.rpm", "custom-unsigned-rpm-1-0.1.fc17.noarch.rpm"])

    def _cleanup(self):
        '''[TCMS#324680 cleanup] Delete custom repo '''
        RHUIManagerRepo.delete_repo(self.rs.Instances["RHUA"][0], ["repo324680"])

        '''[TCMS#284279 cleanup] Remove fake rpm from RHUI '''
        Expect.ping_pong(self.rs.Instances["RHUA"][0], " rm -f /root/fake.rpm && echo SUCCESS", "[^ ]SUCCESS")


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
