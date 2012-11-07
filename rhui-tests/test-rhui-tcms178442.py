#! /usr/bin/python -tt

import nose
import logging

from rhuilib.util import *
from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_cds import *
from rhuilib.rhuimanager_repo import *
from rhuilib.pulp_admin import PulpAdmin
from rhuilib.cds import RhuiCds

class test_bug_tcms178442(RHUITestcase):
    def __init__(self):
        RHUITestcase.__init__(self)
        if len(self.rs.CDS) < 3:
            raise nose.exc.SkipTest("can't test without having at least three CDSes!")

    def test_01_initial_run(self):
        '''[TCMS#178442 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.RHUA)

    def test_02_add_cds(self):
        '''[TCMS#178442 setup] Add cdses: cds0, cds2 -> cluster1; cds1 -> cluster2'''
        RHUIManagerCds.add_cds(self.rs.RHUA, "Cluster1", self.rs.CDS[0].hostname)
        RHUIManagerCds.add_cds(self.rs.RHUA, "Cluster2", self.rs.CDS[1].hostname)
        RHUIManagerCds.add_cds(self.rs.RHUA, "Cluster1", self.rs.CDS[2].hostname)

    def test_03_add_custom_repos(self):
        '''[TCMS#178442 setup] Create custom repo1 '''
        RHUIManagerRepo.add_custom_repo(self.rs.RHUA, "repo1")

    def test_04_associate_repo_cds(self):
        '''[TCMS#178442 setup] Associate repo1 with both the clusters'''
        RHUIManagerCds.associate_repo_cds(self.rs.RHUA, "Cluster1", ["repo1"])
        RHUIManagerCds.associate_repo_cds(self.rs.RHUA, "Cluster2", ["repo1"])

    def test_05_move_cds(self):
        '''[TCMS#178442 test] Move cds2 to cluster2'''
        RHUIManagerCds.move_cds(self.rs.RHUA, [self.rs.CDS[2].hostname], "Cluster2")

    def test_06_info_screen(self):
        '''[TCMS#178442 test] Check that cds2 moved to cluster2'''
        cds0 = RhuiCds(
                hostname = self.rs.CDS[0].hostname,
                cluster = 'Cluster1',
                repos = ['repo1'])
        cds1 = RhuiCds(
                hostname = self.rs.CDS[1].hostname,
                cluster = 'Cluster2',
                repos = ['repo1']
                )
        cds2 = RhuiCds(
                hostname = self.rs.CDS[2].hostname,
                cluster = 'Cluster2',
                repos = ['repo1']
                )
        nose.tools.assert_equal(sorted(RHUIManagerCds.info(self.rs.RHUA,
            ["Cluster1", "Cluster2"])), sorted([cds0, cds1, cds2]))

    def test_07_pulp_admin_list(self):
        '''[TCMS#178442 test] Check pulp-admin and rhui cluster info are the same'''
        nose.tools.assert_equals(sorted(PulpAdmin.cds_list(self.rs.RHUA)),
                sorted(RHUIManagerCds.info(self.rs.RHUA, ['Cluster1',
                    'Cluster2'])))

    def test_08_delete_custom_repo(self):
        '''[TCMS#178442 cleanup] Delete custom repos '''
        RHUIManagerRepo.delete_repo(self.rs.RHUA, ["repo1"])

    def test_09_remove_cds(self):
        '''[TCMS#178442 cleanup] Remove cdses '''
        RHUIManagerCds.delete_cds(self.rs.RHUA, "Cluster1", [self.rs.CDS[0].hostname])
        RHUIManagerCds.delete_cds(self.rs.RHUA, "Cluster2", [self.rs.CDS[1].hostname])
        RHUIManagerCds.delete_cds(self.rs.RHUA, "Cluster2", [self.rs.CDS[2].hostname])

if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
