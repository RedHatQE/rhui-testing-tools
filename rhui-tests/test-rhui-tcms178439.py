#! /usr/bin/python -tt

import nose
import re

from rhuilib.expect import *
from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_cds import *
from rhuilib.pulp_admin import PulpAdmin
from rhuilib.cds import Cds


class test_tcms_178439(RHUITestcase):
    cluster_a = "cluster_a"
    cluster_b = "cluster_b"

    def _setup(self):
        """[TCMS#178439 setup] initial rhui-manager login"""
        RHUIManager.initial_run(self.rs.RHUA)

        """[TCMS#178439 setup] create a single-node cluster_a containing a cds"""
        RHUIManagerCds.add_cds(self.rs.RHUA, self.cluster_a,
                self.rs.CDS[0].private_hostname)

    def _test(self):
        """[TCMS#178439 test] move the cds to cluster_b"""
        RHUIManagerCds.move_cds(self.rs.RHUA, [self.rs.CDS[0].private_hostname],
                self.cluster_b)

        """[TCMS#178439 test] assert cluster_a no longer exists in pulp and cluster_b contains the cds"""
        cdses = PulpAdmin.cds_list(self.rs.RHUA)
        cds = Cds(name=self.rs.CDS[0].private_hostname,
                hostname=self.rs.CDS[0].private_hostname,
                description='RHUI CDS',
                cluster=self.cluster_b)
        nose.tools.assert_equals(cdses, [cds])

        """[TCMS#178439 test] assert pulp and rhui cds list is the same (i.e. cluster_a no longer exists in RHUI)"""
        rhui_cdses = RHUIManagerCds.info(self.rs.RHUA, [self.cluster_b])
        pulp_cdses = PulpAdmin.cds_list(self.rs.RHUA)
        nose.tools.assert_equals(rhui_cdses, pulp_cdses)

    def _cleanup(self):
        """[TCMS#178439 teardown] remove the cds"""
        RHUIManagerCds.delete_cds(self.rs.RHUA, self.cluster_b,
                [self.rs.CDS[0].private_hostname])


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v', '--with-outputsave',
         '--save-directory=%s.logs' % __file__])
