#! /usr/bin/python -tt

import nose

from rhuilib.util import *
from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_repo import *
from rhuilib.rhuimanager_entitlements import *


class test_tcms_90966(RHUITestcase, RHUI_has_RH_cert):
    def _setup(self):
        '''[TCMS#90966 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.RHUA[0])

        '''[TCMS#90966 setup] Create custom repo'''
        RHUIManagerRepo.add_custom_repo(self.rs.RHUA[0], "repo1")

        '''[TCMS#90966 setup] Upload RH content certificate '''
        RHUIManagerEntitlements.upload_content_cert(self.rs.RHUA[0], self.cert)

        '''[TCMS#90966 setup] Add rh repo '''
        RHUIManagerRepo.add_rh_repo_by_repo(self.rs.RHUA[0], ["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])

    def _test(self):
        '''[TCMS#90966 test] Check rhui-manager repo list output '''
        Expect.ping_pong(self.rs.RHUA[0], "rhui-manager repo list | fgrep '^repo1' && echo SUCCESS", "[^ ]SUCCESS", 10)
        Expect.ping_pong(self.rs.RHUA[0], "rhui-manager repo list | fgrep 'Red Hat Update Infrastructure 2' && echo SUCCESS", "[^ ]SUCCESS", 10)

    def _cleanup(self):
        '''[TCMS#90966 cleanup] Remove repos '''
        RHUIManagerRepo.delete_repo(self.rs.RHUA[0], ["repo1", "Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
