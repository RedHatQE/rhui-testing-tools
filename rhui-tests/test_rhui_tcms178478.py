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


class test_tcms_178478(RHUITestcase, RHUI_has_RH_cert, RHUI_has_two_CLIs_RHEL6, RHUI_has_two_CDSes):
    def _setup(self):

        '''[TCMS#178478 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.RHUA[0])

        '''[TCMS#178478 setup] Add cdses '''
        RHUIManagerCds.add_cds(self.rs.RHUA[0], "Cluster1", self.rs.CDS[0].private_hostname)
        RHUIManagerCds.add_cds(self.rs.RHUA[0], "Cluster2", self.rs.CDS[1].private_hostname)

        '''[TCMS#178478 setup] Upload RH content certificate '''
        RHUIManagerEntitlements.upload_content_cert(self.rs.RHUA[0], self.cert)

        '''[TCMS#178478 setup] Add rh repo '''
        RHUIManagerRepo.add_rh_repo_by_repo(self.rs.RHUA[0], ["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])

        '''[TCMS#178478 setup] Associate repo with clusters '''
        RHUIManagerCds.associate_repo_cds(self.rs.RHUA[0], "Cluster1", ["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])
        RHUIManagerCds.associate_repo_cds(self.rs.RHUA[0], "Cluster2", ["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])

        '''[TCMS#178478 setup] Sync RH repo '''
        self._sync_repo(["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])

        '''[TCMS#178478 setup] Sync cds '''
        self._sync_cds([self.rs.CDS[0].private_hostname, self.rs.CDS[1].private_hostname])

        '''[TCMS#178478 setup] Remove rhui configuration rpm from clients '''
        Util.remove_conf_rpm(self.rhel6client1)
        Util.remove_conf_rpm(self.rhel6client2)

        '''[TCMS#178478 setup] Generate entitlement certificates '''
        RHUIManagerClient.generate_ent_cert(self.rs.RHUA[0], "Cluster1", ["Red Hat Update Infrastructure 2 \(RPMs\)"], "cert1", "/root/", validity_days="", cert_pw=None)
        RHUIManagerClient.generate_ent_cert(self.rs.RHUA[0], "Cluster2", ["Red Hat Update Infrastructure 2 \(RPMs\)"], "cert2", "/root/", validity_days="", cert_pw=None)

        '''[TCMS#178478 setup] Create configuration rpms '''
        RHUIManagerClient.create_conf_rpm(self.rs.RHUA[0], "Cluster1", self.rs.CDS[0].private_hostname, "/root", "/root/cert1.crt", "/root/cert1.key", "repo1", "3.0")
        RHUIManagerClient.create_conf_rpm(self.rs.RHUA[0], "Cluster2", self.rs.CDS[1].private_hostname, "/root", "/root/cert2.crt", "/root/cert2.key", "repo2", "3.0")

        '''[TCMS#178478 setup] Install configuration rpm to client '''
        Util.install_rpm_from_rhua(self.rs.RHUA[0], rhel6client1, "/root/repo1-3.0/build/RPMS/noarch/repo1-3.0-1.noarch.rpm")
        Util.install_rpm_from_rhua(self.rs.RHUA[0], rhel6client2, "/root/repo2-3.0/build/RPMS/noarch/repo2-3.0-1.noarch.rpm")

    def _test(self):
        '''[TCMS#178478 test] Installing RH rpm to the clients '''
        Expect.ping_pong(self.rhel6client1, "yum install -y pymongo && echo SUCCESS", "[^ ]SUCCESS", 60)
        Expect.ping_pong(self.rhel6client2, "yum install -y pymongo && echo SUCCESS", "[^ ]SUCCESS", 60)

    def _cleanup(self):
        '''[TCMS#178478 cleanup] Removing RH rpm from the clients '''
        Expect.ping_pong(self.rhel6client1, "rpm -e pymongo && echo SUCCESS", "[^ ]SUCCESS", 60)
        Expect.ping_pong(self.rhel6client2, "rpm -e pymongo && echo SUCCESS", "[^ ]SUCCESS", 60)

        '''[TCMS#178478 cleanup] Removing configuration rpm from the client '''
        Util.remove_conf_rpm(self.rhel6client1)
        Util.remove_conf_rpm(self.rhel6client2)

        '''[TCMS#178478 cleanup] Remove cdses '''
        RHUIManagerCds.delete_cds(self.rs.RHUA[0], "Cluster1", [self.rs.CDS[0].private_hostname])
        RHUIManagerCds.delete_cds(self.rs.RHUA[0], "Cluster2", [self.rs.CDS[1].private_hostname])

        '''[TCMS#178478 cleanup] Delete repos '''
        RHUIManagerRepo.delete_repo(self.rs.RHUA[0], ["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])
        
        '''[TCMS#178478 cleanup] Remove RH certificate from RHUI '''
        RHUIManager.remove_rh_certs(self.rs.RHUA[0])


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
