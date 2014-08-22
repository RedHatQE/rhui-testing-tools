#! /usr/bin/python -tt

import nose

from rhuilib.util import *
from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_cds import *
from rhuilib.rhuimanager_client import *
from rhuilib.rhuimanager_repo import *
from rhuilib.rhuimanager_sync import *


class test_tcms_110761(RHUITestcase, RHUI_has_two_CDSes):
    def _setup(self):
        '''[TCMS#110761 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.Instances["RHUA"][0])

        '''[TCMS#110761 setup] Add cdses'''
        RHUIManagerCds.add_cds(self.rs.Instances["RHUA"][0], "Cluster1", self.rs.Instances["CDS"][0].private_hostname)
        RHUIManagerCds.add_cds(self.rs.Instances["RHUA"][0], "Cluster1", self.rs.Instances["CDS"][1].private_hostname)

        '''[TCMS#110761 setup] Remove rhui configuration rpm from client'''
        Util.remove_conf_rpm(self.rs.Instances["CLI"][0])

        '''[TCMS#178470 setup] Create custom repo '''
        self.rs.Instances["RHUA"][0].sftp.put("/usr/share/rhui-testing-tools/testing-data/public.key", "/root/public.key")
        RHUIManagerRepo.add_custom_repo(self.rs.Instances["RHUA"][0], "repo1", entitlement="y", custom_gpg="/root/public.key")

        '''[TCMS#178470 setup] Upload signed rpm to custom repo '''
        self.rs.Instances["RHUA"][0].sftp.put("/usr/share/rhui-testing-tools/testing-data/custom-signed-rpm-1-0.1.fc17.noarch.rpm", "/root/custom-signed-rpm-1-0.1.fc17.noarch.rpm")
        RHUIManagerRepo.upload_content(self.rs.Instances["RHUA"][0], ["repo1"], "/root/custom-signed-rpm-1-0.1.fc17.noarch.rpm")

        '''[TCMS#110761 setup] Associate custom repo with cluster'''
        RHUIManagerCds.associate_repo_cds(self.rs.Instances["RHUA"][0], "Cluster1", ["repo1"])

        '''[TCMS#110761 setup] Sync cluster '''
        RHUIManagerSync.sync_cluster(self.rs.Instances["RHUA"][0], ["Cluster1"])
        self._sync_wait_cds([self.rs.Instances["CDS"][0].private_hostname, self.rs.Instances["CDS"][1].private_hostname])

        '''[TCMS#110761 setup] Generate entitlement certificate '''
        RHUIManagerClient.generate_ent_cert(self.rs.Instances["RHUA"][0], "Cluster1", ["repo1"], "cert-repo1", "/root/", validity_days="", cert_pw=None)

        '''[TCMS#110761 setup] Create configuration rpm '''
        RHUIManagerClient.create_conf_rpm(self.rs.Instances["RHUA"][0], "Cluster1", self.rs.Instances["CDS"][0].private_hostname, "/root", "/root/cert-repo1.crt", "/root/cert-repo1.key", "repo1", "3.0")

        '''[TCMS#110761 setup] Install configuration rpm to client '''
        Util.install_rpm_from_rhua(self.rs.Instances["RHUA"][0], self.rs.Instances["CLI"][0], "/root/repo1-3.0/build/RPMS/noarch/repo1-3.0-1.noarch.rpm")

    def _test(self):
        '''[TCMS#110761 test] Test client with 2 cdses '''
        Expect.ping_pong(self.rs.Instances["CLI"][0], "yum install -y custom-signed-rpm && echo SUCCESS", "[^ ]SUCCESS", 60)
        Expect.ping_pong(self.rs.Instances["CLI"][0], "rpm -e custom-signed-rpm && echo SUCCESS", "[^ ]SUCCESS", 60)

        '''[TCMS#110761 test] Test client with second cds only '''
        Expect.ping_pong(self.rs.Instances["CLI"][0], "sed -i '/^" + self.rs.Instances["CDS"][0].private_hostname + "$/d' /etc/yum.repos.d/rhui-load-balancers && echo SUCCESS", "[^ ]SUCCESS", 60)
        Expect.ping_pong(self.rs.Instances["CLI"][0], "yum clean all && echo SUCCESS", "[^ ]SUCCESS", 60)
        Expect.ping_pong(self.rs.Instances["CLI"][0], "yum install -y custom-signed-rpm && echo SUCCESS", "[^ ]SUCCESS", 60)
        Expect.ping_pong(self.rs.Instances["CLI"][0], "rpm -e custom-signed-rpm && echo SUCCESS", "[^ ]SUCCESS", 60)

    def _cleanup(self):
        '''[TCMS#110761 cleanup] Remove cdses '''
        RHUIManagerCds.delete_cds(self.rs.Instances["RHUA"][0], "Cluster1", [self.rs.Instances["CDS"][0].private_hostname, self.rs.Instances["CDS"][1].private_hostname])

        '''[TCMS#110761 cleanup] Delete custom repos '''
        RHUIManagerRepo.delete_repo(self.rs.Instances["RHUA"][0], ["repo1"])

        '''[TCMS#110761 cleanup] Removing gpg key from the client '''
        Expect.ping_pong(self.rs.Instances["CLI"][0], "rpm -e gpg-pubkey-b6963d12-5080038c && echo SUCCESS", "[^ ]SUCCESS", 60)

        '''[TCMS#110761 cleanup] Remove rhui configuration rpm from client'''
        Util.remove_conf_rpm(self.rs.Instances["CLI"][0])

if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
