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
from rhuilib.cds import RhuiCds


class test_tcms_178470(RHUITestcase, RHUI_has_RH_cert):
    def _setup(self):

        '''[TCMS#178470 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.RHUA)

        '''[TCMS#178470 setup] Add cdses '''
        RHUIManagerCds.add_cds(self.rs.RHUA, "Cluster1", self.rs.CDS[0].private_hostname)

        '''[TCMS#178470 setup] Create custom repo '''
        self.rs.RHUA.sftp.put("/usr/share/rhui-testing-tools/testing-data/public.key", "/root/public.key")
        RHUIManagerRepo.add_custom_repo(self.rs.RHUA, "repo1", entitlement="y", custom_gpg="/root/public.key")

        '''[TCMS#178470 setup] Upload signed rpm to custom repo '''
        self.rs.RHUA.sftp.put("/usr/share/rhui-testing-tools/testing-data/custom-signed-rpm-1-0.1.fc17.noarch.rpm", "/root/custom-signed-rpm-1-0.1.fc17.noarch.rpm")
        RHUIManagerRepo.upload_content(self.rs.RHUA, ["repo1"], "/root/custom-signed-rpm-1-0.1.fc17.noarch.rpm")

        '''[TCMS#178470 setup] Upload RH content certificate '''
        RHUIManagerEntitlements.upload_content_cert(self.rs.RHUA, self.cert)

        '''[TCMS#178470 setup] Add rh repo '''
        RHUIManagerRepo.add_rh_repo_by_repo(self.rs.RHUA, ["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])

        '''[TCMS#178470 setup] Associate repo with cluster '''
        RHUIManagerCds.associate_repo_cds(self.rs.RHUA, "Cluster1", ["repo1", "Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])

        '''[TCMS#178470 setup] Sync RH repo '''
        self._sync_repo(["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])

        '''[TCMS#178470 setup] Sync cds '''
        self._sync_cds([self.rs.CDS[0].private_hostname])

        '''[TCMS#178470 setup] Remove rhui configuration rpm from RHUA '''
        Util.remove_conf_rpm(self.rs.CLI[0])

        '''[TCMS#178470 setup] Generate entitlement certificate '''
        RHUIManagerClient.generate_ent_cert(self.rs.RHUA, "Cluster1", ["repo1", "Red Hat Update Infrastructure 2 \(RPMs\)"], "cert-repo1", "/root/", validity_days="", cert_pw=None)

        '''[TCMS#178470 setup] Create configuration rpm '''
        RHUIManagerClient.create_conf_rpm(self.rs.RHUA, "Cluster1", self.rs.CDS[0].private_hostname, "/root", "/root/cert-repo1.crt", "/root/cert-repo1.key", "repo1", "3.0")

        '''[TCMS#178470 setup] Install configuration rpm to client '''
        Util.install_rpm_from_rhua(self.rs.RHUA, self.rs.CLI[0], "/root/repo1-3.0/build/RPMS/noarch/repo1-3.0-1.noarch.rpm")

    def _test(self):
        '''[TCMS#178470 test] Installing RH rpm from RH repo to the client '''
        Expect.ping_pong(self.rs.CLI[0], "yum install -y pymongo && echo SUCCESS", "[^ ]SUCCESS", 60)

        '''[TCMS#178470 test] Installing RH rpm from RH repo to the client '''
        Expect.ping_pong(self.rs.CLI[0], "yum install -y custom-signed-rpm && echo SUCCESS", "[^ ]SUCCESS", 60)

    def _cleanup(self):
        '''[TCMS#178470 cleanup] Removing RH rpm from the client '''
        Expect.ping_pong(self.rs.CLI[0], "rpm -e pymongo && echo SUCCESS", "[^ ]SUCCESS", 60)

        '''[TCMS#178470 cleanup] Removing custom rpm from the client '''
        Expect.ping_pong(self.rs.CLI[0], "rpm -e custom-signed-rpm && echo SUCCESS", "[^ ]SUCCESS", 60)

        '''[TCMS#178470 cleanup] Removing gpg key from the client '''
        Expect.ping_pong(self. rs.CLI[0], "rpm -e gpg-pubkey-b6963d12-5080038c && echo SUCCESS", "[^ ]SUCCESS", 60)

        '''[TCMS#178470 cleanup] Removing configuration rpm from the client '''
        Util.remove_conf_rpm(self.rs.CLI[0])

        '''[TCMS#178470 cleanup] Remove cdses '''
        RHUIManagerCds.delete_cds(self.rs.RHUA, "Cluster1", [self.rs.CDS[0].private_hostname])

        '''[TCMS#178470 cleanup] Delete repos '''
        RHUIManagerRepo.delete_repo(self.rs.RHUA, ["repo1", "Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])
        
        '''[TCMS#178470 cleanup] Remove RH certificate from RHUI '''
        RHUIManager.remove_rh_certs(self.rs.RHUA)


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
