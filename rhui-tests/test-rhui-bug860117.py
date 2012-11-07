#! /usr/bin/python -tt

import nose

from rhuilib.util import *
from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_cds import *
from rhuilib.rhuimanager_client import *
from rhuilib.rhuimanager_repo import *


class test_bug_860117(RHUITestcase):
    def __init__(self):
        RHUITestcase.__init__(self)
        if len(self.rs.CDS) < 2:
            raise nose.exc.SkipTest("can't test without having at least two CDSes!")

        '''[Bug#860117 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.RHUA)

        '''[Bug#860117 setup] Add cdses '''
        RHUIManagerCds.add_cds(self.rs.RHUA, "Cluster1", self.rs.CDS[0].hostname)
        RHUIManagerCds.add_cds(self.rs.RHUA, "Cluster2", self.rs.CDS[1].hostname)

        '''[Bug#860117 setup] Create custom repos '''
        RHUIManagerRepo.add_custom_repo(self.rs.RHUA, "repo1")
        RHUIManagerRepo.add_custom_repo(self.rs.RHUA, "repo2")
        RHUIManagerRepo.add_custom_repo(self.rs.RHUA, "repo3")
        RHUIManagerRepo.add_custom_repo(self.rs.RHUA, "repo4")
        RHUIManagerRepo.add_custom_repo(self.rs.RHUA, "repo5")
        RHUIManagerRepo.add_custom_repo(self.rs.RHUA, "repo6")

    def test_bug_860117(self):
        '''[Bug#860117 test] Associate custom repos with cluster '''
        RHUIManagerCds.associate_repo_cds(self.rs.RHUA, "Cluster1", ["repo1", "repo3", "repo6"])

        '''[Bug#860117 test] Generate entitlement certificate '''
        RHUIManagerClient.generate_ent_cert(self.rs.RHUA, "Cluster1", ["repo1", "repo3", "repo6"], "cert-repo1", "/root/", validity_days="", cert_pw=None)

        '''[Bug#860117 test] Create configuration rpm '''
        RHUIManagerClient.create_conf_rpm(self.rs.RHUA, "Cluster1", self.rs.CDS[0].hostname, "/root", "/root/cert-repo1.crt", "/root/cert-repo1.key", "repo1", "3.0")

    def __del__(self):
        '''[Bug#860117 cleanup] Remove cdses '''
        RHUIManagerCds.delete_cds(self.rs.RHUA, "Cluster1", [self.rs.CDS[0].hostname])
        RHUIManagerCds.delete_cds(self.rs.RHUA, "Cluster2", [self.rs.CDS[1].hostname])

        '''[Bug#860117 cleanup] Delete custom repos '''
        RHUIManagerRepo.delete_repo(self.rs.RHUA, ["repo1", "repo2", "repo3", "repo4", "repo5", "repo6"])

        RHUITestcase.__del__()


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
