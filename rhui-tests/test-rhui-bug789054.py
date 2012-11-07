#! /usr/bin/python -tt

import nose

from rhuilib.expect import *
from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_cds import *
from rhuilib.rhuimanager_repo import *


class test_bug_789054(RHUITestcase):
    def test_01_initial_run(self):
        '''[Bug#789054 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.RHUA)

    def test_02_add_cds(self):
        '''[Bug#789054 setup] Add cds '''
        RHUIManagerCds.add_cds(self.rs.RHUA, "Cluster1", self.rs.CDS[0].hostname)

    def test_03_add_custom_repos(self):
        '''[Bug#789054 setup] Create custom repos '''
        RHUIManagerRepo.add_custom_repo(self.rs.RHUA, "repo1")
        RHUIManagerRepo.add_custom_repo(self.rs.RHUA, "repo2")
        RHUIManagerRepo.add_custom_repo(self.rs.RHUA, "repo3")

    def test_04_associate_repo_cds(self):
        '''[Bug#789054 setup] Associate custom repos with cluster '''
        RHUIManagerCds.associate_repo_cds(self.rs.RHUA, "Cluster1", ["repo1", "repo2", "repo3"])

    def test_05_generate_ent_cert(self):
        '''[Bug#789054 test] Generate entitlement certificate '''
        RHUIManager.screen(self.rs.RHUA, "client")
        Expect.enter(self.rs.RHUA, "e")
        RHUIManager.select_one(self.rs.RHUA, "Cluster1")
        RHUIManager.select(self.rs.RHUA, ["repo1", "repo2"])
        Expect.expect(self.rs.RHUA, "Name of the certificate.*contained with it:")
        Expect.ping_pong(self.rs.RHUA, "cert with spaces", "The name can not contain spaces")

    def test_06_remove_cds(self):
        '''[Bug#789054 cleanup] Remove cds '''
        RHUIManagerCds.delete_cds(self.rs.RHUA, "Cluster1", [self.rs.CDS[0].hostname])

    def test_07_delete_custom_repo(self):
        '''[Bug#789054 cleanup] Delete custom repos '''
        RHUIManagerRepo.delete_repo(self.rs.RHUA, ["repo1", "repo2", "repo3"])


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
