#! /usr/bin/python -tt
import nose

from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_repo import *
from rhuilib.rhuimanager_sync import *
from rhuilib.rhuimanager_cds import *
from rhuilib.rhuimanager_entitlements import *


class test_rhui_tcms267489(RHUITestcase, RHUI_has_RH_cert):
    def _setup(self):
        '''[TCMS#267489 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.Instances["RHUA"][0])

        '''[TCMS#267489 setup] Add cds '''
        RHUIManagerCds.add_cds(self.rs.Instances["RHUA"][0], "Cluster1", self.rs.Instances["CDS"][0].private_hostname)

        '''[TCMS#267489 setup] Upload RH content certificate '''
        RHUIManagerEntitlements.upload_content_cert(self.rs.Instances["RHUA"][0], self.cert)

        '''[TCMS#267489 setup] Add rh repo '''
        RHUIManagerRepo.add_rh_repo_by_repo(self.rs.Instances["RHUA"][0], ["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])

        '''[TCMS#267489 setup] Sync RH repo '''
        self._sync_repo(["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])

        '''[TCMS#267489 setup] Sync cds '''
        self._sync_cds([self.rs.Instances["CDS"][0].private_hostname])

        '''[TCMS#267489 setup] Delete RH repo '''
        RHUIManagerRepo.delete_repo(self.rs.Instances["RHUA"][0], ["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])

        '''[TCMS#267489 setup] Remove cds '''
        RHUIManagerCds.delete_cds(self.rs.Instances["RHUA"][0], "Cluster1", [self.rs.Instances["CDS"][0].private_hostname])

        '''[TCMS#267489 setup] Add rh repo '''
        RHUIManagerRepo.add_rh_repo_by_repo(self.rs.Instances["RHUA"][0], ["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])

        '''[TCMS#267489 setup] Add cds '''
        RHUIManagerCds.add_cds(self.rs.Instances["RHUA"][0], "Cluster1", self.rs.Instances["CDS"][0].private_hostname)

    def _test(self):
        '''[TCMS#267489 test] Check repo sync status '''
        reposync = RHUIManagerSync.get_repo_status(self.rs.Instances["RHUA"][0], "Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)")
        nose.tools.assert_equal(reposync[2], "Never")

        '''[TCMS#267489 test] Check cds sync status '''
        cdssync = RHUIManagerSync.get_cds_status(self.rs.Instances["RHUA"][0], self.rs.Instances["CDS"][0].private_hostname)
        nose.tools.assert_equal(cdssync[3], "Never")

    def _cleanup(self):
        '''[TCMS#267489 cleanup] Delete RH repo '''
        RHUIManagerRepo.delete_repo(self.rs.Instances["RHUA"][0], ["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])

        '''[TCMS#267489 cleanup] Remove RH certificate from RHUI '''
        RHUIManager.remove_rh_certs(self.rs.Instances["RHUA"][0])

        '''[TCMS#267489 cleanup] Remove cds '''
        RHUIManagerCds.delete_cds(self.rs.Instances["RHUA"][0], "Cluster1", [self.rs.Instances["CDS"][0].private_hostname])


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
