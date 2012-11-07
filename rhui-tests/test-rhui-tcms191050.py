#! /usr/bin/python -tt

import nose

from rhuilib.util import *
from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_cds import *
from rhuilib.rhuimanager_client import *
from rhuilib.rhuimanager_repo import *
from rhuilib.rhuimanager_sync import *


class test_tcms_191050(RHUITestcase):
    def __init__(self):
        RHUITestcase.__init__()
        if not 'rhrpm' in self.rs.config.keys():
            raise nose.exc.SkipTest("can't test without RH-signed RPM")
        self.rhrpm = self.rs.config['rhrpm']
        (self.rhrpmnvr, self.rhrpmname) = Util.get_rpm_details(self.rhrpm)

    def test_01_initial_run(self):
        '''[TCMS#191050 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.RHUA)

    def test_02_add_cds(self):
        '''[TCMS#191050 setup] Add cds '''
        RHUIManagerCds.add_cds(self.rs.RHUA, "Cluster1", self.rs.CDS[0].hostname)

    def test_03_cli_remove_conf_rpm(self):
        '''[TCMS#191050 setup] Remove rhui configuration rpm from client '''
        for cli in self.rs.CLI:
            Util.remove_conf_rpm(cli)

    def test_04_add_custom_repos(self):
        '''[TCMS#191050 setup] Create custom repo '''
        self.rs.RHUA.sftp.put("/usr/share/rhui-testing-tools/testing-data/public.key", "/root/public.key")
        RHUIManagerRepo.add_custom_repo(self.rs.RHUA, "repo1", redhat_gpg="n")

    def test_05_associate_repo_cds(self):
        '''[TCMS#191050 setup] Associate custom repo with cluster '''
        RHUIManagerCds.associate_repo_cds(self.rs.RHUA, "Cluster1", ["repo1"])

    def test_06_upload_rh_rpm(self):
        '''[TCMS#191050 setup] Upload rh rpm to custom repo '''
        self.rs.RHUA.sftp.put(self.rhrpm, "/root/" + self.rhrpmnvr)
        RHUIManagerRepo.upload_content(self.rs.RHUA, ["repo1"], "/root/" + self.rhrpmnvr)

    def test_07_upload_signed_rpm(self):
        '''[TCMS#191050 setup] Upload signed rpm to custom repo '''
        self.rs.RHUA.sftp.put("/usr/share/rhui-testing-tools/testing-data/custom-signed-rpm-1-0.1.fc17.noarch.rpm", "/root/custom-signed-rpm-1-0.1.fc17.noarch.rpm")
        RHUIManagerRepo.upload_content(self.rs.RHUA, ["repo1"], "/root/custom-signed-rpm-1-0.1.fc17.noarch.rpm")

    def test_08_upload_unsigned_rpm(self):
        '''[TCMS#191050 setup] Upload unsigned rpm to custom repo '''
        self.rs.RHUA.sftp.put("/usr/share/rhui-testing-tools/testing-data/custom-unsigned-rpm-1-0.1.fc17.noarch.rpm", "/root/custom-unsigned-rpm-1-0.1.fc17.noarch.rpm")
        RHUIManagerRepo.upload_content(self.rs.RHUA, ["repo1"], "/root/custom-unsigned-rpm-1-0.1.fc17.noarch.rpm")

    def test_09_sync_cluster(self):
        '''[TCMS#191050 setup] Sync cluster '''
        RHUIManagerSync.sync_cluster(self.rs.RHUA, ["Cluster1"])

    def test_10_generate_ent_cert(self):
        '''[TCMS#191050 setup] Generate entitlement certificate '''
        RHUIManagerClient.generate_ent_cert(self.rs.RHUA, "Cluster1", ["repo1"], "cert-repo1", "/root/", validity_days="", cert_pw=None)

    def test_11_create_conf_rpm(self):
        '''[TCMS#191050 setup] Create configuration rpm '''
        RHUIManagerClient.create_conf_rpm(self.rs.RHUA, "Cluster1", self.rs.CDS[0].hostname, "/root", "/root/cert-repo1.crt", "/root/cert-repo1.key", "repo1", "3.0")

    def test_12_install_conf_rpm_client(self):
        '''[TCMS#191050 setup] Install configuration rpm to client '''
        self.rs.RHUA.sftp.get("/root/repo1-3.0/build/RPMS/noarch/repo1-3.0-1.noarch.rpm", "/root/repo1-3.0-1.noarch.rpm")
        Util.install_rpm_from_master(self.rs.CLI[0], "/root/repo1-3.0-1.noarch.rpm")

    def test_13_rh_rpm_install(self):
        '''[TCMS#191050 setup] Installing RH rpm to the client '''
        if not self.rhrpmname:
            raise nose.exc.SkipTest("can't test without RH rpm")
        Expect.ping_pong(self. rs.CLI[0], "yum install -y --nogpgcheck " + self.rhrpmname + " && echo SUCCESS", "[^ ]SUCCESS", 60)

    def test_14_signed_rpm_install(self):
        '''[TCMS#191050 test] Installing signed rpm to the client '''
        Expect.ping_pong(self. rs.CLI[0], "yum install -y --nogpgcheck custom-signed-rpm && echo SUCCESS", "[^ ]SUCCESS", 60)

    def test_15_unsigned_rpm_install(self):
        '''[TCMS#191050 test] Installing unsigned rpm to the client '''
        Expect.ping_pong(self. rs.CLI[0], "yum install -y --nogpgcheck custom-unsigned-rpm && echo SUCCESS", "[^ ]SUCCESS", 60)

    def test_16_rh_rpm_remove(self):
        '''[TCMS#191050 test] Removing RH rpm from the client '''
        if not self.rhrpmname:
            raise nose.exc.SkipTest("can't test without RH rpm")
        Expect.ping_pong(self. rs.CLI[0], "rpm -e " + self.rhrpmname + " && echo SUCCESS", "[^ ]SUCCESS", 60)

    def test_17_signed_rpm_remove(self):
        '''[TCMS#191050 cleanup] Removing signed rpm from the client '''
        Expect.ping_pong(self. rs.CLI[0], "rpm -e custom-signed-rpm && echo SUCCESS", "[^ ]SUCCESS", 60)

    def test_18_unsigned_rpm_remove(self):
        '''[TCMS#191050 cleanup] Removing unsigned rpm from the client '''
        Expect.ping_pong(self. rs.CLI[0], "rpm -e custom-unsigned-rpm && echo SUCCESS", "[^ ]SUCCESS", 60)

    def test_19_remove_cds(self):
        '''[TCMS#191050 cleanup] Remove cds '''
        RHUIManagerCds.delete_cds(self.rs.RHUA, "Cluster1", [self.rs.CDS[0].hostname])

    def test_20_delete_custom_repo(self):
        '''[TCMS#191050 cleanup] Delete custom repo '''
        RHUIManagerRepo.delete_repo(self.rs.RHUA, ["repo1"])


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
