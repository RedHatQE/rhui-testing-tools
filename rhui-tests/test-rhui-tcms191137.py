#! /usr/bin/python -tt

import nose
import time

from rhuilib.util import *
from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_cds import *
from rhuilib.rhuimanager_client import *
from rhuilib.rhuimanager_repo import *
from rhuilib.rhuimanager_sync import *
from rhuilib.rhuimanager_entitlements import *


class test_tcms_191137(RHUITestcase):
    def __init__(self):
        RHUITestcase.__init__()
        if not 'rhrpm' in self.rs.config.keys():
            raise nose.exc.SkipTest("can't test without RH-signed RPM")
        self.rhrpm = self.rs.config['rhrpm']
        if not 'rhcert' in self.rs.config.keys():
            raise nose.exc.SkipTest("can't test without RH certificate")
        self.cert = self.rs.config['rhcert']
        (self.rhrpmnvr, self.rhrpmname) = Util.get_rpm_details(self.rhrpm)

    def test_01_initial_run(self):
        '''[TCMS#191137 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.RHUA)

    def test_02_add_cds(self):
        '''[TCMS#191137 setup] Add cds '''
        RHUIManagerCds.add_cds(self.rs.RHUA, "Cluster1", self.rs.CDS[0].hostname)

    def test_03_cli_remove_conf_rpm(self):
        '''[TCMS#191137 setup] Remove rhui configuration rpm from client '''
        for cli in self.rs.CLI:
            Util.remove_conf_rpm(cli)

    def test_04_add_custom_repos(self):
        '''[TCMS#191137 setup] Create custom repo '''
        self.rs.RHUA.sftp.put("/usr/share/rhui-testing-tools/testing-data/public.key", "/root/public.key")
        RHUIManagerRepo.add_custom_repo(self.rs.RHUA, "repo1", entitlement="n", custom_gpg="/root/public.key")

    def test_05_upload_content_cert(self):
        '''[TCMS#191137 setup] Upload RH content certificate '''
        RHUIManagerEntitlements.upload_content_cert(self.rs.RHUA, self.cert)

    def test_06_add_rh_repo_by_repo(self):
        '''[TCMS#191137 setup] Add rh repo '''
        RHUIManagerRepo.add_rh_repo_by_repo(self.rs.RHUA, ["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])

    def test_07_associate_repo_cds(self):
        '''[TCMS#191137 setup] Associate repos with cluster '''
        RHUIManagerCds.associate_repo_cds(self.rs.RHUA, "Cluster1", ["repo1", "Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])

    def test_08_upload_rh_rpm(self):
        '''[TCMS#191137 setup] Upload rh rpm to custom repo '''
        self.rs.RHUA.sftp.put(self.rhrpm, "/root/" + self.rhrpmnvr)
        RHUIManagerRepo.upload_content(self.rs.RHUA, ["repo1"], "/root/" + self.rhrpmnvr)

    def test_09_upload_signed_rpm(self):
        '''[TCMS#191137 setup] Upload signed rpm to custom repo '''
        self.rs.RHUA.sftp.put("/usr/share/rhui-testing-tools/testing-data/custom-signed-rpm-1-0.1.fc17.noarch.rpm", "/root/custom-signed-rpm-1-0.1.fc17.noarch.rpm")
        RHUIManagerRepo.upload_content(self.rs.RHUA, ["repo1"], "/root/custom-signed-rpm-1-0.1.fc17.noarch.rpm")

    def test_10_upload_unsigned_rpm(self):
        '''[TCMS#191137 setup] Upload unsigned rpm to custom repo '''
        self.rs.RHUA.sftp.put("/usr/share/rhui-testing-tools/testing-data/custom-unsigned-rpm-1-0.1.fc17.noarch.rpm", "/root/custom-unsigned-rpm-1-0.1.fc17.noarch.rpm")
        RHUIManagerRepo.upload_content(self.rs.RHUA, ["repo1"], "/root/custom-unsigned-rpm-1-0.1.fc17.noarch.rpm")

    def test_11_sync_repo(self):
        '''[TCMS#191137 setup] Sync RH repo '''
        RHUIManagerSync.sync_repo(self.rs.RHUA, ["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])
        reposync = ["In Progress", "", ""]
        while reposync[0] == "In Progress":
            time.sleep(10)
            reposync = RHUIManagerSync.get_repo_status(self.rs.RHUA, "Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)")
        nose.tools.assert_equal(reposync[2], "Success")

    def test_12_sync_cds(self):
        '''[TCMS#191137 setup] Sync cds '''
        RHUIManagerSync.sync_cds(self.rs.RHUA, [self.rs.CDS[0].hostname])
        cdssync = ["UP", "In Progress", "", ""]
        while cdssync[1] == "In Progress":
            time.sleep(10)
            cdssync = RHUIManagerSync.get_cds_status(self.rs.RHUA, self.rs.CDS[0].hostname)
        nose.tools.assert_equal(cdssync[3], "Success")

    def test_13_generate_ent_cert(self):
        '''[TCMS#191137 setup] Generate entitlement certificate '''
        RHUIManagerClient.generate_ent_cert(self.rs.RHUA, "Cluster1", ["Red Hat Update Infrastructure 2 \(RPMs\)"], "cert-repo1", "/root/", validity_days="", cert_pw=None)

    def test_14_create_conf_rpm(self):
        '''[TCMS#191137 setup] Create configuration rpm '''
        RHUIManagerClient.create_conf_rpm(self.rs.RHUA, "Cluster1", self.rs.CDS[0].hostname, "/root", "/root/cert-repo1.crt", "/root/cert-repo1.key", "repo1", "3.0", ["repo1"])

    def test_15_install_conf_rpm_client(self):
        '''[TCMS#191137 setup] Install configuration rpm to client '''
        self.rs.RHUA.sftp.get("/root/repo1-3.0/build/RPMS/noarch/repo1-3.0-1.noarch.rpm", "/root/repo1-3.0-1.noarch.rpm")
        Util.install_rpm_from_master(self.rs.CLI[0], "/root/repo1-3.0-1.noarch.rpm")

    def test_16_rh_rpm_install(self):
        '''[TCMS#191137 test] Installing RH rpm from RH repo to the client '''
        Expect.ping_pong(self.rs.CLI[0], "yum install -y pymongo && echo SUCCESS", "[^ ]SUCCESS", 60)

    def test_17_rh_rpm_install(self):
        '''[TCMS#191137 test] Installing RH rpm from custom repo to the client '''
        Expect.ping_pong(self.rs.CLI[0], "yum install -y " + self.rhrpmname + " && echo SUCCESS", "[^ ]SUCCESS", 60)

    def test_18_signed_rpm_install(self):
        '''[TCMS#191137 test] Installing signed rpm from custom repo to the client '''
        Expect.ping_pong(self.rs.CLI[0], "yum install -y custom-signed-rpm && echo SUCCESS", "[^ ]SUCCESS", 60)

    def test_19_unsigned_rpm_install(self):
        '''[TCMS#191137 test] Trying to install unsigned rpm from custom repo to the client '''
        Expect.ping_pong(self.rs.CLI[0], "yum install -y custom-unsigned-rpm || echo FAILURE", "[^ ]FAILURE", 60)

    def test_20_rh_rpm_remove(self):
        '''[TCMS#191137 cleanup] Removing RH rpm from RH repo from the client '''
        Expect.ping_pong(self.rs.CLI[0], "rpm -e pymongo && echo SUCCESS", "[^ ]SUCCESS", 60)

    def test_21_rh_rpm_remove(self):
        '''[TCMS#191137 cleanup] Removing RH rpm from custom repo from the client '''
        Expect.ping_pong(self.rs.CLI[0], "rpm -e " + self.rhrpmname + " && echo SUCCESS", "[^ ]SUCCESS", 60)

    def test_22_signed_rpm_remove(self):
        '''[TCMS#191137 cleanup] Removing signed rpm from the client '''
        Expect.ping_pong(self.rs.CLI[0], "rpm -e custom-signed-rpm && echo SUCCESS", "[^ ]SUCCESS", 60)

    def test_23_remove_cds(self):
        '''[TCMS#191137 cleanup] Remove cds '''
        RHUIManagerCds.delete_cds(self.rs.RHUA, "Cluster1", [self.rs.CDS[0].hostname])

    def test_24_delete_custom_repo(self):
        '''[TCMS#191137 cleanup] Delete custom repo '''
        RHUIManagerRepo.delete_repo(self.rs.RHUA, ["repo1"])

    def test_25_delete_rh_repo(self):
        '''[TCMS#191137 cleanup] Delete RH repo '''
        RHUIManagerRepo.delete_repo(self.rs.RHUA, ["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])

    def test_26_delete_rh_cert(self):
        '''[TCMS#191137 cleanup] Remove RH certs from RHUI '''
        RHUIManager.remove_rh_certs(self.rs.RHUA)


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
