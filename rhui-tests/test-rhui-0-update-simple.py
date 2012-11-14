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


class test_0_update_simple(RHUITestcase, RHUI_has_RH_cert):
    def _setup(self):
        '''[Update Simple setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.RHUA)

        '''[Update Simple setup] Add cds '''
        RHUIManagerCds.add_cds(self.rs.RHUA, "Cluster1", self.rs.CDS[0].private_hostname)

        '''[Update Simple setup] Upload RH content certificate '''
        RHUIManagerEntitlements.upload_content_cert(self.rs.RHUA, self.cert)

        '''[Update Simple setup] Add rh repo '''
        RHUIManagerRepo.add_rh_repo_by_repo(self.rs.RHUA, ["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])

        '''[Update Simple setup] Associate repos with cluster '''
        RHUIManagerCds.associate_repo_cds(self.rs.RHUA, "Cluster1", ["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])

        '''[Update Simple setup] Remove rhui configuration rpm from RHUA '''
        Util.remove_conf_rpm(self.rs.RHUA)

        '''[Update Simple setup] Sync RH repo '''
        self._sync_repo(["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])

        '''[Update Simple setup] Sync cds '''
        self._sync_cds([self.rs.CDS[0].private_hostname])

        '''[Update Simple setup] Generate entitlement certificate '''
        RHUIManagerClient.generate_ent_cert(self.rs.RHUA, "Cluster1", ["Red Hat Update Infrastructure 2 \(RPMs\)"], "cert-repo1", "/root/", validity_days="", cert_pw=None)

        '''[Update Simple setup] Create configuration rpm '''
        RHUIManagerClient.create_conf_rpm(self.rs.RHUA, "Cluster1", self.rs.CDS[0].private_hostname, "/root", "/root/cert-repo1.crt", "/root/cert-repo1.key", "repo1", "3.0")

        '''[Update Simple setup] Install configuration rpm to RHUA '''
        Expect.ping_pong(self.rs.RHUA, "yum install -y /root/repo1-3.0/build/RPMS/noarch/repo1-3.0-1.noarch.rpm && echo SUCCESS", "[^ ]SUCCESS", 60)

    def _test(self):
        '''[Update Simple test] Upgrade RHUI '''
        Expect.ping_pong(self.rs.RHUA, "yum -y update && echo SUCCESS", "[^ ]SUCCESS", 120)

    def _cleanup(self):
        '''[Update Simple cleanup] Remove cds '''
        RHUIManagerCds.delete_cds(self.rs.RHUA, "Cluster1", [self.rs.CDS[0].private_hostname])

        '''[Update Simple cleanup] Delete RH repo '''
        RHUIManagerRepo.delete_repo(self.rs.RHUA, ["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])

        '''[Update Simple cleanup] Remove RH certs from RHUI '''
        RHUIManager.remove_rh_certs(self.rs.RHUA)

        '''[Update Simple cleanup] Remove rhui configuration rpm from RHUA '''
        Util.remove_conf_rpm(self.rs.RHUA)


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
