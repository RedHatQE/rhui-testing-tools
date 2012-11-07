#! /usr/bin/python -tt

import nose

from rhuilib.util import *
from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_cds import *
from rhuilib.rhuimanager_client import *
from rhuilib.rhuimanager_repo import *
from rhuilib.rhuimanager_sync import *
from rhuilib.rhuimanager_entitlements import *


class test_bug_tcms178467(RHUITestcase):
    def __init__(self):
        RHUITestcase.__init__()
        if not 'rhcert' in self.rs.config.keys():
            raise nose.exc.SkipTest("can't test without RH certificate")
        self.cert = self.rs.config['rhcert']

    def _sync(self):
        RHUIManagerSync.sync_cds(self.rs.RHUA, [self.rs.CDS[0].hostname])
        cdssync = ["UP", "In Progress", "", ""]
        while cdssync[1] == "In Progress":
            time.sleep(10)
            cdssync = RHUIManagerSync.get_cds_status(self.rs.RHUA, self.rs.CDS[0].hostname)
        nose.tools.assert_equal(cdssync[3], "Success")

    def test_01_initial_run(self):
        '''[TCMS#178467 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.RHUA)

    def test_02_add_cds(self):
        '''[TCMS#178467 setup] Add cds '''
        RHUIManagerCds.add_cds(self.rs.RHUA, "Cluster1", self.rs.CDS[0].hostname)

    def test_03_add_custom_repos(self):
        '''[TCMS#178467 setup] Create custom repo '''
        self.rs.RHUA.sftp.put("/usr/share/rhui-testing-tools/testing-data/public.key", "/root/public.key")
        RHUIManagerRepo.add_custom_repo(self.rs.RHUA, "repo1", entitlement="y", custom_gpg="/root/public.key")

    def test_04_upload_signed_rpm(self):
        '''[TCMS#178467 setup] Upload signed rpm to custom repo '''
        self.rs.RHUA.sftp.put("/usr/share/rhui-testing-tools/testing-data/custom-signed-rpm-1-0.1.fc17.noarch.rpm", "/root/custom-signed-rpm-1-0.1.fc17.noarch.rpm")
        RHUIManagerRepo.upload_content(self.rs.RHUA, ["repo1"], "/root/custom-signed-rpm-1-0.1.fc17.noarch.rpm")

    def test_05_upload_unsigned_rpm(self):
        '''[TCMS#178467 setup] Upload unsigned rpm to custom repo '''
        self.rs.RHUA.sftp.put("/usr/share/rhui-testing-tools/testing-data/custom-unsigned-rpm-1-0.1.fc17.noarch.rpm", "/root/custom-unsigned-rpm-1-0.1.fc17.noarch.rpm")
        RHUIManagerRepo.upload_content(self.rs.RHUA, ["repo1"], "/root/custom-unsigned-rpm-1-0.1.fc17.noarch.rpm")

    def test_06_upload_content_cert(self):
        '''[TCMS#178467 setup] Upload RH content certificate '''
        RHUIManagerEntitlements.upload_content_cert(self.rs.RHUA, self.cert)

    def test_07_add_rh_repo_by_repo(self):
        '''[TCMS#178467 setup] Add rh repo '''
        RHUIManagerRepo.add_rh_repo_by_repo(self.rs.RHUA, ["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])

    def test_08_associate_repo_cds(self):
        '''[TCMS#178467 setup] Associate repos with cluster '''
        RHUIManagerCds.associate_repo_cds(self.rs.RHUA, "Cluster1", ["repo1", "Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])

    def test_09_sync_repo(self):
        '''[TCMS#178467 setup] Sync RH repo '''
        RHUIManagerSync.sync_repo(self.rs.RHUA, ["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])
        reposync = ["In Progress", "", ""]
        while reposync[0] == "In Progress":
            time.sleep(10)
            reposync = RHUIManagerSync.get_repo_status(self.rs.RHUA, "Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)")
        nose.tools.assert_equal(reposync[2], "Success")

    def test_10_sync_cds(self):
        '''[TCMS#178467 setup] Sync cds '''
        self._sync()

    def test_11_check_cds_content(self):
        '''[TCMS#178467 test] Check repo content on cds '''
        Expect.ping_pong(self.rs.CDS[0], "test -f /var/lib/pulp-cds/repos/repo1/custom-signed-rpm-1-0.1.fc17.noarch.rpm && echo SUCCESS", "[^ ]SUCCESS")
        Expect.ping_pong(self.rs.CDS[0], "find /var/lib/pulp-cds/ -name 'mongodb*.rpm' | grep mongodb && echo SUCCESS", "[^ ]SUCCESS")

    def test_12_delete_custom_repo(self):
        '''[TCMS#178467 cleanup] Delete custom repos '''
        RHUIManagerRepo.delete_repo(self.rs.RHUA, ["repo1"])

    def test_13_delete_rh_repo(self):
        '''[TCMS#178467 cleanup] Delete RH repo '''
        RHUIManagerRepo.delete_repo(self.rs.RHUA, ["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])

    def test_14_sync_cds(self):
        '''[TCMS#178467 cleanup] Sync cds '''
        self._sync()

    def test_15_remove_cds(self):
        '''[TCMS#178467 cleanup] Remove cds '''
        RHUIManagerCds.delete_cds(self.rs.RHUA, "Cluster1", [self.rs.CDS[0].hostname])

if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
