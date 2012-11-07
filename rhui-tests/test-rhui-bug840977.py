#! /usr/bin/python -tt

import nose

from rhuilib.util import *
from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_cds import *
from rhuilib.rhuimanager_repo import *


class test_bug_840977(RHUITestcase):
    def test_01_initial_run(self):
        '''[Bug#840977 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.RHUA)

    def test_02_add_cds(self):
        '''[Bug#840977 setup] Add cds '''
        RHUIManagerCds.add_cds(self.rs.RHUA, "Cluster1", self.rs.CDS[0].hostname)

    def test_03_add_protected_repo(self):
        '''[Bug#840977 setup] Create protected repo '''
        RHUIManagerRepo.add_custom_repo(self.rs.RHUA, "custom_repo_1")

    def test_04_add_unprotected_repo(self):
        '''[Bug#840977 setup] Create unprotected repo '''
        RHUIManagerRepo.add_custom_repo(self.rs.RHUA, "custom_repo_2", entitlement="n")

    def test_05_test_repo_assignment(self):
        '''[Bug#840977 test] Test repos assignment '''
        RHUIManager.screen(self.rs.RHUA, "cds")
        Expect.enter(self.rs.RHUA, "i")
        RHUIManager.select(self.rs.RHUA, ["Cluster1"])
        Expect.expect(self.rs.RHUA, "Repositories.*\(None\).*rhui \(cds\) =>")
        Expect.ping_pong(self.rs.RHUA, "q", "root@")

    def test_06_remove_cds(self):
        '''[Bug#840977 cleanup] Remove cds '''
        RHUIManagerCds.delete_cds(self.rs.RHUA, "Cluster1", [self.rs.CDS[0].hostname])

    def test_07_delete_custom_repo(self):
        '''[Bug#840977 cleanup] Delete custom repos '''
        RHUIManagerRepo.delete_repo(self.rs.RHUA, ["custom_repo_1", "custom_repo_2"])


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
