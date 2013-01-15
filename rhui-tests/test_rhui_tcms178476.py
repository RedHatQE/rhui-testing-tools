#! /usr/bin/python -tt

import nose

from rhuilib.util import *
from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_cds import *
from rhuilib.rhuimanager_client import *
from rhuilib.rhuimanager_repo import *
from rhuilib.rhuimanager_sync import *


class test_tcms_178476(RHUITestcase, RHUI_has_two_CDSes):
    def _setup(self):
        '''[TCMS#178476 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.Instances["RHUA"][0])

        '''[TCMS#178476 setup] Add cdses'''
        RHUIManagerCds.add_cds(self.rs.Instances["RHUA"][0], "Cluster1", self.rs.Instances["CDS"][0].private_hostname, self.rs.Instances["CDS"][0].public_hostname)
        RHUIManagerCds.add_cds(self.rs.Instances["RHUA"][0], "Cluster1", self.rs.Instances["CDS"][1].private_hostname, self.rs.Instances["CDS"][1].public_hostname)

        '''[TCMS#178476 setup] Remove rhui configuration rpm from client'''
        for cli in self.rs.Instances["CLI"]:
            Util.remove_conf_rpm(cli)

        '''[TCMS#178476 setup] Create custom repo'''
        RHUIManagerRepo.add_custom_repo(self.rs.Instances["RHUA"][0], "repo1")

        '''[TCMS#178476 setup] Associate custom repo with cluster'''
        RHUIManagerCds.associate_repo_cds(self.rs.Instances["RHUA"][0], "Cluster1", ["repo1"])

        '''[TCMS#178476 setup] Upload content to custom repo'''
        RHUIManagerRepo.upload_content(self.rs.Instances["RHUA"][0], ["repo1"], "/etc/rhui/confrpm")

        '''[TCMS#178476 setup] Sync cluster '''
        RHUIManagerSync.sync_cluster(self.rs.Instances["RHUA"][0], ["Cluster1"])

        '''[TCMS#178476 setup] Generate entitlement certificate '''
        RHUIManagerClient.generate_ent_cert(self.rs.Instances["RHUA"][0], "Cluster1", ["repo1"], "cert-repo1", "/root/", validity_days="", cert_pw=None)

        '''[TCMS#178476 setup] Create configuration rpm '''
        RHUIManagerClient.create_conf_rpm(self.rs.Instances["RHUA"][0], "Cluster1", self.rs.Instances["CDS"][0].public_hostname, "/root", "/root/cert-repo1.crt", "/root/cert-repo1.key", "repo1", "3.0")

        '''[TCMS#178476 setup] Install configuration rpm to client '''
        Util.install_rpm_from_rhua(self.rs.Instances["RHUA"][0], self.rs.Instances["CLI"][0], "/root/repo1-3.0/build/RPMS/noarch/repo1-3.0-1.noarch.rpm")

    def _test(self):
        '''[TCMS#178476 test] Test client with 2 cdses up '''
        Expect.ping_pong(self. rs.Instances["CLI"][0], "yum clean metadata && yum check-update && echo SUCCESS", "[^ ]SUCCESS")

        '''[TCMS#178476 test] Test client with only slave cds up '''
        # disabling httpd on master
        Expect.ping_pong(self.rs.Instances["CDS"][0], "service httpd stop && echo SUCCESS", "[^ ]SUCCESS")
        Expect.ping_pong(self.rs.Instances["CLI"][0], "yum clean metadata && yum check-update && echo SUCCESS", "[^ ]SUCCESS")

        '''[TCMS#178476 test] Test client with only master cds up '''
        # enabling httpd on master, disabling on slave
        Expect.ping_pong(self.rs.Instances["CDS"][0], "service httpd start && echo SUCCESS", "[^ ]SUCCESS")
        Expect.ping_pong(self.rs.Instances["CDS"][1], "service httpd stop && echo SUCCESS", "[^ ]SUCCESS")
        Expect.ping_pong(self.rs.Instances["CLI"][0], "yum clean metadata && yum check-update && echo SUCCESS", "[^ ]SUCCESS")

    def _cleanup(self):
        '''[TCMS#178476 cleanup] Recover from tests '''
        # enabling httpd on slave
        Expect.ping_pong(self.rs.Instances["CDS"][1], "service httpd start && echo SUCCESS", "[^ ]SUCCESS")

        '''[TCMS#178476 cleanup] Remove cdses '''
        RHUIManagerCds.delete_cds(self.rs.Instances["RHUA"][0], "Cluster1", [self.rs.Instances["CDS"][0].private_hostname, self.rs.Instances["CDS"][1].private_hostname])

        '''[TCMS#178476 cleanup] Delete custom repos '''
        RHUIManagerRepo.delete_repo(self.rs.Instances["RHUA"][0], ["repo1"])


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
