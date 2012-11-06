#! /usr/bin/python -tt

import nose

from rhuilib.util import *
from rhuilib.rhuisetup import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_cds import *
from rhuilib.rhuimanager_client import *
from rhuilib.rhuimanager_repo import *
from rhuilib.pulp_admin import PulpAdmin


class test_tcms_178465(object):
    def __init__(self):
        self.rs = RHUIsetup()
        self.rs.setup_from_yamlfile()

    def __del__(self):
        self.rs.__del__()

    def test_01_initial_run(self):
        ''' Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.RHUA)

    def test_02_add_cds(self):
        ''' Add cds '''
        RHUIManagerCds.add_cds(self.rs.RHUA, "Cluster1", self.rs.CDS[0].hostname)

    def test_03_add_custom_repos(self):
        ''' Create custom repos '''
        RHUIManagerRepo.add_custom_repo(self.rs.RHUA, "repo1")
        RHUIManagerRepo.add_custom_repo(self.rs.RHUA, "repo2")

    def test_06_associate_repo_cds(self):
        ''' Associate repos with cluster '''
        RHUIManagerCds.associate_repo_cds(self.rs.RHUA, "Cluster1", ["repo1", "repo2"])

    def test_07_info_screen(self):
        ''' Check cds info screen '''
        nose.tools.assert_equal(RHUIManagerCds.info(self.rs.RHUA, ["Cluster1"]), [{'Instances': [{'hostname': 'cds1.example.com', 'client': 'cds1.example.com', 'CDS': 'cds1.example.com'}], 'Repositories': ['repo1', 'repo2'], 'Name': 'Cluster1'}])

    def test_08_unassociate_repo_cds(self):
        ''' Unassociate repos from cluster '''
        RHUIManagerCds.unassociate_repo_cds(self.rs.RHUA, "Cluster1", ["repo1"])

    def test_09_info_screen(self):
        ''' Check cds info screen '''
        nose.tools.assert_equal(RHUIManagerCds.info(self.rs.RHUA, ["Cluster1"]), [{'Instances': [{'hostname': 'cds1.example.com', 'client': 'cds1.example.com', 'CDS': 'cds1.example.com'}], 'Repositories': ['repo2'], 'Name': 'Cluster1'}])

    def test_10_pulp_admin_list(self):
        ''' Check pulp-admin cds list '''
        result = PulpAdmin.cds_list(self.rs.RHUA)
        nose.tools.assert_equals(result, [{'Status': 'Yes', 'Cluster': 'Cluster1', 'Repos': 'repo2', 'Hostname': 'cds1.example.com', 'Name': 'cds1.example.com'}])
        
    def test_11_remove_cds(self):
        ''' Remove cds '''
        RHUIManagerCds.delete_cds(self.rs.RHUA, "Cluster1", [self.rs.CDS[0].hostname])

    def test_12_delete_custom_repo(self):
        ''' Delete custom repos '''
        RHUIManagerRepo.delete_repo(self.rs.RHUA, ["repo1", "repo2"])


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
