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


class test_tcms_191048(RHUITestcase, RHUI_has_RH_rpm):
    def _setup(self):
        '''[TCMS#191048 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.Instances["RHUA"][0])

        '''[TCMS#191048 setup] Add cds '''
        RHUIManagerCds.add_cds(self.rs.Instances["RHUA"][0], "Cluster1", self.rs.Instances["CDS"][0].private_hostname)

        '''[TCMS#191048 setup] Remove rhui configuration rpm from client '''
        for cli in self.rs.Instances["CLI"]:
            Util.remove_conf_rpm(cli)

        '''[TCMS#191048 setup] Create custom repo '''
        self.rs.Instances["RHUA"][0].sftp.put("/usr/share/rhui-testing-tools/testing-data/public.key", "/root/public.key")
        RHUIManagerRepo.add_custom_repo(self.rs.Instances["RHUA"][0], "repo1", redhat_gpg="n", custom_gpg="/root/public.key")

        '''[TCMS#191048 setup] Associate custom repo with cluster '''
        RHUIManagerCds.associate_repo_cds(self.rs.Instances["RHUA"][0], "Cluster1", ["repo1"])

        '''[TCMS#191048 setup] Upload rh rpm to custom repo '''
        self.rs.Instances["RHUA"][0].sftp.put(self.rhrpm, "/root/" + self.rhrpmnvr)
        RHUIManagerRepo.upload_content(self.rs.Instances["RHUA"][0], ["repo1"], "/root/" + self.rhrpmnvr)

        '''[TCMS#191048 setup] Upload signed rpm to custom repo '''
        self.rs.Instances["RHUA"][0].sftp.put("/usr/share/rhui-testing-tools/testing-data/custom-signed-rpm-1-0.1.fc17.noarch.rpm", "/root/custom-signed-rpm-1-0.1.fc17.noarch.rpm")
        RHUIManagerRepo.upload_content(self.rs.Instances["RHUA"][0], ["repo1"], "/root/custom-signed-rpm-1-0.1.fc17.noarch.rpm")

        '''[TCMS#191048 setup] Upload unsigned rpm to custom repo '''
        self.rs.Instances["RHUA"][0].sftp.put("/usr/share/rhui-testing-tools/testing-data/custom-unsigned-rpm-1-0.1.fc17.noarch.rpm", "/root/custom-unsigned-rpm-1-0.1.fc17.noarch.rpm")
        RHUIManagerRepo.upload_content(self.rs.Instances["RHUA"][0], ["repo1"], "/root/custom-unsigned-rpm-1-0.1.fc17.noarch.rpm")

        '''[TCMS#191048 setup] Sync cds '''
        self._sync_cds([self.rs.Instances["CDS"][0].private_hostname])

        '''[TCMS#191048 setup] Generate entitlement certificate '''
        RHUIManagerClient.generate_ent_cert(self.rs.Instances["RHUA"][0], "Cluster1", ["repo1"], "cert-repo1", "/root/", validity_days="", cert_pw=None)

        '''[TCMS#191048 setup] Create configuration rpm '''
        RHUIManagerClient.create_conf_rpm(self.rs.Instances["RHUA"][0], "Cluster1", self.rs.Instances["CDS"][0].private_hostname, "/root", "/root/cert-repo1.crt", "/root/cert-repo1.key", "repo1", "3.0")

        '''[TCMS#191048 setup] Install configuration rpm to client '''
        Util.install_rpm_from_rhua(self.rs.Instances["RHUA"][0], self.rs.Instances["CLI"][0], "/root/repo1-3.0/build/RPMS/noarch/repo1-3.0-1.noarch.rpm")

    def _test(self):
        '''[TCMS#191048 test] Check RH gpg key in repo file '''
        Expect.ping_pong(self. rs.Instances["CLI"][0], "grep RPM-GPG-KEY-redhat-release /etc/yum.repos.d/rh-cloud.repo || echo SUCCESS", "[^ ]SUCCESS", 60)

        '''[TCMS#191048 test] Installing signed rpm to the client '''
        Expect.ping_pong(self. rs.Instances["CLI"][0], "yum install -y custom-signed-rpm && echo SUCCESS", "[^ ]SUCCESS", 60)

        '''[TCMS#191048 test] Trying to install unsigned rpm to the client '''
        Expect.ping_pong(self. rs.Instances["CLI"][0], "yum install -y custom-unsigned-rpm || echo FAILURE", "[^ ]FAILURE", 60)

    def _cleanup(self):
        '''[TCMS#191048 cleanup] Removing signed rpm from the client '''
        Expect.ping_pong(self. rs.Instances["CLI"][0], "rpm -e custom-signed-rpm && echo SUCCESS", "[^ ]SUCCESS", 60)

        '''[TCMS#191048 cleanup] Removing configuration rpm from the client '''
        Util.remove_conf_rpm(self.rs.Instances["CLI"][0])

        '''[TCMS#191048 cleanup] Removing gpg key from the client '''
        Expect.ping_pong(self. rs.Instances["CLI"][0], "rpm -e gpg-pubkey-b6963d12-5080038c && echo SUCCESS", "[^ ]SUCCESS", 60)

        '''[TCMS#191048 cleanup] Remove cds '''
        RHUIManagerCds.delete_cds(self.rs.Instances["RHUA"][0], "Cluster1", [self.rs.Instances["CDS"][0].private_hostname])

        '''[TCMS#191048 cleanup] Delete custom repo '''
        RHUIManagerRepo.delete_repo(self.rs.Instances["RHUA"][0], ["repo1"])


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
