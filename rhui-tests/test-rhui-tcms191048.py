#! /usr/bin/python -tt

import argparse
import nose

from rhuilib.util import *
from rhuilib.rhuisetup import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_cds import *
from rhuilib.rhuimanager_client import *
from rhuilib.rhuimanager_repo import *
from rhuilib.rhuimanager_sync import *
from rhuilib.rhuimanager_entitlements import *


class test_tcms_191048(object):
    def __init__(self):
        argparser = argparse.ArgumentParser(description='RHUI TCMS testcase test-rhui-191048')
        argparser.add_argument('--rhrpm',
                               help='use supplied RH rpm for tests')
        args = argparser.parse_args()
        self.rhrpm = args.rhrpm
        self.rs = RHUIsetup()
        self.rs.setup_from_rolesfile()
        (self.rhrpmnvr, self.rhrpmname) = Util.get_rpm_details(self.rhrpm)

    def __del__(self):
        self.rs.__del__()

    def test_01_initial_run(self):
        ''' Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.RHUA)

    def test_02_add_cds(self):
        ''' Add cds '''
        RHUIManagerCds.add_cds(self.rs.RHUA, "Cluster1", self.rs.CDS[0].hostname)

    def test_03_cli_remove_conf_rpm(self):
        ''' Remove rhui configuration rpm from client '''
        for cli in self.rs.CLI:
            Util.remove_conf_rpm(cli)

    def test_04_add_custom_repos(self):
        ''' Create custom repo '''
        self.rs.RHUA.sftp.put("/usr/share/rhui-testing-tools/testing-data/public.key", "/root/public.key")
        RHUIManagerRepo.add_custom_repo(self.rs.RHUA, "repo1", redhat_gpg="n", custom_gpg="/root/public.key")

    def test_05_associate_repo_cds(self):
        ''' Associate custom repo with cluster '''
        RHUIManagerCds.associate_repo_cds(self.rs.RHUA, "Cluster1", ["repo1"])

    def test_06_upload_rh_rpm(self):
        ''' Upload rh rpm to custom repo '''
        if not self.rhrpm:
            raise nose.exc.SkipTest("can't test without RH rpm")

        self.rs.RHUA.sftp.put(self.rhrpm, "/root/" + self.rhrpmnvr)
        RHUIManagerRepo.upload_content(self.rs.RHUA, ["repo1"], "/root/" + self.rhrpmnvr)

    def test_07_upload_signed_rpm(self):
        ''' Upload signed rpm to custom repo '''
        self.rs.RHUA.sftp.put("/usr/share/rhui-testing-tools/testing-data/custom-signed-rpm-1-0.1.fc17.noarch.rpm", "/root/custom-signed-rpm-1-0.1.fc17.noarch.rpm")
        RHUIManagerRepo.upload_content(self.rs.RHUA, ["repo1"], "/root/custom-signed-rpm-1-0.1.fc17.noarch.rpm")

    def test_08_upload_unsigned_rpm(self):
        ''' Upload unsigned rpm to custom repo '''
        self.rs.RHUA.sftp.put("/usr/share/rhui-testing-tools/testing-data/custom-unsigned-rpm-1-0.1.fc17.noarch.rpm", "/root/custom-unsigned-rpm-1-0.1.fc17.noarch.rpm")
        RHUIManagerRepo.upload_content(self.rs.RHUA, ["repo1"], "/root/custom-unsigned-rpm-1-0.1.fc17.noarch.rpm")

    def test_09_sync_cds(self):
        ''' Sync cds '''
        RHUIManagerSync.sync_cds(self.rs.RHUA, [self.rs.CDS[0].hostname])
        cdssync = ["UP", "In Progress", "", ""]
        while cdssync[1] == "In Progress":
            time.sleep(10)
            cdssync = RHUIManagerSync.get_cds_status(self.rs.RHUA, self.rs.CDS[0].hostname)
        nose.tools.assert_equal(cdssync[3], "Success")

    def test_10_generate_ent_cert(self):
        ''' Generate entitlement certificate '''
        RHUIManagerClient.generate_ent_cert(self.rs.RHUA, "Cluster1", ["repo1"], "cert-repo1", "/root/", validity_days="", cert_pw=None)

    def test_11_create_conf_rpm(self):
        ''' Create configuration rpm '''
        RHUIManagerClient.create_conf_rpm(self.rs.RHUA, "Cluster1", self.rs.CDS[0].hostname, "/root", "/root/cert-repo1.crt", "/root/cert-repo1.key", "repo1", "3.0")

    def test_12_install_conf_rpm_client(self):
        ''' Install configuration rpm to client '''
        self.rs.RHUA.sftp.get("/root/repo1-3.0/build/RPMS/noarch/repo1-3.0-1.noarch.rpm", "/root/repo1-3.0-1.noarch.rpm")
        Util.install_rpm_from_master(self.rs.CLI[0], "/root/repo1-3.0-1.noarch.rpm")

    def test_13_check_repo_gpg(self):
        ''' Check RH gpg key in repo file '''
        Expect.enter(self. rs.CLI[0], "grep RPM-GPG-KEY-redhat-release /etc/yum.repos.d/rh-cloud.repo || echo SUCCESS")
        Expect.expect(self. rs.CLI[0], "[^ ]SUCCESS", 60)

    def test_14_signed_rpm_install(self):
        ''' Installing signed rpm to the client '''
        Expect.enter(self. rs.CLI[0], "yum install -y custom-signed-rpm && echo SUCCESS")
        Expect.expect(self. rs.CLI[0], "[^ ]SUCCESS", 60)

    def test_15_unsigned_rpm_install(self):
        ''' Trying to install unsigned rpm to the client '''
        Expect.enter(self. rs.CLI[0], "yum install -y custom-unsigned-rpm || echo FAILURE")
        Expect.expect(self. rs.CLI[0], "[^ ]FAILURE", 60)

    def test_16_signed_rpm_remove(self):
        ''' Removing signed rpm from the client '''
        Expect.enter(self. rs.CLI[0], "rpm -e custom-signed-rpm && echo SUCCESS")
        Expect.expect(self. rs.CLI[0], "[^ ]SUCCESS", 60)

    def test_17_remove_cds(self):
        ''' Remove cds '''
        RHUIManagerCds.delete_cds(self.rs.RHUA, "Cluster1", [self.rs.CDS[0].hostname])

    def test_18_delete_custom_repo(self):
        ''' Delete custom repo '''
        RHUIManagerRepo.delete_repo(self.rs.RHUA, ["repo1"])


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
