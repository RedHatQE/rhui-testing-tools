#! /usr/bin/python -tt

import nose

from rhuilib.util import *
from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_cds import *
from rhuilib.rhuimanager_client import *
from rhuilib.rhuimanager_repo import *
from rhuilib.rhuimanager_sync import *


class test_tcms_191050(RHUITestcase, RHUI_has_RH_rpm):
    def _setup(self):
        '''[TCMS#191050 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.Instances["RHUA"][0])

        '''[TCMS#191050 setup] Add cds '''
        RHUIManagerCds.add_cds(self.rs.Instances["RHUA"][0], "Cluster1", self.rs.Instances["CDS"][0].private_hostname)

        '''[TCMS#191050 setup] Remove rhui configuration rpm from client '''
        for cli in self.rs.Instances["CLI"]:
            Util.remove_conf_rpm(cli)

        '''[TCMS#191050 setup] Create custom repo '''
        RHUIManagerRepo.add_custom_repo(self.rs.Instances["RHUA"][0], "repo1", redhat_gpg="n")

        '''[TCMS#191050 setup] Associate custom repo with cluster '''
        RHUIManagerCds.associate_repo_cds(self.rs.Instances["RHUA"][0], "Cluster1", ["repo1"])

        '''[TCMS#191050 setup] Upload rh rpm to custom repo '''
        self.rs.Instances["RHUA"][0].sftp.put(self.rhrpm, "/root/" + self.rhrpmnvr)
        RHUIManagerRepo.upload_content(self.rs.Instances["RHUA"][0], ["repo1"], "/root/" + self.rhrpmnvr)

        '''[TCMS#191050 setup] Upload signed rpm to custom repo '''
        self.rs.Instances["RHUA"][0].sftp.put("/usr/share/rhui-testing-tools/testing-data/custom-signed-rpm-1-0.1.fc17.noarch.rpm", "/root/custom-signed-rpm-1-0.1.fc17.noarch.rpm")
        RHUIManagerRepo.upload_content(self.rs.Instances["RHUA"][0], ["repo1"], "/root/custom-signed-rpm-1-0.1.fc17.noarch.rpm")

        '''[TCMS#191050 setup] Upload unsigned rpm to custom repo '''
        self.rs.Instances["RHUA"][0].sftp.put("/usr/share/rhui-testing-tools/testing-data/custom-unsigned-rpm-1-0.1.fc17.noarch.rpm", "/root/custom-unsigned-rpm-1-0.1.fc17.noarch.rpm")
        RHUIManagerRepo.upload_content(self.rs.Instances["RHUA"][0], ["repo1"], "/root/custom-unsigned-rpm-1-0.1.fc17.noarch.rpm")

        '''[TCMS#191050 setup] Sync cluster '''
        RHUIManagerSync.sync_cluster(self.rs.Instances["RHUA"][0], ["Cluster1"])
        self._sync_wait_cds([self.rs.Instances["CDS"][0].private_hostname])

        '''[TCMS#191050 setup] Generate entitlement certificate '''
        RHUIManagerClient.generate_ent_cert(self.rs.Instances["RHUA"][0], "Cluster1", ["repo1"], "cert-repo1", "/root/", validity_days="", cert_pw=None)

        '''[TCMS#191050 setup] Create configuration rpm '''
        RHUIManagerClient.create_conf_rpm(self.rs.Instances["RHUA"][0], "Cluster1", self.rs.Instances["CDS"][0].private_hostname, "/root", "/root/cert-repo1.crt", "/root/cert-repo1.key", "repo1", "3.0")

        '''[TCMS#191050 setup] Install configuration rpm to client '''
        Util.install_rpm_from_rhua(self.rs.Instances["RHUA"][0], self.rs.Instances["CLI"][0], "/root/repo1-3.0/build/RPMS/noarch/repo1-3.0-1.noarch.rpm")

        '''[TCMS#191050 setup] Installing RH rpm to the client '''
        Expect.ping_pong(self. rs.Instances["CLI"][0], "yum install -y --nogpgcheck " + self.rhrpmname + " && echo SUCCESS", "[^ ]SUCCESS", 60)

    def _test(self):
        '''[TCMS#191050 test] Installing signed rpm to the client '''
        Expect.ping_pong(self. rs.Instances["CLI"][0], "yum install -y --nogpgcheck custom-signed-rpm && echo SUCCESS", "[^ ]SUCCESS", 60)

        '''[TCMS#191050 test] Installing unsigned rpm to the client '''
        Expect.ping_pong(self. rs.Instances["CLI"][0], "yum install -y --nogpgcheck custom-unsigned-rpm && echo SUCCESS", "[^ ]SUCCESS", 60)

        '''[TCMS#191050 test] Removing RH rpm from the client '''
        Expect.ping_pong(self. rs.Instances["CLI"][0], "rpm -e " + self.rhrpmname + " && echo SUCCESS", "[^ ]SUCCESS", 60)

    def _cleanup(self):
        '''[TCMS#191050 cleanup] Removing signed rpm from the client '''
        Expect.ping_pong(self. rs.Instances["CLI"][0], "rpm -e custom-signed-rpm && echo SUCCESS", "[^ ]SUCCESS", 60)

        '''[TCMS#191050 cleanup] Removing unsigned rpm from the client '''
        Expect.ping_pong(self. rs.Instances["CLI"][0], "rpm -e custom-unsigned-rpm && echo SUCCESS", "[^ ]SUCCESS", 60)

        '''[TCMS#191050 cleanup] Remove cds '''
        RHUIManagerCds.delete_cds(self.rs.Instances["RHUA"][0], "Cluster1", [self.rs.Instances["CDS"][0].private_hostname])

        '''[TCMS#191050 cleanup] Delete custom repo '''
        RHUIManagerRepo.delete_repo(self.rs.Instances["RHUA"][0], ["repo1"])


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
