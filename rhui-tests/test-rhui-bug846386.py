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
from rhuilib.rhuimanager_identity import *
from rhuilib.rhuimanager_users import *
from rhuilib.rhuimanager_entitlements import *

class test_bug_846386:
    def __init__(self):
        argparser = argparse.ArgumentParser(description='RHUI bug 846386')
        args = argparser.parse_args()
        self.rs = RHUIsetup()
        self.rs.setup_from_rolesfile()
        
    def test_01_initial_run(self):
        RHUIManager.initial_run(self.rs.RHUA)

    def test_02_add_cds(self):
        RHUIManagerCds.add_cds(self.rs.RHUA, "Cluster1", self.rs.CDS[0].hostname)

    def test_03_add_protected_repo(self):
        RHUIManagerRepo.add_custom_repo(self.rs.RHUA, "custom_repo_1")

    def test_04_add_unprotected_repo(self):
        RHUIManagerRepo.add_custom_repo(self.rs.RHUA, "custom_repo_2", entitlement="n")

    def test_05_upload_content(self):
        RHUIManagerRepo.upload_content(self.rs.RHUA, ["custom_repo_2"], "/etc/rhui/confrpm")

    def test_06_associate_repo_cds(self):
        RHUIManagerCds.associate_repo_cds(self.rs.RHUA, "Cluster1", ["custom_repo_1", "custom_repo_2"])

    def test_07_generate_ent_cert(self):
        RHUIManagerClient.generate_ent_cert(self.rs.RHUA, "Cluster1", ["custom_repo_1"], "cert-repo1", "/root/", validity_days="", cert_pw=None)

    def test_08_create_conf_rpm(self):
        RHUIManagerClient.create_conf_rpm(self.rs.RHUA, "Cluster1", self.rs.CDS[0].hostname, "/root", "/root/cert-repo1.crt", "/root/cert-repo1.key", "repo1", "3.0", ["custom_repo_2"])

if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
