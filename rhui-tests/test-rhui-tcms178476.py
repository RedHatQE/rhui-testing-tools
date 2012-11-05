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


class test_tcms_178476(object):
    def __init__(self):
        argparser = argparse.ArgumentParser(description='RHUI TCMS testcase test-rhui-178476')
        args = argparser.parse_args()
        self.rs = RHUIsetup()
        self.rs.setup_from_rolesfile()
        if len(self.rs.CDS) < 2:
            raise nose.exc.SkipTest("can't test without having at least two CDSes!")

    def __del__(self):
        self.rs.__del__()

    def test_01_initial_run(self):
        ''' Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.RHUA)

    def test_02_add_cds(self):
        ''' Add cdses '''
        RHUIManagerCds.add_cds(self.rs.RHUA, "Cluster1", self.rs.CDS[0].hostname)
        RHUIManagerCds.add_cds(self.rs.RHUA, "Cluster1", self.rs.CDS[1].hostname)

    def test_03_cli_remove_conf_rpm(self):
        ''' Remove rhui configuration rpm from client '''
        for cli in self.rs.CLI:
            Util.remove_conf_rpm(cli)

    def test_04_add_custom_repos(self):
        ''' Create custom repo '''
        RHUIManagerRepo.add_custom_repo(self.rs.RHUA, "repo1")

    def test_05_associate_repo_cds(self):
        ''' Associate custom repo with cluster '''
        RHUIManagerCds.associate_repo_cds(self.rs.RHUA, "Cluster1", ["repo1"])

    def test_06_upload_content(self):
        ''' Upload content to custom repo '''
        RHUIManagerRepo.upload_content(self.rs.RHUA, ["repo1"], "/etc/rhui/confrpm")

    def test_07_sync_cluster(self):
        ''' Sync cluster '''
        RHUIManagerSync.sync_cluster(self.rs.RHUA, ["Cluster1"])

    def test_08_generate_ent_cert(self):
        ''' Generate entitlement certificate '''
        RHUIManagerClient.generate_ent_cert(self.rs.RHUA, "Cluster1", ["repo1"], "cert-repo1", "/root/", validity_days="", cert_pw=None)

    def test_09_create_conf_rpm(self):
        ''' Create configuration rpm '''
        RHUIManagerClient.create_conf_rpm(self.rs.RHUA, "Cluster1", self.rs.CDS[0].hostname, "/root", "/root/cert-repo1.crt", "/root/cert-repo1.key", "repo1", "3.0")

    def test_10_install_conf_rpm_client(self):
        ''' Install configuration rpm to client '''
        self.rs.RHUA.sftp.get("/root/repo1-3.0/build/RPMS/noarch/repo1-3.0-1.noarch.rpm", "/root/repo1-3.0-1.noarch.rpm")
        Util.install_rpm_from_master(self.rs.CLI[0], "/root/repo1-3.0-1.noarch.rpm")

    def test_11_cli_2cds(self):
        ''' Test client with 2 cdses up '''
        Expect.ping_pong(self. rs.CLI[0], "yum clean metadata && yum check-update && echo SUCCESS", "[^ ]SUCCESS")

    def test_12_cli_1cds_slave(self):
        ''' Test client with only slave cds up '''
        # disabling httpd on master
        Expect.ping_pong(self.rs.CDS[0], "service httpd stop && echo SUCCESS", "[^ ]SUCCESS")
        Expect.ping_pong(self.rs.CLI[0], "yum clean metadata && yum check-update && echo SUCCESS", "[^ ]SUCCESS")

    def test_13_cli_1cds_master(self):
        ''' Test client with only master cds up '''
        # enabling httpd on master, disabling on slave
        Expect.ping_pong(self.rs.CDS[0], "service httpd start && echo SUCCESS", "[^ ]SUCCESS")
        Expect.ping_pong(self.rs.CDS[1], "service httpd stop && echo SUCCESS", "[^ ]SUCCESS")
        Expect.ping_pong(self.rs.CLI[0], "yum clean metadata && yum check-update && echo SUCCESS", "[^ ]SUCCESS")

    def test_14_recover(self):
        ''' Recover from tests '''
        # enabling httpd on slave
        Expect.ping_pong(self.rs.CDS[1], "service httpd start && echo SUCCESS", "[^ ]SUCCESS")

    def test_15_remove_cds(self):
        ''' Remove cdses '''
        RHUIManagerCds.delete_cds(self.rs.RHUA, "Cluster1", [self.rs.CDS[0].hostname, self.rs.CDS[1].hostname])

    def test_16_delete_custom_repo(self):
        ''' Delete custom repos '''
        RHUIManagerRepo.delete_repo(self.rs.RHUA, ["repo1"])


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
