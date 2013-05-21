#! /usr/bin/python -tt

import nose

from rhuilib.util import *
from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_cds import *
from rhuilib.rhuimanager_repo import *
from rhuilib.rhuimanager_entitlements import *


class test_tcms_178463(RHUITestcase, RHUI_has_RH_cert):
    def _setup(self):
        '''[TCMS#178463 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.Instances["RHUA"][0])

        '''[TCMS#178463 setup] Add cds '''
        RHUIManagerCds.add_cds(self.rs.Instances["RHUA"][0], "Cluster1", self.rs.Instances["CDS"][0].private_hostname)

        '''[TCMS#178463 setup] Upload RH content certificate '''
        RHUIManagerEntitlements.upload_content_cert(self.rs.Instances["RHUA"][0], self.cert)

        '''[TCMS#178463 setup] Add rh repo '''
        RHUIManagerRepo.add_rh_repo_by_repo(self.rs.Instances["RHUA"][0], ["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])

        '''[TCMS#178463 setup] Associate repo with cluster '''
        RHUIManagerCds.associate_repo_cds(self.rs.Instances["RHUA"][0], "Cluster1", ["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])

    def _test(self):
        '''[TCMS#178463 test] Unassociate rh repo from cluster '''
        RHUIManagerCds.unassociate_repo_cds(self.rs.Instances["RHUA"][0], "Cluster1", ["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])

    def _cleanup(self):
        '''[TCMS#178463 cleanup] Remove cds '''
        RHUIManagerCds.delete_cds(self.rs.Instances["RHUA"][0], "Cluster1", [self.rs.Instances["CDS"][0].private_hostname])

        '''[TCMS#178463 cleanup] Delete RH repo '''
        RHUIManagerRepo.delete_repo(self.rs.Instances["RHUA"][0], ["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])

        '''[TCMS#178463 cleanup] Remove RH certificate from RHUI '''
        RHUIManager.remove_rh_certs(self.rs.Instances["RHUA"][0])

if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
