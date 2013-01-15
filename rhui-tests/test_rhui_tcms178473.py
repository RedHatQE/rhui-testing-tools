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
from rhuilib.cds import RhuiCds


class test_tcms_178473(RHUITestcase, RHUI_has_two_CDSes):
    def _setup(self):

        '''[TCMS#178473 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.Instances["RHUA"][0])

        '''[TCMS#178473 setup] Add cdses '''
        RHUIManagerCds.add_cds(self.rs.Instances["RHUA"][0], "Cluster1", self.rs.Instances["CDS"][0].private_hostname, self.rs.Instances["CDS"][0].public_hostname)
        RHUIManagerCds.add_cds(self.rs.Instances["RHUA"][0], "Cluster2", self.rs.Instances["CDS"][1].private_hostname, self.rs.Instances["CDS"][1].public_hostname)

        '''[TCMS#178473 setup] Create custom repo '''
        RHUIManagerRepo.add_custom_repo(self.rs.Instances["RHUA"][0], "repo1")

        '''[TCMS#178473 setup] Associate repos with clusters '''
        RHUIManagerCds.associate_repo_cds(self.rs.Instances["RHUA"][0], "Cluster1", ["repo1"])
        RHUIManagerCds.associate_repo_cds(self.rs.Instances["RHUA"][0], "Cluster2", ["repo1"])

    def _test(self):
        '''[TCMS#178473 test] Check cds info screen '''
        cds0 = RhuiCds(
                hostname=self.rs.Instances["CDS"][0].private_hostname,
                client_hostname=self.rs.Instances["CDS"][0].public_hostname,
                cluster="Cluster1",
                repos=["repo1"]
                )
        cds1 = RhuiCds(
                hostname=self.rs.Instances["CDS"][1].private_hostname,
                client_hostname=self.rs.Instances["CDS"][1].public_hostname,
                cluster="Cluster2",
                repos=["repo1"]
                )
        nose.tools.assert_equal(sorted(RHUIManagerCds.info(self.rs.Instances["RHUA"][0], ["Cluster1", "Cluster2"])),
                sorted([cds0, cds1]))

    def _cleanup(self):
        '''[TCMS#178473 cleanup] Remove cdses '''
        RHUIManagerCds.delete_cds(self.rs.Instances["RHUA"][0], "Cluster1", [self.rs.Instances["CDS"][0].private_hostname])
        RHUIManagerCds.delete_cds(self.rs.Instances["RHUA"][0], "Cluster2", [self.rs.Instances["CDS"][1].private_hostname])

        '''[TCMS#178473 cleanup] Delete custom repos '''
        RHUIManagerRepo.delete_repo(self.rs.Instances["RHUA"][0], ["repo1"])


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
