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


class test_tcms_178477(RHUITestcase, RHUI_has_RH_cert, RHUI_has_RHEL5_and_RHEL6_CLIs):
    def _setup(self):

        '''[TCMS#178477 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.RHUA[0])

        '''[TCMS#178477 setup] Add cdses '''
        RHUIManagerCds.add_cds(self.rs.RHUA[0], "Cluster1", self.rs.CDS[0].private_hostname)

        '''[TCMS#178477 setup] Upload RH content certificate '''
        RHUIManagerEntitlements.upload_content_cert(self.rs.RHUA[0], self.cert)

        '''[TCMS#178477 setup] Remove rhui configuration rpm from clients '''
        Util.remove_conf_rpm(self.rhel5client)
        Util.remove_conf_rpm(self.rhel6client)

        '''[TCMS#178477 setup] Add rh repo '''
        RHUIManagerRepo.add_rh_repo_by_repo(self.rs.RHUA[0], ["Red Hat Enterprise Linux 6 Server from RHUI \(RPMs\) \(6Server-x86_64\)", "Red Hat Enterprise Linux 5 Server from RHUI \(RPMs\) \(5Server-x86_64\)"])

        '''[TCMS#178477 setup] Associate repo with clusters '''
        RHUIManagerCds.associate_repo_cds(self.rs.RHUA[0], "Cluster1", ["Red Hat Enterprise Linux 6 Server from RHUI \(RPMs\) \(6Server-x86_64\)", "Red Hat Enterprise Linux 5 Server from RHUI \(RPMs\) \(5Server-x86_64\)"])

        '''[TCMS#178477 setup] Sync RH repo '''
        self._sync_repo(["Red Hat Enterprise Linux 6 Server from RHUI \(RPMs\) \(6Server-x86_64\)", "Red Hat Enterprise Linux 5 Server from RHUI \(RPMs\) \(5Server-x86_64\)"])

        '''[TCMS#178477 setup] Sync cds '''
        self._sync_cds([self.rs.CDS[0].private_hostname])

        '''[TCMS#178477 setup] Generate entitlement certificates '''
        RHUIManagerClient.generate_ent_cert(self.rs.RHUA[0], "Cluster1", ["Red Hat Enterprise Linux 5 Server from RHUI \(RPMs\)"], "cert1", "/root/", validity_days="", cert_pw=None)
        RHUIManagerClient.generate_ent_cert(self.rs.RHUA[0], "Cluster1", ["Red Hat Enterprise Linux 6 Server from RHUI \(RPMs\)"], "cert2", "/root/", validity_days="", cert_pw=None)

        '''[TCMS#178477 setup] Create configuration rpms '''
        RHUIManagerClient.create_conf_rpm(self.rs.RHUA[0], "Cluster1", self.rs.CDS[0].private_hostname, "/root", "/root/cert1.crt", "/root/cert1.key", "repo1", "3.0")
        RHUIManagerClient.create_conf_rpm(self.rs.RHUA[0], "Cluster1", self.rs.CDS[0].private_hostname, "/root", "/root/cert2.crt", "/root/cert2.key", "repo2", "3.0")

        '''[TCMS#178477 setup] Install configuration rpms to the clients '''
        Util.install_rpm_from_rhua(self.rs.RHUA[0], self.rhel5client, "/root/repo1-3.0/build/RPMS/noarch/repo1-3.0-1.noarch.rpm")
        Util.install_rpm_from_rhua(self.rs.RHUA[0], self.rhel6client, "/root/repo2-3.0/build/RPMS/noarch/repo2-3.0-1.noarch.rpm")

    def _test(self):
        '''[TCMS#178477 test] Installing RH rpm to the clients '''
        Expect.ping_pong(self.rhel5client, "yum install -y zsh && echo SUCCESS", "[^ ]SUCCESS", 60)
        Expect.ping_pong(self.rhel6client, "yum install -y zsh && echo SUCCESS", "[^ ]SUCCESS", 60)

    def _cleanup(self):
        '''[TCMS#178477 cleanup] Removing RH rpms from the clients '''
        Expect.ping_pong(self.rhel5client, "rpm -e zsh && echo SUCCESS", "[^ ]SUCCESS", 60)
        Expect.ping_pong(self.rhel6client, "rpm -e zsh && echo SUCCESS", "[^ ]SUCCESS", 60)

        '''[TCMS#178477 cleanup] Removing configuration rpms from the clients '''
        Util.remove_conf_rpm(self.rhel5client)
        Util.remove_conf_rpm(self.rhel6client)

        '''[TCMS#178477 cleanup] Delete repos '''
        RHUIManagerRepo.delete_repo(self.rs.RHUA[0], ["Red Hat Enterprise Linux 6 Server from RHUI \(RPMs\) \(6Server-x86_64\)", "Red Hat Enterprise Linux 5 Server from RHUI \(RPMs\) \(5Server-x86_64\)"])

        '''[TCMS#178477 cleanup] Sync cds '''
        self._sync_cds([self.rs.CDS[0].private_hostname])

        '''[TCMS#178477 cleanup] Remove cds '''
        RHUIManagerCds.delete_cds(self.rs.RHUA[0], "Cluster1", [self.rs.CDS[0].private_hostname])

        '''[TCMS#178477 cleanup] Remove RH certificate from RHUI '''
        RHUIManager.remove_rh_certs(self.rs.RHUA[0])


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
