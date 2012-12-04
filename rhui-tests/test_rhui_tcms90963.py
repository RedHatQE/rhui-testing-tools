#! /usr/bin/python -tt

import nose

from rhuilib.util import *
from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_repo import *


class test_tcms_90963(RHUITestcase):
    def _setup(self):
        '''[TCMS#90963 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.Instances["RHUA"][0])

        '''[TCMS#90963 setup] Create repo'''
        RHUIManagerRepo.add_custom_repo(self.rs.Instances["RHUA"][0], "repo1")

        '''[TCMS#90963 setup] Create testdir'''
        Expect.ping_pong(self.rs.Instances["RHUA"][0], "mkdir /root/test-tcms-90963 && echo SUCCESS", "[^ ]SUCCESS")

        '''[TCMS#90963 setup] Create repo'''
        self.rs.Instances["RHUA"][0].sftp.put("/usr/share/rhui-testing-tools/testing-data/custom-signed-rpm-1-0.1.fc17.noarch.rpm", "/root/test-tcms-90963/custom-signed-rpm-1-0.1.fc17.noarch.rpm")

        '''[TCMS#90963 setup] Upload directory with packages '''
        Expect.ping_pong(self.rs.Instances["RHUA"][0], "rhui-manager packages upload --repo_id repo1 --packages /root/test-tcms-90963 | fgrep 'custom-signed-rpm' && echo SUCCESS", "[^ ]SUCCESS", 10)

    def _test(self):
        '''[TCMS#90963 test] Check rhui-manager list output '''
        Expect.ping_pong(self.rs.Instances["RHUA"][0], "rhui-manager packages list --repo_id repo1 | fgrep 'custom-signed-rpm' && echo SUCCESS", "[^ ]SUCCESS", 10)

    def _cleanup(self):
        '''[TCMS#90963 cleanup] Remove testdir'''
        Expect.ping_pong(self.rs.Instances["RHUA"][0], "rm -rf /root/test-tcms-90963 && echo SUCCESS", "[^ ]SUCCESS")

        '''[TCMS#90963 cleanup] Remove repo '''
        RHUIManagerRepo.delete_repo(self.rs.Instances["RHUA"][0], ["repo1"])


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
