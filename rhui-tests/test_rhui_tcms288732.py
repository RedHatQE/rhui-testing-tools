#! /usr/bin/python -tt

import nose
import time

from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_repo import *
from rhuilib.rhuimanager_sync import *
from rhuilib.rhuimanager_entitlements import *


class test_tcms_288732(RHUITestcase, RHUI_has_RH_cert):
    def _setup(self):
        '''[TCMS#288732 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.Instances["RHUA"][0])

        '''[TCMS#288732 setup] Upload RH content certificate '''
        RHUIManagerEntitlements.upload_content_cert(self.rs.Instances["RHUA"][0], self.cert)

        '''[TCMS#288732 setup] Add rh repo '''
        RHUIManagerRepo.add_rh_repo_by_repo(self.rs.Instances["RHUA"][0], ["Red Hat Enterprise Linux 5 Server Beta from RHUI \(Debug RPMs\) \(5Server-x86_64\)"])

        '''[TCMS#288732 setup] Sync rh repo '''
        RHUIManagerSync.sync_repo(self.rs.Instances["RHUA"][0], ["Red Hat Enterprise Linux 5 Server Beta from RHUI \(Debug RPMs\) \(5Server-x86_64\)"])

    def _test(self):
        '''[TCMS#288732 test] Check the status of the repo'''
        Expect.ping_pong(self.rs.Instances["RHUA"][0], "rhui-manager status | grep \"Red Hat Enterprise Linux 5 Server Beta from RHUI (Debug RPMs) (5Server-x86_64)\" | grep \"SYNCING\" && echo SUCCESS", "[^ ]SUCCESS", 20)

    def _cleanup(self):
        '''[TCMS#288732 cleanup] Wait untill repo is synced '''
        reposync = ["In Progress", "", ""]
        while reposync[0] == "In Progress":
            time.sleep(10)
            reposync = RHUIManagerSync.get_repo_status(self.rs.Instances["RHUA"][0], "Red Hat Enterprise Linux 5 Server Beta from RHUI \(Debug RPMs\) \(5Server-x86_64\)")
        nose.tools.assert_equal(reposync[2], "Success")

        '''[TCMS#288732 cleanup] Delete RH repo '''
        RHUIManagerRepo.delete_repo(self.rs.Instances["RHUA"][0], ["Red Hat Enterprise Linux 5 Server Beta from RHUI \(Debug RPMs\) \(5Server-x86_64\)"])

        '''[TCMS#288732 cleanup] Remove RH certs from RHUI '''
        RHUIManager.remove_rh_certs(self.rs.Instances["RHUA"][0])


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])

