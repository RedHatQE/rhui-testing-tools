#! /usr/bin/python -tt

import nose
import time

from rhuilib.util import *
from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_cds import *
from rhuilib.rhuimanager_client import *
from rhuilib.rhuimanager_repo import *
from rhuilib.rhuimanager_sync import *
from rhuilib.rhuimanager_entitlements import *
from rhuilib.cds import RhuiCds


class test_tcms_248535(RHUITestcase, RHUI_has_RH_cert):
    ''' Bug 916378 '''
    def _setup(self):

        '''[TCMS#248535 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.Instances["RHUA"][0])

        '''[TCMS#248535 setup] Add cdses '''
        RHUIManagerCds.add_cds(self.rs.Instances["RHUA"][0], "Cluster1", self.rs.Instances["CDS"][0].private_hostname, self.rs.Instances["CDS"][0].public_hostname)

        '''[TCMS#248535 setup] Upload RH content certificate '''
        RHUIManagerEntitlements.upload_content_cert(self.rs.Instances["RHUA"][0], self.cert)

        '''[TCMS#248535 setup] Add rh repo '''
        RHUIManagerRepo.add_rh_repo_by_repo(self.rs.Instances["RHUA"][0], ["Red Hat Update Infrastructure 2 \(Source RPMs\) \(6Server-x86_64\)"])

        '''[TCMS#248535 setup] Associate repo with cluster '''
        RHUIManagerCds.associate_repo_cds(self.rs.Instances["RHUA"][0], "Cluster1", ["Red Hat Update Infrastructure 2 \(Source RPMs\) \(6Server-x86_64\)"])

        '''[TCMS#248535 setup] Sync RH repo '''
        self._sync_repo(["Red Hat Update Infrastructure 2 \(Source RPMs\) \(6Server-x86_64\)"])

        '''[TCMS#248535 setup] Sync cds '''
        self._sync_cds([self.rs.Instances["CDS"][0].private_hostname])

        '''[TCMS#248535 setup] Delete RH repo '''
        RHUIManagerRepo.delete_repo(self.rs.Instances["RHUA"][0], ["Red Hat Update Infrastructure 2 \(Source RPMs\) \(6Server-x86_64\)"])

        time.sleep(30)

        '''[TCMS#248535 setup] Sync cds '''
        self._sync_cds([self.rs.Instances["CDS"][0].private_hostname])

    def _test(self):
        '''[TCMS#248535 test] Check packages on RHUA '''
        Expect.ping_pong(self.rs.Instances["RHUA"][0], "find /var/lib/pulp/ -name \"rh-rhui-tools*.src.rpm\" | grep rh-rhui-tools || echo SUCCESS", "[^ ]SUCCESS", 10)

        '''[TCMS#248535 test] Check packages on CDS '''
        Expect.ping_pong(self.rs.Instances["CDS"][0], "find /var/lib/pulp-cds/ -name \"rh-rhui-tools*.src.rpm\" | grep rh-rhui-tools || echo SUCCESS", "[^ ]SUCCESS", 10)

    def _cleanup(self):
        '''[TCMS#248535 cleanup] Remove cds '''
        RHUIManagerCds.delete_cds(self.rs.Instances["RHUA"][0], "Cluster1", [self.rs.Instances["CDS"][0].private_hostname])

        '''[TCMS#248535 cleanup] Remove RH certificate from RHUI '''
        RHUIManager.remove_rh_certs(self.rs.Instances["RHUA"][0])


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
