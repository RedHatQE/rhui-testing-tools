#! /usr/bin/python -tt

import nose

from rhuilib.util import *
from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_cds import *
from rhuilib.rhuimanager_client import *
from rhuilib.rhuimanager_repo import *
from rhuilib.rhuimanager_sync import *
from rhuilib.rhuimanager_entitlements import *
from rhuilib.pulp_admin import PulpAdmin
from rhuilib.cds import RhuiCds


class test_tcms_178466(RHUITestcase, RHUI_has_RH_cert, RHUI_has_two_CDSes):
    def _setup(self):

        '''[TCMS#178466 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.RHUA)

        '''[TCMS#178466 setup] Add cdses '''
        RHUIManagerCds.add_cds(self.rs.RHUA, "Cluster1", self.rs.CDS[0].private_hostname)
        RHUIManagerCds.add_cds(self.rs.RHUA, "Cluster2", self.rs.CDS[1].private_hostname)

        '''[TCMS#178466 setup] Create custom repo '''
        RHUIManagerRepo.add_custom_repo(self.rs.RHUA, "repo1")

        '''[TCMS#178466 setup] Upload RH content certificate '''
        RHUIManagerEntitlements.upload_content_cert(self.rs.RHUA, self.cert)

        '''[TCMS#178466 setup] Add rh repo '''
        RHUIManagerRepo.add_rh_repo_by_repo(self.rs.RHUA, ["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])

        '''[TCMS#178466 setup] Associate repos with clusters '''
        RHUIManagerCds.associate_repo_cds(self.rs.RHUA, "Cluster1", ["repo1", "Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])
        RHUIManagerCds.associate_repo_cds(self.rs.RHUA, "Cluster2", ["repo1", "Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])

    def _test(self):
        '''[TCMS#178466 test] Check cds info screen '''
        cds0 = RhuiCds(
                hostname=self.rs.CDS[0].private_hostname,
                cluster="Cluster1",
                repos=["repo1",
                "Red Hat Update Infrastructure 2 (RPMs) (6Server-x86_64)"]
                )
        cds1 = RhuiCds(
                hostname=self.rs.CDS[1].private_hostname,
                cluster="Cluster2",
                repos=["repo1",
                    "Red Hat Update Infrastructure 2 (RPMs) (6Server-x86_64)"]
                )
        nose.tools.assert_equal(sorted(RHUIManagerCds.info(self.rs.RHUA, ["Cluster1", "Cluster2"])),
                sorted([cds0, cds1]))

        '''[TCMS#178466 test] Check pulp-admin cds list and rhui cds info are the same '''
        pulp_cdses = PulpAdmin.cds_list(self.rs.RHUA)
        rhui_cdses = RHUIManagerCds.info(self.rs.RHUA, ["Cluster1", "Cluster2"])
        nose.tools.assert_equals(sorted(pulp_cdses), sorted(rhui_cdses))

    def _cleanup(self):
        '''[TCMS#178466 cleanup] Remove cdses '''
        RHUIManagerCds.delete_cds(self.rs.RHUA, "Cluster1", [self.rs.CDS[0].private_hostname])
        RHUIManagerCds.delete_cds(self.rs.RHUA, "Cluster2", [self.rs.CDS[1].private_hostname])

        '''[TCMS#178466 cleanup] Delete RH repo '''
        RHUIManagerRepo.delete_repo(self.rs.RHUA, ["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])

        '''[TCMS#178466 cleanup] Delete custom repos '''
        RHUIManagerRepo.delete_repo(self.rs.RHUA, ["repo1"])

        '''[TCMS#178466 cleanup] Remove RH certificate from RHUI '''
        RHUIManager.remove_rh_certs(self.rs.RHUA)


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
