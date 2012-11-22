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
from rhuilib.pulp_admin import PulpAdmin
from rhuilib.cds import *


class test_tcms_178462(RHUITestcase, RHUI_has_RH_cert):
    def _setup(self):
        '''[TCMS#178462 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.RHUA[0])

        '''[TCMS#178462 setup] Add cds '''
        RHUIManagerCds.add_cds(self.rs.RHUA[0], "Cluster1", self.rs.CDS[0].private_hostname)

        '''[TCMS#178462 setup] Upload RH content certificate '''
        RHUIManagerEntitlements.upload_content_cert(self.rs.RHUA[0], self.cert)

        '''[TCMS#178462 setup] Add rh repo '''
        RHUIManagerRepo.add_rh_repo_by_repo(self.rs.RHUA[0], ["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])

        '''[TCMS#178462 setup] Associate repo with cluster '''
        RHUIManagerCds.associate_repo_cds(self.rs.RHUA[0], "Cluster1", ["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])

    def _test(self):
        '''[TCMS#178462 test] Check cds info screen '''
        rhui_cds = RhuiCds(name = 'cds1.example.com',
                           hostname = 'cds1.example.com',
                           description = 'RHUI CDS',
                           cluster = 'Cluster1',
                           repos = ['Red Hat Update Infrastructure 2 (RPMs) (6Server-x86_64)'], 
                           client_hostname = 'cds1.example.com')

        nose.tools.assert_equal(RHUIManagerCds.info(self.rs.RHUA[0], ["Cluster1"]), [rhui_cds])

        '''[TCMS#178462 test] Check pulp-admin cds list '''
        cdses = PulpAdmin.cds_list(self.rs.RHUA[0])

        nose.tools.eq_(cdses, [rhui_cds])

        '''[TCMS#178462 test] Check certs created for RH repo '''
        Expect.ping_pong(self.rs.RHUA[0], "test -f /etc/pki/pulp/content/rhel-x86_64-6-rhui-2-rpms-6Server-x86_64/consumer-rhel-x86_64-6-rhui-2-rpms-6Server-x86_64.ca && echo SUCCESS", "[^ ]SUCCESS")
        Expect.ping_pong(self.rs.RHUA[0], "test -f /etc/pki/pulp/content/rhel-x86_64-6-rhui-2-rpms-6Server-x86_64/feed-rhel-x86_64-6-rhui-2-rpms-6Server-x86_64.cert && echo SUCCESS", "[^ ]SUCCESS")
        Expect.ping_pong(self.rs.RHUA[0], "test -f /etc/pki/pulp/content/rhel-x86_64-6-rhui-2-rpms-6Server-x86_64/feed-rhel-x86_64-6-rhui-2-rpms-6Server-x86_64.ca && echo SUCCESS", "[^ ]SUCCESS")
        Expect.ping_pong(self.rs.RHUA[0], "test -f /etc/pki/pulp/content/rhel-x86_64-6-rhui-2-rpms-6Server-x86_64/consumer-rhel-x86_64-6-rhui-2-rpms-6Server-x86_64.cert && echo SUCCESS", "[^ ]SUCCESS")

    def _cleanup(self):
        '''[TCMS#178462 cleanup] Remove cds '''
        RHUIManagerCds.delete_cds(self.rs.RHUA[0], "Cluster1", [self.rs.CDS[0].private_hostname])

        '''[TCMS#178462 cleanup] Delete RH repo '''
        RHUIManagerRepo.delete_repo(self.rs.RHUA[0], ["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])

        '''[TCMS#178462 cleanup] Remove RH certificate from RHUI '''
        RHUIManager.remove_rh_certs(self.rs.RHUA[0])


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
