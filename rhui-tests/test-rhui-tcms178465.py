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


class test_tcms_178465(RHUITestcase):
    def _setup(self):
        '''[TCMS#178465 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.RHUA)

        '''[TCMS#178465 setup] Add cds '''
        RHUIManagerCds.add_cds(self.rs.RHUA, "Cluster1", self.rs.CDS[0].hostname)

        '''[TCMS#178465 setup] Create custom repos repo1, repo2'''
        RHUIManagerRepo.add_custom_repo(self.rs.RHUA, "repo1")
        RHUIManagerRepo.add_custom_repo(self.rs.RHUA, "repo2")

        '''[TCMS#178465 setup] Associate repos with cluster '''
        RHUIManagerCds.associate_repo_cds(self.rs.RHUA, "Cluster1", ["repo1", "repo2"])

    def _test(self):
        '''[TCMS#178465 test] Check repos are associated '''
        cds = RhuiCds(
                hostname=self.rs.CDS[0].hostname,
                cluster="Cluster1",
                repos=["repo1", "repo2"]
                )
        nose.tools.assert_equal(RHUIManagerCds.info(self.rs.RHUA, ["Cluster1"]), [cds])

        '''[TCMS#178465 test] Unassociate repo1 from cluster '''
        RHUIManagerCds.unassociate_repo_cds(self.rs.RHUA, "Cluster1", ["repo1"])

        '''[TCMS#178465 test] Check repo1 has been unassociated'''
        cds = RhuiCds(
                hostname=self.rs.CDS[0].hostname,
                cluster="Cluster1",
                repos=["repo2"]
                )
        nose.tools.assert_equal(RHUIManagerCds.info(self.rs.RHUA, ["Cluster1"]), [cds])

        '''[TCMS#178465 test] Check pulp-admin cds list and rhui cluster info are the same'''
        pulp_cdses = PulpAdmin.cds_list(self.rs.RHUA)
        rhui_cdses = RHUIManagerCds.info(self.rs.RHUA, ["Cluster1"])
        nose.tools.assert_equals(pulp_cdses, rhui_cdses)

    def _cleanup(self):
        '''[TCMS#178465 cleanup] Remove cds '''
        RHUIManagerCds.delete_cds(self.rs.RHUA, "Cluster1", [self.rs.CDS[0].hostname])

        '''[TCMS#178465 cleanup] Delete custom repos '''
        RHUIManagerRepo.delete_repo(self.rs.RHUA, ["repo1", "repo2"])


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
