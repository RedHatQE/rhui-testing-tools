#! /usr/bin/python -tt

import nose

from rhuilib.util import *
from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_repo import *


class test_tcms_90962(RHUITestcase, RHUI_has_two_CDSes):
    def _setup(self):
        '''[TCMS#90962 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.RHUA[0])

        '''[TCMS#90962 setup] Create repo'''
        RHUIManagerRepo.add_custom_repo(self.rs.RHUA[0], "repo1")

        '''[TCMS#90962 setup] Create testdir'''
        Expect.ping_pong(self.rs.RHUA[0], "mkdir /root/test-tcms-90962 && echo SUCCESS", "[^ ]SUCCESS")

        '''[TCMS#90962 setup] Create repo'''
        self.rs.RHUA[0].sftp.put("/usr/share/rhui-testing-tools/testing-data/custom-signed-rpm-1-0.1.fc17.noarch.rpm", "/root/test-tcms-90962/custom-signed-rpm-1-0.1.fc17.noarch.rpm")
        Expect.ping_pong(self.rs.RHUA[0], "head -c 1024000 /dev/urandom > /root/test-tcms-90962/pkg.deb && echo SUCCESS", "[^ ]SUCCESS", 10)

    def _test(self):
        '''[TCMS#90962 test] Uploading directory with packages, expecting to see only rpm file '''
        Expect.ping_pong(self.rs.RHUA[0], "rhui-manager packages upload --repo_id repo1 --packages /root/test-tcms-90962 | fgrep 'custom-signed-rpm' && echo SUCCESS", "[^ ]SUCCESS", 10)
        Expect.ping_pong(self.rs.RHUA[0], "rhui-manager packages upload --repo_id repo1 --packages /root/test-tcms-90962 | fgrep '.deb' || echo SUCCESS", "[^ ]SUCCESS", 10)

        '''[TCMS#90962 test] Additional check '''
        Expect.ping_pong(self.rs.RHUA[0], "find /var/lib/pulp/ -name '*.deb' | grep deb || echo SUCCESS", "[^ ]SUCCESS", 10)

    def _cleanup(self):
        '''[TCMS#90962 cleanup] Remove testdir'''
        Expect.ping_pong(self.rs.RHUA[0], "rm -rf /root/test-tcms-90962 && echo SUCCESS", "[^ ]SUCCESS")

        '''[TCMS#90962 cleanup] Remove repo '''
        RHUIManagerRepo.delete_repo(self.rs.RHUA[0], ["repo1"])


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
