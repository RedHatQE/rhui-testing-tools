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


class test_tcms_138854(RHUITestcase, RHUI_has_RH_cert, RHUI_has_PROXY):
    def _setup(self):
        '''[TCMS#138854 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.RHUA[0])

        '''[TCMS#138854 setup] Add cds '''
        RHUIManagerCds.add_cds(self.rs.RHUA[0], "Cluster1", self.rs.CDS[0].private_hostname)

        '''[TCMS#138854 setup] Upload RH content certificate '''
        RHUIManagerEntitlements.upload_content_cert(self.rs.RHUA[0], self.cert)

        '''[TCMS#138854 setup] Add rh repo '''
        RHUIManagerRepo.add_rh_repo_by_repo(self.rs.RHUA[0], ["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])

        '''[TCMS#138854 setup] Associate repo with cluster '''
        RHUIManagerCds.associate_repo_cds(self.rs.RHUA[0], "Cluster1", ["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])

        '''[TCMS#138854 setup] Sync RH repo '''
        self._sync_repo(["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])

        '''[TCMS#138854 setup] Sync cds '''
        self._sync_cds([self.rs.CDS[0].private_hostname])

        '''[TCMS#138854 setup] Remove rhui configuration rpm from RHUA '''
        Util.remove_conf_rpm(self.rs.CLI[0])

        '''[TCMS#138854 setup] Generate entitlement certificate '''
        RHUIManagerClient.generate_ent_cert(self.rs.RHUA[0], "Cluster1", ["Red Hat Update Infrastructure 2 \(RPMs\)"], "cert-repo1", "/root/", validity_days="", cert_pw=None)

        '''[TCMS#138854 setup] Create configuration rpm '''
        RHUIManagerClient.create_conf_rpm(self.rs.RHUA[0], "Cluster1", self.rs.CDS[0].private_hostname, "/root", "/root/cert-repo1.crt", "/root/cert-repo1.key", "repo1", "3.0")

        '''[TCMS#138854 setup] Install configuration rpm to client '''
        Util.install_rpm_from_rhua(self.rs.RHUA[0], self.rs.CLI[0], "/root/repo1-3.0/build/RPMS/noarch/repo1-3.0-1.noarch.rpm")

    def _test(self):
        '''[TCMS#138854 test] Installing RH rpm from RH repo to the client '''
        Expect.ping_pong(self.rs.CLI[0], "yum install -y pymongo && echo SUCCESS", "[^ ]SUCCESS", 60)

    def _cleanup(self):
        '''[TCMS#138854 cleanup] Removing RH rpm from the client '''
        Expect.ping_pong(self.rs.CLI[0], "rpm -e pymongo && echo SUCCESS", "[^ ]SUCCESS", 60)

        '''[TCMS#138854 cleanup] Removing configuration rpm from the client '''
        Util.remove_conf_rpm(self.rs.CLI[0])

        '''[TCMS#138854 cleanup] Remove cds '''
        RHUIManagerCds.delete_cds(self.rs.RHUA[0], "Cluster1", [self.rs.CDS[0].private_hostname])

        '''[TCMS#138854 cleanup] Delete repo '''
        RHUIManagerRepo.delete_repo(self.rs.RHUA[0], ["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])

        '''[TCMS#138854 cleanup] Remove RH certificate from RHUI '''
        RHUIManager.remove_rh_certs(self.rs.RHUA[0])


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
