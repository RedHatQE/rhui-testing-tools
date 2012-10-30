#! /usr/bin/python -tt

import argparse
import nose
import re

from rhuilib.expect import *
from rhuilib.rhuisetup import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_cds import *


class test_178434(object):
    def __init__(self):
        argparser = argparse.ArgumentParser(description='178434: Unregister a CDS belonging to a Single-node Cluster')
        args = argparser.parse_args()
        self.rs = RHUIsetup()
        self.rs.setup_from_rolesfile()

    def test_01_initial_run(self):
        """[setup] check initial rhui-manager login"""
        RHUIManager.initial_run(self.rs.RHUA)

    def test_02_add_cds(self):
        """[setup] check creating a single-node cds cluster"""
        RHUIManagerCds.add_cds(self.rs.RHUA, "cluster-1",
                self.rs.CDS[0].hostname)

    def test_03_remove_cds(self):
        """[setup] check removing a cds from single node cluster"""
        RHUIManagerCds.delete_cds(self.rs.RHUA, "cluster-1", [self.rs.CDS[0].hostname])

    def test_04_check_cluster(self):
        """[test] check the cluster no longer exists"""
        pattern = re.compile('No CDS instances are registered.')
        output = RHUIManagerCds.list(self.rs.RHUA)
        match = pattern.match(output)
        nose.tools.ok_(match is not None)

    def test_05_assert_pulp(self):
        """[test] assert no CDSes are dumped by pulp-admin cds list"""
        from rhuilib.pulp_admin import PulpAdmin
        pulp_admin = PulpAdmin(self.rs.RHUA)
        result = pulp_admin.cds_list()
        pattern = re.compile("^(\r\n)*$", re.DOTALL)
        match = pattern.match(result)
        nose.tools.ok_(match is not None)


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
