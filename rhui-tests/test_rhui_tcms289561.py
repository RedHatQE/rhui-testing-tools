#! /usr/bin/python -tt

from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_repo import *
from rhuilib.rhuimanager_entitlements import *


class test_tcms_289561(RHUITestcase, RHUI_has_RH_cert):
    def _setup(self):
        '''[TCMS#289561 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.Instances["RHUA"][0])

        '''[TCMS#289561 setup] Upload RH content certificate '''
        RHUIManagerEntitlements.upload_content_cert(self.rs.Instances["RHUA"][0], self.cert)

        '''[TCMS#289561 setup] Add rh repo '''
        RHUIManagerRepo.add_rh_repo_by_repo(self.rs.Instances["RHUA"][0], ["Red Hat Enterprise Linux 5 Server Beta from RHUI \(Debug RPMs\) \(5Server-x86_64\)"])

    def _test(self):
        '''[TCMS#289561 test] Check the status of the repo'''
        Expect.ping_pong(self.rs.Instances["RHUA"][0], "rhui-manager status | grep \"Red Hat Enterprise Linux 5 Server Beta from RHUI (Debug RPMs) (5Server-x86_64)\" | grep \"NEVER\" && echo SUCCESS", "[^ ]SUCCESS", 20)

    def _cleanup(self):
        '''[TCMS#289561 cleanup] Delete RH repo '''
        RHUIManagerRepo.delete_repo(self.rs.Instances["RHUA"][0], ["Red Hat Enterprise Linux 5 Server Beta from RHUI \(Debug RPMs\) \(5Server-x86_64\)"])

        '''[TCMS#289561 cleanup] Remove RH certs from RHUI '''
        RHUIManager.remove_rh_certs(self.rs.Instances["RHUA"][0])


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
