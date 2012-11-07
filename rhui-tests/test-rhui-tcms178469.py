#! /usr/bin/python -tt

import nose

from rhuilib.util import *
from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_cds import *
from rhuilib.rhuimanager_client import *
from rhuilib.rhuimanager_repo import *
from rhuilib.rhuimanager_sync import *


class test_bug_tcms178469(RHUITestcase):
    def __init__(self):
        RHUITestcase.__init__(self)
        if len(self.rs.CDS) < 2:
            raise nose.exc.SkipTest("can't test without having at least two CDSes!")

    def _sync(self):
        RHUIManagerSync.sync_cds(self.rs.RHUA, [self.rs.CDS[0].hostname, self.rs.CDS[1].hostname])
        for cds in [self.rs.CDS[0].hostname, self.rs.CDS[1].hostname]:
            cdssync = ["UP", "In Progress", "", ""]
            while cdssync[1] == "In Progress":
                time.sleep(10)
                cdssync = RHUIManagerSync.get_cds_status(self.rs.RHUA, cds)
            nose.tools.assert_equal(cdssync[3], "Success")

    def test_01_initial_run(self):
        '''[TCMS#178469 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.RHUA)

    def test_02_add_cds(self):
        '''[TCMS#178469 setup] Add cdses '''
        RHUIManagerCds.add_cds(self.rs.RHUA, "Cluster1", self.rs.CDS[0].hostname)
        RHUIManagerCds.add_cds(self.rs.RHUA, "Cluster2", self.rs.CDS[1].hostname)

    def test_03_add_custom_repos(self):
        '''[TCMS#178469 setup] Create custom repo '''
        self.rs.RHUA.sftp.put("/usr/share/rhui-testing-tools/testing-data/public.key", "/root/public.key")
        RHUIManagerRepo.add_custom_repo(self.rs.RHUA, "repo1", entitlement="y", custom_gpg="/root/public.key")

    def test_04_associate_repo_cds(self):
        '''[TCMS#178469 setup] Associate custom repos with cluster '''
        RHUIManagerCds.associate_repo_cds(self.rs.RHUA, "Cluster1", ["repo1"])
        RHUIManagerCds.associate_repo_cds(self.rs.RHUA, "Cluster2", ["repo1"])

    def test_05_upload_signed_rpm(self):
        '''[TCMS#178469 setup] Upload signed rpm to custom repo '''
        self.rs.RHUA.sftp.put("/usr/share/rhui-testing-tools/testing-data/custom-signed-rpm-1-0.1.fc17.noarch.rpm", "/root/custom-signed-rpm-1-0.1.fc17.noarch.rpm")
        RHUIManagerRepo.upload_content(self.rs.RHUA, ["repo1"], "/root/custom-signed-rpm-1-0.1.fc17.noarch.rpm")

    def test_06_upload_unsigned_rpm(self):
        '''[TCMS#178469 setup] Upload unsigned rpm to custom repo '''
        self.rs.RHUA.sftp.put("/usr/share/rhui-testing-tools/testing-data/custom-unsigned-rpm-1-0.1.fc17.noarch.rpm", "/root/custom-unsigned-rpm-1-0.1.fc17.noarch.rpm")
        RHUIManagerRepo.upload_content(self.rs.RHUA, ["repo1"], "/root/custom-unsigned-rpm-1-0.1.fc17.noarch.rpm")

    def test_07_sync_cds(self):
        '''[TCMS#178469 setup] Sync cdses '''
        self._sync()

    def test_08_check_cds_content(self):
        '''[TCMS#178469 test] Check repo content on cdses '''
        for cds in self.rs.CDS:
            Expect.ping_pong(cds, "test -f /var/lib/pulp-cds/repos/repo1/custom-signed-rpm-1-0.1.fc17.noarch.rpm && echo SUCCESS", "[^ ]SUCCESS")

    def test_09_delete_custom_repo(self):
        '''[TCMS#178469 test] Delete custom repos '''
        RHUIManagerRepo.delete_repo(self.rs.RHUA, ["repo1"])

    def test_10_sync_cds(self):
        '''[TCMS#178469 test] Sync cdses '''
        self._sync()

    def test_11_check_cds_content(self):
        '''[TCMS#178469 test] Check repo content on cdses '''
        for cds in self.rs.CDS:
            Expect.ping_pong(cds, "test -f /var/lib/pulp-cds/repos/repo1/custom-signed-rpm-1-0.1.fc17.noarch.rpm || echo FAILURE", "[^ ]FAILURE")

    def test_12_remove_cds(self):
        '''[TCMS#178469 cleanup] Remove cdses '''
        RHUIManagerCds.delete_cds(self.rs.RHUA, "Cluster1", [self.rs.CDS[0].hostname])
        RHUIManagerCds.delete_cds(self.rs.RHUA, "Cluster2", [self.rs.CDS[1].hostname])

if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
