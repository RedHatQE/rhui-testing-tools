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


class test_0_update_rhel_only(RHUITestcase, RHUI_has_RH_cert):
    def _setup(self):
        '''[Update RHEL only setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.Instances["RHUA"][0])

        '''[Update RHEL only setup] Add cds '''
        RHUIManagerCds.add_cds(self.rs.Instances["RHUA"][0], "Cluster1", self.rs.Instances["CDS"][0].private_hostname)

        '''[Update RHEL only setup] Upload RH content certificate '''
        RHUIManagerEntitlements.upload_content_cert(self.rs.Instances["RHUA"][0], self.cert)

        '''[Update RHEL only setup] Add rh repo '''
        RHUIManagerRepo.add_rh_repo_by_repo(self.rs.Instances["RHUA"][0], ["Red Hat Enterprise Linux 6 Server from RHUI \(RPMs\) \(6Server-x86_64\)"])

        '''[Update RHEL only setup] Associate repos with cluster '''
        RHUIManagerCds.associate_repo_cds(self.rs.Instances["RHUA"][0], "Cluster1", ["Red Hat Enterprise Linux 6 Server from RHUI \(RPMs\) \(6Server-x86_64\)"])

        '''[Update RHEL only setup] Remove rhui configuration rpm from RHUA '''
        Util.remove_conf_rpm(self.rs.Instances["RHUA"][0])

        '''[Update RHEL only setup] Sync RH repo '''
        self._sync_repo(["Red Hat Enterprise Linux 6 Server from RHUI \(RPMs\) \(6Server-x86_64\)"])

        '''[Update RHEL only setup] Sync cds '''
        self._sync_cds([self.rs.Instances["CDS"][0].private_hostname])

        '''[Update RHEL only setup] Generate entitlement certificate '''
        RHUIManagerClient.generate_ent_cert(self.rs.Instances["RHUA"][0], "Cluster1", ["Red Hat Enterprise Linux 6 Server from RHUI \(RPMs\)"], "cert-repo1", "/root/", validity_days="", cert_pw=None)

        '''[Update RHEL only setup] Create configuration rpm '''
        RHUIManagerClient.create_conf_rpm(self.rs.Instances["RHUA"][0], "Cluster1", self.rs.Instances["CDS"][0].private_hostname, "/root", "/root/cert-repo1.crt", "/root/cert-repo1.key", "repo1", "3.0")

        '''[Update RHEL only setup] Install configuration rpm to RHUA '''
        Expect.ping_pong(self.rs.Instances["RHUA"][0], "yum install -y /root/repo1-3.0/build/RPMS/noarch/repo1-3.0-1.noarch.rpm && echo SUCCESS", "[^ ]SUCCESS", 60)

        '''[Update RHEL only setup] Install configuration rpm to all CDSes '''
        for cds in self.rs.Instances["CDS"]:
            Util.remove_conf_rpm(cds)
            Util.install_rpm_from_rhua(self.rs.Instances["RHUA"][0], cds, "/root/repo1-3.0/build/RPMS/noarch/repo1-3.0-1.noarch.rpm")

    def _test(self):
        '''[Update RHEL only test] Upgrade RHUI '''
        Expect.expect_retval(self.rs.Instances["RHUA"][0], "yum -y update", timeout=7200)

        '''[Update RHEL only test] Restast pulp server '''
        Expect.ping_pong(self.rs.Instances["RHUA"][0], "service pulp-server restart && echo SUCCESS", "[^ ]SUCCESS", 20)

        '''[Update RHEL only test] Update all CDSes '''
        for cds in self.rs.Instances["CDS"]:
            Expect.expect_retval(cds, "yum -y update", timeout=7200)
            Expect.ping_pong(cds, "service pulp-cds restart && echo SUCCESS", "[^ ]SUCCESS", 20)

    def _cleanup(self):
        '''[Update RHEL only cleanup] Remove cds '''
        RHUIManagerCds.delete_cds(self.rs.Instances["RHUA"][0], "Cluster1", [self.rs.Instances["CDS"][0].private_hostname])

        '''[Update RHEL only cleanup] Delete RH repo '''
        RHUIManagerRepo.delete_repo(self.rs.Instances["RHUA"][0], ["Red Hat Enterprise Linux 6 Server from RHUI \(RPMs\) \(6Server-x86_64\)"])

        '''[Update RHEL only cleanup] Remove RH certs from RHUI '''
        RHUIManager.remove_rh_certs(self.rs.Instances["RHUA"][0])

        '''[Update RHEL only cleanup] Remove rhui configuration rpm from RHUA '''
        Util.remove_conf_rpm(self.rs.Instances["RHUA"][0])

        '''[Update RHEL only cleanup] Remove rhui configuration rpm from CDSes '''
        for cds in self.rs.Instances["CDS"]:
            Util.remove_conf_rpm(cds)


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
