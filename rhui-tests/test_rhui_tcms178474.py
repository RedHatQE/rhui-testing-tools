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


class test_tcms_178474(RHUITestcase, RHUI_has_RH_cert):
    def _setup(self):

        '''[TCMS#178474 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.RHUA[0])

        '''[TCMS#178474 setup] Add cdses '''
        RHUIManagerCds.add_cds(self.rs.RHUA[0], "Cluster1", self.rs.CDS[0].private_hostname, self.rs.CDS[0].public_hostname)

        '''[TCMS#178474 setup] Upload RH content certificate '''
        RHUIManagerEntitlements.upload_content_cert(self.rs.RHUA[0], self.cert)

        '''[TCMS#178474 setup] Add rh repo '''
        RHUIManagerRepo.add_rh_repo_by_repo(self.rs.RHUA[0], ["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])

        '''[TCMS#178474 setup] Associate repo with cluster '''
        RHUIManagerCds.associate_repo_cds(self.rs.RHUA[0], "Cluster1", ["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])

    def _test(self):
        '''[TCMS#178474 test] Generate entitlement certificate '''
        RHUIManagerClient.generate_ent_cert(self.rs.RHUA[0], "Cluster1", ["Red Hat Update Infrastructure 2 \(RPMs\)"], "cert-repo1", "/root/", validity_days="", cert_pw=None)

        '''[TCMS#178474 test] Create configuration rpm '''
        RHUIManagerClient.create_conf_rpm(self.rs.RHUA[0], "Cluster1", self.rs.CDS[0].public_hostname, "/root", "/root/cert-repo1.crt", "/root/cert-repo1.key", "repo1", "3.0")

    def _cleanup(self):
        '''[TCMS#178474 cleanup] Remove cdses '''
        RHUIManagerCds.delete_cds(self.rs.RHUA[0], "Cluster1", [self.rs.CDS[0].private_hostname])

        '''[TCMS#178474 cleanup] Delete custom repos '''
        RHUIManagerRepo.delete_repo(self.rs.RHUA[0], ["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])

        '''[TCMS#178474 cleanup] Remove RH certificate from RHUI '''
        RHUIManager.remove_rh_certs(self.rs.RHUA[0])


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
