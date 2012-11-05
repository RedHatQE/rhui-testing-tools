#! /usr/bin/python -tt

import argparse
import nose
import re

from rhuilib.expect import *
from rhuilib.rhuisetup import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_cds import *
from rhuilib.pulp_admin import PulpAdmin, Cds


class test_tcms_178439(object):
    cluster_a = "cluster_a"
    cluster_b = "cluster_b"

    def __init__(self):
        argparser = argparse.ArgumentParser(description='RHUI TCMS testcase 178439: Move a CDS belonging to a Single-node Cluster')
        args = argparser.parse_args()
        self.rs = RHUIsetup()
        self.rs.setup_from_rolesfile()
        self.cds = self.rs.CDS[0]

    def __del__(self):
        self.rs.__del__()

    def test_01_initial_run(self):
        """[setup] initial rhui-manager login"""
        RHUIManager.initial_run(self.rs.RHUA)

    def test_02_add_cds(self):
        """[setup] create a single-node cluster_a containing a cds"""
        RHUIManagerCds.add_cds(self.rs.RHUA, self.cluster_a,
                self.cds.hostname)

    def test_03_move_cds(self):
        """[test] move the cds to cluster_b"""
        RHUIManagerCds.move_cds(self.rs.RHUA, [self.cds.hostname],
                self.cluster_b)

    def test_04_check_cds_assignment(self):
        """[test] assert cds is now associated with cluster_b"""
        clusters = RHUIManagerCds.info(self.rs.RHUA, [self.cluster_b])
        for cds in clusters[0]["Instances"]:
            nose.tools.eq_(cds["hostname"],  self.cds.hostname,
                self.cds.hostname)

    def test_05_cluster_a_removed(self):
        """[test] assert cluster_a no longer exists"""
        result = RHUIManagerCds.list(self.rs.RHUA)
        # check cluster_a doesn't exist anymore
        pattern = re.compile(str(self.cluster_a))
        match = pattern.match(result)
        nose.tools.ok_(match is None)

    def test_06_assert_propper_pulp_list(self):
        """[test] assert cluster_a no longer exists in pulp and cluster_b exists"""
        cdses = PulpAdmin.cds_list(self.rs.RHUA)
        cds = Cds(name = self.cds.hostname,
                hostname = self.cds.hostname,
                description = 'RHUI CDS',
                cluster = self.cluster_b)
        nose.tools.eq_(cdses, [cds])

    def test_07_remove_cds(self):
        """[teardown] remove the cds"""
        RHUIManagerCds.delete_cds(self.rs.RHUA, self.cluster_b,
                [self.cds.hostname])


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
