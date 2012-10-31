#! /usr/bin/python -tt

import argparse, nose, re

from rhuilib.expect import *
from rhuilib.rhuisetup import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_cds import *
from rhuilib.pulp_admin import PulpAdmin

class test_178439(object):
    cluster_a = "cluster_a"
    cluster_b = "cluster_b"

    def __init__(self):
        argparser = argparse.ArgumentParser(description=\
                '178439: Move a CDS belonging to a Single-node Cluster')
        args = argparser.parse_args()
        self.rs = RHUIsetup()
        self.rs.setup_from_rolesfile()
        self.pulp_admin = PulpAdmin(self.rs.RHUA)
    def test_01_initial_run(self):
        """[setup] initial rhui-manager login"""
        RHUIManager.initial_run(self.rs.RHUA)
    def test_02_add_cds(self):
        """[setup] create a single-node cluster_a containing a cds"""
        RHUIManagerCds.add_cds(self.rs.RHUA, self.cluster_a,
                self.rs.CDS[0].hostname)
    def test_03_move_cds(self):
        """[test] move the cds to cluster_b"""
        RHUIManagerCds.move_cdses(self.rs.RHUA, [self.rs.CDS[0].hostname],
                self.cluster_b)
    def test_04_check_cds_assignment(self):
        """[test] assert cds is now associated with cluster_b"""
        result = RHUIManagerCds.list(self.rs.RHUA)
        print result
        # check cds is now associated with cluster_b
        # NOTE: this expression _really_ checks that the cds is the first
        # record of a particular cluster; see [1]
        pattern = re.compile(
                ".*%s\s*\n\s*-+\s*\n\s*Content Delivery Servers\s*\n\s*-+\s*%s.*" % \
                (self.cluster_b, self.rs.CDS[0].hostname), re.DOTALL)
        match = pattern.match(result)
        nose.tools.ok_(match is not None)
    def test_05_cluster_a_removed(self):
        """[test] assert cluster_a no longer exists"""
        result = RHUIManagerCds.list(self.rs.RHUA)
        # check cluster_a doesn't exist anymore
        pattern = re.compile(str(self.cluster_a))
        match = pattern.match(result)
        nose.tools.ok_(match is None)
    def test_06_assert_no_cluster_a_in_pulp(self):
        """[test] assert cluster_a no longer exists in pulp"""
        result = self.pulp_admin.cds_list()
        pattern = re.compile(str(self.cluster_a))
        match = pattern.match(result)
        nose.tools.ok_(match is None)
    def test_07_assert_cds_cluster_b_in_pulp(self):
        """[test] assert cluster_b holds cds now in pulp"""
        result = self.pulp_admin.cds_list()
        print result
        # see [2]
        pattern = re.compile(
                ".*Hostname[^\r\n\w]*%s[^\r\n\w]*\r\n[^\r\n\w]*Description[^\r\n\w]*RHUI\s*CDS[^\w\r\n]*\r\n[^\r\n\w]*Cluster[^\r\n\w]*%s.*" \
                % (self.rs.CDS[0].hostname, self.cluster_b), re.DOTALL)
        match = pattern.match(result)
        nose.tools.ok_(match is not None)
    def test_08_remove_cds(self):
        """[teardown] remove the cds"""
        RHUIManagerCds.delete_cds(self.rs.RHUA, self.cluster_b,
                [self.rs.CDS[0].hostname])


#[1] clusters listed in rhui-manager e.g.
"""

 cluster-1
  ---------
    Content Deliver Servers
    -----------------------
    cds1.example.com
"""

#[2] cdses listed in pulp-admin
"""

+------------------------------------------+
                CDS Instances
+------------------------------------------+

Name                    cds1.example.com         
Hostname                cds1.example.com         
Description             RHUI CDS                 
Cluster                 cluster-a                
Sync Schedule           2012-10-29T19:20:09-04:00/PT6H
Repos                   None                     
Last Sync               Never                    
Status:
   Responding           Yes                      
   Last Heartbeat       2012-10-29 17:36:29.182300+00:00

"""


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
