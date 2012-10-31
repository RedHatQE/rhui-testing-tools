#! /usr/bin/python -tt

import argparse
import nose
import re
import os
import logging
import time

from rhuilib.util import *
from rhuilib.rhuisetup import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_cds import *
from rhuilib.rhuimanager_client import *
from rhuilib.rhuimanager_repo import *
from rhuilib.rhuimanager_sync import *
from rhuilib.rhuimanager_identity import *
from rhuilib.rhuimanager_users import *
from rhuilib.rhuimanager_entitlements import *


class test_tcms_191137(object):
    def __init__(self):
        argparser = argparse.ArgumentParser(description='RHUI TCMS testcase test-rhui-191137')
        argparser.add_argument('--rhrpm',
                               help='use supplied RH rpm for tests')
        argparser.add_argument('--cert',
                               help='use supplied RH enablement certificate')
        args = argparser.parse_args()
        self.cert = args.cert
        if not self.cert:
            raise nose.exc.SkipTest("can't test without RH certificate")
        self.rhrpm = args.rhrpm
        self.rs = RHUIsetup()
        self.rs.setup_from_rolesfile()
        if self.rhrpm:
            self.rhrpmnvr = os.popen("basename " + self.rhrpm).read()[:-1]
            logging.debug("RHRPMNVR: " + self.rhrpmnvr)
            self.rs.RHUA.sftp.put(self.rhrpm, "/root/" + self.rhrpmnvr)
            Expect.enter(self. rs.RHUA, "rpm -qp --queryformat '###%{NAME}###' /root/" + self.rhrpmnvr)
            self.rhrpmname = Expect.match(self.rs.RHUA, re.compile(".*###([^\n]*)###.*", re.DOTALL))[0]
            logging.debug("RHRPMNAME: " + self.rhrpmnvr)
        else:
            self.rhrpmname = None

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
        RHUIManagerRepo.add_custom_repo(self.rs.RHUA, "repo1", entitlement="n", custom_gpg="/root/public.key")

    def test_05_upload_content_cert(self):
        ''' Upload RH content certificate '''
        RHUIManagerEntitlements.upload_content_cert(self.rs.RHUA, self.cert)

    def test_06_add_rh_repo_by_product(self):
        ''' Add rh repo '''
        RHUIManagerRepo.add_rh_repo_by_repo(self.rs.RHUA, ["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])

    def test_07_associate_repo_cds(self):
        ''' Associate repos with cluster '''
        RHUIManagerCds.associate_repo_cds(self.rs.RHUA, "Cluster1", ["repo1", "Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])

    def test_08_upload_rh_rpm(self):
        ''' Upload rh rpm to custom repo '''
        if not self.rhrpm:
            raise nose.exc.SkipTest("can't test without RH rpm")
        RHUIManagerRepo.upload_content(self.rs.RHUA, ["repo1"], "/root/" + self.rhrpmnvr)

    def test_09_upload_signed_rpm(self):
        ''' Upload signed rpm to custom repo '''
        self.rs.RHUA.sftp.put("/usr/share/rhui-testing-tools/testing-data/custom-signed-rpm-1-0.1.fc17.noarch.rpm", "/root/custom-signed-rpm-1-0.1.fc17.noarch.rpm")
        RHUIManagerRepo.upload_content(self.rs.RHUA, ["repo1"], "/root/custom-signed-rpm-1-0.1.fc17.noarch.rpm")

    def test_10_upload_unsigned_rpm(self):
        ''' Upload unsigned rpm to custom repo '''
        self.rs.RHUA.sftp.put("/usr/share/rhui-testing-tools/testing-data/custom-unsigned-rpm-1-0.1.fc17.noarch.rpm", "/root/custom-unsigned-rpm-1-0.1.fc17.noarch.rpm")
        RHUIManagerRepo.upload_content(self.rs.RHUA, ["repo1"], "/root/custom-unsigned-rpm-1-0.1.fc17.noarch.rpm")

    def test_11_sync_repo(self):
        ''' Sync RH repo '''
        RHUIManagerSync.sync_repo(self.rs.RHUA, ["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])
        reposync = ["In Progress", "", ""]
        while reposync[0] == "In Progress":
            time.sleep(10)
            reposync = RHUIManagerSync.get_repo_status(self.rs.RHUA, "Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)")
        nose.tools.assert_equal(reposync[2], "Success")

    def test_12_sync_cds(self):
        ''' Sync cds '''
        RHUIManagerSync.sync_cds(self.rs.RHUA, [self.rs.CDS[0].hostname])
        cdssync = ["UP", "In Progress", "", ""]
        while cdssync[1] == "In Progress":
            time.sleep(10)
            cdssync = RHUIManagerSync.get_cds_status(self.rs.RHUA, self.rs.CDS[0].hostname)
        nose.tools.assert_equal(cdssync[3], "Success")

    def test_13_generate_ent_cert(self):
        ''' Generate entitlement certificate '''
        RHUIManagerClient.generate_ent_cert(self.rs.RHUA, "Cluster1", ["Red Hat Update Infrastructure 2 \(RPMs\)"], "cert-repo1", "/root/", validity_days="", cert_pw=None)

    def test_14_create_conf_rpm(self):
        ''' Create configuration rpm '''
        RHUIManagerClient.create_conf_rpm(self.rs.RHUA, "Cluster1", self.rs.CDS[0].hostname, "/root", "/root/cert-repo1.crt", "/root/cert-repo1.key", "repo1", "3.0", ["repo1"])

    def test_15_install_conf_rpm_client(self):
        ''' Install configuration rpm to client '''
        self.rs.RHUA.sftp.get("/root/repo1-3.0/build/RPMS/noarch/repo1-3.0-1.noarch.rpm", "/root/repo1-3.0-1.noarch.rpm")
        Util.install_rpm_from_master(self.rs.CLI[0], "/root/repo1-3.0-1.noarch.rpm")

    def test_16_rh_rpm_install(self):
        ''' Installing RH rpm from RH repo to the client '''
        Expect.enter(self. rs.CLI[0], "yum install -y pymongo && echo SUCCESS")
        Expect.expect(self. rs.CLI[0], "[^ ]SUCCESS", 60)

    def test_17_rh_rpm_install(self):
        ''' Installing RH rpm from custom repo to the client '''
        if not self.rhrpmname:
            raise nose.exc.SkipTest("can't test without RH rpm")
        Expect.enter(self. rs.CLI[0], "yum install -y " + self.rhrpmname + " && echo SUCCESS")
        Expect.expect(self. rs.CLI[0], "[^ ]SUCCESS", 60)

    def test_18_signed_rpm_install(self):
        ''' Installing signed rpm from custom repo to the client '''
        Expect.enter(self. rs.CLI[0], "yum install -y custom-signed-rpm && echo SUCCESS")
        Expect.expect(self. rs.CLI[0], "[^ ]SUCCESS", 60)

    def test_19_unsigned_rpm_install(self):
        ''' Trying to install unsigned rpm from custom repo to the client '''
        Expect.enter(self. rs.CLI[0], "yum install -y custom-unsigned-rpm || echo FAILURE")
        Expect.expect(self. rs.CLI[0], "[^ ]FAILURE", 60)

    def test_20_rh_rpm_remove(self):
        ''' Removing RH rpm from RH repo from the client '''
        Expect.enter(self. rs.CLI[0], "rpm -e pymongo && echo SUCCESS")
        Expect.expect(self. rs.CLI[0], "[^ ]SUCCESS", 60)

    def test_21_rh_rpm_remove(self):
        ''' Removing RH rpm from custom repo from the client '''
        if not self.rhrpmname:
            raise nose.exc.SkipTest("can't test without RH rpm")
        Expect.enter(self. rs.CLI[0], "rpm -e " + self.rhrpmname + " && echo SUCCESS")
        Expect.expect(self. rs.CLI[0], "[^ ]SUCCESS", 60)

    def test_22_signed_rpm_remove(self):
        ''' Removing signed rpm from the client '''
        Expect.enter(self. rs.CLI[0], "rpm -e custom-signed-rpm && echo SUCCESS")
        Expect.expect(self. rs.CLI[0], "[^ ]SUCCESS", 60)

    def test_23_remove_cds(self):
        ''' Remove cds '''
        RHUIManagerCds.delete_cds(self.rs.RHUA, "Cluster1", [self.rs.CDS[0].hostname])

    def test_24_delete_custom_repo(self):
        ''' Delete custom repo '''
        RHUIManagerRepo.delete_repo(self.rs.RHUA, ["repo1"])

    def test_25_delete_rh_repo(self):
        ''' Delete RH repo '''
        RHUIManagerRepo.delete_repo(self.rs.RHUA, ["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
