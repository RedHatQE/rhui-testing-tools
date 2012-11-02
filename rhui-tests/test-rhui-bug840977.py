#! /usr/bin/python -tt

import argparse
import nose

from rhuilib.util import *
from rhuilib.rhuisetup import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_cds import *
from rhuilib.rhuimanager_repo import *


class test_bug_840977(object):
    def __init__(self):
        argparser = argparse.ArgumentParser(description='RHUI bug 840977')
        args = argparser.parse_args()
        self.rs = RHUIsetup()
        self.rs.setup_from_rolesfile()

    def __del__(self):
        self.rs.__del__()

    def test_01_initial_run(self):
        ''' Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.RHUA)

    def test_02_add_cds(self):
        ''' Add cds '''
        RHUIManagerCds.add_cds(self.rs.RHUA, "Cluster1", self.rs.CDS[0].hostname)

    def test_03_add_protected_repo(self):
        ''' Create protected repo '''
        RHUIManagerRepo.add_custom_repo(self.rs.RHUA, "custom_repo_1")

    def test_04_add_unprotected_repo(self):
        ''' Create unprotected repo '''
        RHUIManagerRepo.add_custom_repo(self.rs.RHUA, "custom_repo_2", entitlement="n")

    def test_05_test_repo_assignment(self):
        ''' Test repos assignment '''
        RHUIManager.screen(self.rs.RHUA, "cds")
        Expect.enter(self.rs.RHUA, "i")
        RHUIManager.select(self.rs.RHUA, ["Cluster1"])
        Expect.expect(self.rs.RHUA, "Repositories.*\(None\).*rhui \(cds\) =>")
        Expect.enter(self.rs.RHUA, "q")

    def test_06_remove_cds(self):
        ''' Remove cds '''
        RHUIManagerCds.delete_cds(self.rs.RHUA, "Cluster1", [self.rs.CDS[0].hostname])

    def test_07_delete_custom_repo(self):
        ''' Delete custom repos '''
        RHUIManagerRepo.delete_repo(self.rs.RHUA, ["custom_repo_1", "custom_repo_2"])


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
