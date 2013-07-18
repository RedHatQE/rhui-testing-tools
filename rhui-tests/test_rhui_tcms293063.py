#! /usr/bin/python -tt

import nose

from rhuilib.util import *
from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_cds import *
from rhuilib.rhuimanager_client import *
from rhuilib.rhuimanager_repo import *
from rhuilib.pulp_admin import PulpAdmin
from rhuilib.cds import RhuiCds

class test_tcms_293063(RHUITestcase):
    def _setup(self):
        '''[TCMS#293063 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.Instances["RHUA"][0])

        '''[TCMS#293063 setup] Add cds'''
        RHUIManagerCds.add_cds(self.rs.Instances["RHUA"][0], "Cluster1", self.rs.Instances["CDS"][0].private_hostname)

        '''[TCMS#293063 setup] Create custom repos'''
        RHUIManagerRepo.add_custom_repo(self.rs.Instances["RHUA"][0], "repo1")
        RHUIManagerRepo.add_custom_repo(self.rs.Instances["RHUA"][0], "repo2")

        '''[TCMS#293063 setup] Associate repos with cluster'''
        RHUIManagerCds.associate_repo_cds(self.rs.Instances["RHUA"][0], "Cluster1", ["repo1", "repo2"])
        
        '''[TCMS#293063 setup] Unassociate repo1 from cluster '''
        RHUIManagerCds.unassociate_repo_cds(self.rs.Instances["RHUA"][0], "Cluster1", ["repo1"])

    def _test(self):
        '''[TCMS#293063 test] Check CDS info screen'''
        rhui_cds = RhuiCds(
                           hostname=self.rs.Instances["CDS"][0].private_hostname,
                           description='RHUI CDS',
                           cluster='Cluster1',
                           repos=["repo2"])
                           
        nose.tools.assert_equal(RHUIManagerCds.info(self.rs.Instances["RHUA"][0], ["Cluster1"]), [rhui_cds])

        '''[TCMS#293063 test] Check pulp-admin and rhui cluster info are the same'''
        nose.tools.assert_equal(PulpAdmin.cds_list(self.rs.Instances["RHUA"][0]), RHUIManagerCds.info(self.rs.Instances["RHUA"][0], ['Cluster1']))

    def _cleanup(self):
        '''[TCMS#293063 cleanup] Remove cds'''
        RHUIManagerCds.delete_cds(self.rs.Instances["RHUA"][0], "Cluster1", [self.rs.Instances["CDS"][0].private_hostname])

        '''[TCMS#293063 cleanup] Remove custom repos'''
        RHUIManagerRepo.delete_repo(self.rs.Instances["RHUA"][0], ["repo1", "repo2"])

if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
