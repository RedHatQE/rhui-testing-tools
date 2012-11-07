#! /usr/bin/python -tt

import nose

from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_cds import *
from rhuilib.rhuimanager_client import *
from rhuilib.rhuimanager_repo import *


class test_bug_846386(RHUITestcase):
    def test_01_initial_run(self):
        '''[Bug#846386 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.RHUA)

    def test_02_add_cds(self):
        '''[Bug#846386 setup] Add cds '''
        RHUIManagerCds.add_cds(self.rs.RHUA, "Cluster1", self.rs.CDS[0].hostname)

    def test_03_add_protected_repo(self):
        '''[Bug#846386 setup] Create protected repo '''
        RHUIManagerRepo.add_custom_repo(self.rs.RHUA, "custom_repo_1")

    def test_04_add_unprotected_repo(self):
        '''[Bug#846386 setup] Create unprotected repo '''
        RHUIManagerRepo.add_custom_repo(self.rs.RHUA, "custom_repo_2", entitlement="n")

    def test_05_upload_content(self):
        '''[Bug#846386 setup] Upload content to unprotected repo '''
        RHUIManagerRepo.upload_content(self.rs.RHUA, ["custom_repo_2"], "/etc/rhui/confrpm")

    def test_06_associate_repo_cds(self):
        '''[Bug#846386 setup] Associate cdses with cluster '''
        RHUIManagerCds.associate_repo_cds(self.rs.RHUA, "Cluster1", ["custom_repo_1", "custom_repo_2"])

    def test_07_generate_ent_cert(self):
        '''[Bug#846386 test] Generate entitlement certificate '''
        RHUIManagerClient.generate_ent_cert(self.rs.RHUA, "Cluster1", ["custom_repo_1"], "cert-repo1", "/root/", validity_days="", cert_pw=None)

    def test_08_create_conf_rpm(self):
        '''[Bug#846386 test] Create configuration rpm '''
        RHUIManagerClient.create_conf_rpm(self.rs.RHUA, "Cluster1", self.rs.CDS[0].hostname, "/root", "/root/cert-repo1.crt", "/root/cert-repo1.key", "repo1", "3.0", ["custom_repo_2"])

    def test_09_remove_cds(self):
        '''[Bug#846386 clenup] Remove cds '''
        RHUIManagerCds.delete_cds(self.rs.RHUA, "Cluster1", [self.rs.CDS[0].hostname])

    def test_10_delete_custom_repo(self):
        '''[Bug#846386 cleanup] Delete custom repos '''
        RHUIManagerRepo.delete_repo(self.rs.RHUA, ["custom_repo_1", "custom_repo_2"])


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
