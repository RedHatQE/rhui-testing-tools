#! /usr/bin/python -tt

import argparse
import nose

from rhuilib.util import *
from rhuilib.rhuisetup import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_cds import *
from rhuilib.rhuimanager_client import *
from rhuilib.rhuimanager_repo import *
from rhuilib.rhuimanager_sync import *
from rhuilib.rhuimanager_entitlements import *
from rhuilib.pulp_admin import PulpAdmin


class test_tcms_178462(object):
    def __init__(self):
        argparser = argparse.ArgumentParser(description='RHUI TCMS testcase 178462')
        argparser.add_argument('--cert',
                               help='use supplied RH enablement certificate')
        args = argparser.parse_args()
        self.cert = args.cert
        if not self.cert:
            raise nose.exc.SkipTest("can't test without RH certificate")
        self.rs = RHUIsetup()
        self.rs.setup_from_rolesfile()

    def __del__(self):
        self.rs.__del__()

    def test_01_initial_run(self):
        ''' Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.RHUA)

    def test_02_add_cds(self):
        ''' Add cds '''
        RHUIManagerCds.add_cds(self.rs.RHUA, "Cluster1", self.rs.CDS[0].hostname)

    def test_03_upload_content_cert(self):
        ''' Upload RH content certificate '''
        RHUIManagerEntitlements.upload_content_cert(self.rs.RHUA, self.cert)

    def test_04_add_rh_repo_by_repo(self):
        ''' Add rh repo '''
        RHUIManagerRepo.add_rh_repo_by_repo(self.rs.RHUA, ["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])

    def test_05_associate_repo_cds(self):
        ''' Associate repo with cluster '''
        RHUIManagerCds.associate_repo_cds(self.rs.RHUA, "Cluster1", ["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])

    def test_06_info_screen(self):
        ''' Check cds info screen '''
        nose.tools.assert_equal(RHUIManagerCds.info(self.rs.RHUA, ["Cluster1"]), [{'Instances': [{'hostname': 'cds1.example.com', 'client': 'cds1.example.com', 'CDS': 'cds1.example.com'}], 'Repositories': ['Red Hat Update Infrastructure 2 (RPMs) (6Server-x86_64)'], 'Name': 'Cluster1'}])

    def test_07_pulp_admin_list(self):
        ''' Check pulp-admin cds list '''
        result = PulpAdmin.cds_list(self.rs.RHUA)
        nose.tools.assert_equals(result, [{'Status': 'Yes', 'Cluster': 'Cluster1', 'Repos': 'rhel-x86_64-6-rhui-2-rpms-6Server-x86_64', 'Hostname': 'cds1.example.com', 'Name': 'cds1.example.com'}])

    def test_08_check_cds_content(self):
        ''' Check certs created for RH repo '''
        Expect.ping_pong(self.rs.RHUA, "test -f /etc/pki/pulp/content/rhel-x86_64-6-rhui-2-rpms-6Server-x86_64/consumer-rhel-x86_64-6-rhui-2-rpms-6Server-x86_64.ca && echo SUCCESS", "[^ ]SUCCESS")
        Expect.ping_pong(self.rs.RHUA, "test -f /etc/pki/pulp/content/rhel-x86_64-6-rhui-2-rpms-6Server-x86_64/feed-rhel-x86_64-6-rhui-2-rpms-6Server-x86_64.cert && echo SUCCESS", "[^ ]SUCCESS")
        Expect.ping_pong(self.rs.RHUA, "test -f /etc/pki/pulp/content/rhel-x86_64-6-rhui-2-rpms-6Server-x86_64/feed-rhel-x86_64-6-rhui-2-rpms-6Server-x86_64.ca && echo SUCCESS", "[^ ]SUCCESS")
        Expect.ping_pong(self.rs.RHUA, "test -f /etc/pki/pulp/content/rhel-x86_64-6-rhui-2-rpms-6Server-x86_64/consumer-rhel-x86_64-6-rhui-2-rpms-6Server-x86_64.cert && echo SUCCESS", "[^ ]SUCCESS")

    def test_09_remove_cds(self):
        ''' Remove cds '''
        RHUIManagerCds.delete_cds(self.rs.RHUA, "Cluster1", [self.rs.CDS[0].hostname])

    def test_10_delete_rh_repo(self):
        ''' Delete RH repo '''
        RHUIManagerRepo.delete_repo(self.rs.RHUA, ["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])

    def test_11_delete_rh_cert(self):
        ''' Remove RH certificate from RHUI '''
        RHUIManager.remove_rh_certs(self.rs.RHUA)


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
