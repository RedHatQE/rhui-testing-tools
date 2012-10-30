#! /usr/bin/python -tt

import logging
import argparse
import nose

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

class test_simple_workflow:
    def __init__(self):
        argparser = argparse.ArgumentParser(description='RHUI simple workflow')
        argparser.add_argument('--cert',
                               help='use supplied RH enablement certificate')
        args = argparser.parse_args()
        self.cert = args.cert
        self.rs = RHUIsetup()
        self.rs.setup_from_rolesfile()
        
    def test_01_initial_run(self):
        ''' Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.RHUA)

    def test_02_add_cds(self):
        ''' Add cdses '''
        for cds in self.rs.CDS:
            RHUIManagerCds.add_cds(self.rs.RHUA, "Cluster1", cds.hostname)

    def test_03_cli_remove_conf_rpm(self):
        ''' Remove rhui configuration rpm from client '''
        for cli in self.rs.CLI:
            Util.remove_conf_rpm(cli)

    def test_03_add_custom_repos(self):
        ''' Create custom repo '''
        RHUIManagerRepo.add_custom_repo(self.rs.RHUA, "repo1")
        RHUIManagerRepo.add_custom_repo(self.rs.RHUA, "repo2")

    def test_04_associate_repo_cds(self):
        ''' Associate custom repo with cluster '''
        RHUIManagerCds.associate_repo_cds(self.rs.RHUA, "Cluster1", ["repo1", "repo2"])

    def test_05_upload_content(self):
        ''' Upload content to custom repo '''
        RHUIManagerRepo.upload_content(self.rs.RHUA, ["repo1", "repo2"], "/etc/rhui/confrpm")

    def test_06_sync_cds(self):
        ''' Sync cdses '''
        cdslist = []
        for cds in self.rs.CDS:
            cdslist.append(cds.hostname)
        RHUIManagerSync.sync_cds(self.rs.RHUA, cdslist)

    def test_07_generate_ent_cert(self):
        ''' Generate entitlement certificate '''
        RHUIManagerClient.generate_ent_cert(self.rs.RHUA, "Cluster1", ["repo1"], "cert-repo1", "/root/", validity_days="", cert_pw=None)

    def test_08_sync_cluster(self):
        ''' Sync cluster '''
        ##it's impossible to do cluster sync and individual cds sync at the same moment
        ##RHUIManagerSync.sync_cluster(self.rs.RHUA,["Cluster1"])
        pass
    
    def test_09_upload_content_cert(self):
        ''' Upload RH content certificate '''
        if not self.cert:
            raise nose.exc.SkipTest("can't test without RH content cert")
        RHUIManagerEntitlements.upload_content_cert(self.rs.RHUA, self.cert)

    def test_10_add_rh_repo_by_product(self):
        ''' Add rh repo by product '''
        if not self.cert:
            raise nose.exc.SkipTest("can't test without RH content cert")
        RHUIManagerRepo.add_rh_repo_by_product(self.rs.RHUA, ["Red Hat Enterprise Linux 6 Server - Supplementary from RHUI \(RPMs\)", "Red Hat Enterprise Linux 6 Server from RHUI \(RPMs\)"])

    def test_11_add_rh_repo_by_repo(self):
        ''' Add rh repo by repo '''
        if not self.cert:
            raise nose.exc.SkipTest("can't test without RH content cert")
        RHUIManagerRepo.add_rh_repo_by_repo(self.rs.RHUA, ["Red Hat Enterprise Linux 5 Server from RHUI \(RPMs\) \(5Server-i386\)", "Red Hat Enterprise Linux 5 Server from RHUI \(RPMs\) \(5Server-x86_64\)"])

    def test_12_add_rh_repo_all(self):
        ''' Add all rh products '''
        if not self.cert:
            raise nose.exc.SkipTest("can't test without RH content cert")
        RHUIManagerRepo.add_rh_repo_all(self.rs.RHUA)

    def test_13_sync_repo(self):
        ''' Syncronize repo '''
        if not self.cert:
            raise nose.exc.SkipTest("can't test without RH content cert")
        RHUIManagerSync.sync_repo(self.rs.RHUA, ["Red Hat Enterprise Linux 5 Server from RHUI \(RPMs\) \(5Server-i386\)", "Red Hat Enterprise Linux 5 Server from RHUI \(RPMs\) \(5Server-x86_64\)", "Red Hat Enterprise Linux 6 Server from RHUI \(RPMs\) \(6Server-x86_64\)"])

    def test_14_associate_rh_repo_cds(self):
        ''' Associate rh repo with cds '''
        if not self.cert:
            raise nose.exc.SkipTest("can't test without RH content cert")
        RHUIManagerCds.associate_repo_cds(self.rs.RHUA, "Cluster1", ["Red Hat Enterprise Linux 6 Server from RHUI \(RPMs\) \(6Server-x86_64\)"])

    def test_15_generate_ent_cert_with_rh_content(self):
        ''' Generate entitlement certificate with rh content '''
        if not self.cert:
            raise nose.exc.SkipTest("can't test without RH content cert")
        RHUIManagerClient.generate_ent_cert(self.rs.RHUA, "Cluster1", ["repo1", "Red Hat Enterprise Linux 6 Server from RHUI \(RPMs\)"], "cert-repo1", "/root/", validity_days="", cert_pw=None)

    def test_16_create_conf_rpm(self):
        ''' Create configuration rpm '''
        RHUIManagerClient.create_conf_rpm(self.rs.RHUA, "Cluster1", self.rs.CDS[0].hostname, "/root", "/root/cert-repo1.crt", "/root/cert-repo1.key", "repo1", "3.0")

    def test_17_install_conf_rpm_client(self):
        ''' Install configuration rpm to client'''
        self.rs.RHUA.sftp.get("/root/repo1-3.0/build/RPMS/noarch/repo1-3.0-1.noarch.rpm", "/root/repo1-3.0-1.noarch.rpm")
        Util.install_rpm_from_master(self.rs.CLI[0], "/root/repo1-3.0-1.noarch.rpm")

    def test_18_generate_new_identity(self):
        ''' Generate new identity '''
        RHUIManagerIdentity.generate_new(self.rs.RHUA)

    def test_19_change_password(self):
        ''' Change password '''
        RHUIManagerUsers.change_password(self.rs.RHUA, "admin", "admin2")
        RHUIManagerUsers.change_password(self.rs.RHUA, "admin", "admin")

    def test_20_remove_cds(self):
        ''' Remove cdses '''
        for cds in self.rs.CDS:
            RHUIManagerCds.delete_cds(self.rs.RHUA, "Cluster1", [cds.hostname])

    def test_21_delete_custom_repo(self):
        ''' Delete custom repos '''
        RHUIManagerRepo.delete_repo(self.rs.RHUA, ["repo1", "repo2"])

if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
