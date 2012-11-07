#! /usr/bin/python -tt

import nose
import re

from rhuilib.expect import *
from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_cds import *
from rhuilib.pulp_admin import *


class test_tcms_178434(RHUITestcase):
    def _setup(self):
        """[TCMS#178434 setup] check initial rhui-manager login"""
        RHUIManager.initial_run(self.rs.RHUA)

        """[TCMS#178434 setup] check creating a single-node cds cluster"""
        RHUIManagerCds.add_cds(self.rs.RHUA, "cluster-1",
                self.rs.CDS[0].hostname)

        """[TCMS#178434 setup] check removing a cds from single node cluster"""
        RHUIManagerCds.delete_cds(self.rs.RHUA, "cluster-1", [self.rs.CDS[0].hostname])

    def _test(self):
        """[TCMS#178434 test] check the cluster no longer exists"""
        pattern = re.compile('No CDS instances are registered.')
        output = RHUIManagerCds.list(self.rs.RHUA)
        match = pattern.match(output)
        nose.tools.ok_(match is not None)

        """[TCMS#178434 test] assert no CDSes are dumped by pulp-admin cds list"""
        result = PulpAdmin.cds_list(self.rs.RHUA)
        nose.tools.assert_equal(result, [])

    def _cleanup(self):
        pass

if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
