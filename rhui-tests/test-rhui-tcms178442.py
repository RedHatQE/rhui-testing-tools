#! /usr/bin/python -tt

import nose
import logging

from rhuilib.util import *
from rhuilib.rhuisetup import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_cds import *
from rhuilib.rhuimanager_repo import *
from rhuilib.pulp_admin import *

class test_bug_tcms178442(object):
    def __init__(self):
        self.rs = RHUIsetup()
        self.rs.setup_from_yamlfile()
        if len(self.rs.CDS) < 3:
            raise nose.exc.SkipTest("can't test without having at least three CDSes!")

    def __del__(self):
        self.rs.__del__()

    def test_01_initial_run(self):
        ''' Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.RHUA)

    def test_02_add_cds(self):
        ''' Add cdses '''
        RHUIManagerCds.add_cds(self.rs.RHUA, "Cluster1", self.rs.CDS[0].hostname)
        RHUIManagerCds.add_cds(self.rs.RHUA, "Cluster2", self.rs.CDS[1].hostname)
        RHUIManagerCds.add_cds(self.rs.RHUA, "Cluster1", self.rs.CDS[2].hostname)

    def test_03_add_custom_repos(self):
        ''' Create custom repo '''
        RHUIManagerRepo.add_custom_repo(self.rs.RHUA, "repo1")

    def test_04_associate_repo_cds(self):
        ''' Associate repo with clusters '''
        RHUIManagerCds.associate_repo_cds(self.rs.RHUA, "Cluster1", ["repo1"])
        RHUIManagerCds.associate_repo_cds(self.rs.RHUA, "Cluster2", ["repo1"])

    def test_05_move_cds(self):
        ''' Move cds '''
        RHUIManagerCds.move_cds(self.rs.RHUA, [self.rs.CDS[2].hostname], "Cluster2")

    def test_06_info_screen(self):
        ''' Check cds info screen '''
        nose.tools.assert_equal(RHUIManagerCds.info(self.rs.RHUA, ["Cluster1", "Cluster2"]), sorted([{'Instances': sorted([{'hostname': 'cds1.example.com', 'client': 'cds1.example.com', 'CDS': 'cds1.example.com'}]), 'Repositories': ['repo1'], 'Name': 'Cluster1'}, {'Instances': [{'hostname': 'cds2.example.com', 'client': 'cds2.example.com', 'CDS': 'cds2.example.com'}, {'hostname': 'cds3.example.com', 'client': 'cds3.example.com', 'CDS': 'cds3.example.com'}], 'Repositories': ['repo1'], 'Name': 'Cluster2'}]))

    def test_07_pulp_admin_list(self):
        ''' Check pulp-admin cds list '''
        result = PulpAdmin.cds_list(self.rs.RHUA)
        nose.tools.assert_equals(result, sorted([{'Status': 'Yes', 'Cluster': 'Cluster2', 'Repos': 'repo1', 'Hostname': 'cds3.example.com', 'Name': 'cds3.example.com'}, {'Status': 'Yes', 'Cluster': 'Cluster2', 'Repos': 'repo1', 'Hostname': 'cds2.example.com', 'Name': 'cds2.example.com'}, {'Status': 'Yes', 'Cluster': 'Cluster1', 'Repos': 'repo1', 'Hostname': 'cds1.example.com', 'Name': 'cds1.example.com'}]))

    def test_08_delete_custom_repo(self):
        ''' Delete custom repos '''
        RHUIManagerRepo.delete_repo(self.rs.RHUA, ["repo1"])

    def test_09_remove_cds(self):
        ''' Remove cdses '''
        RHUIManagerCds.delete_cds(self.rs.RHUA, "Cluster1", [self.rs.CDS[0].hostname])
        RHUIManagerCds.delete_cds(self.rs.RHUA, "Cluster2", [self.rs.CDS[1].hostname])
        RHUIManagerCds.delete_cds(self.rs.RHUA, "Cluster2", [self.rs.CDS[2].hostname])

if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
