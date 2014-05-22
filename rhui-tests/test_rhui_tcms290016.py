#! /usr/bin/python -tt

import nose
import re

from stitches.expect import *
from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_cds import *
from rhuilib.pulp_admin import *


class test_tcms_290016(RHUITestcase):
    def _setup(self):
        """[TCMS#290016 setup] Do initial rhui-manager run"""
        RHUIManager.initial_run(self.rs.Instances["RHUA"][0])

    def _test(self):
        """[TCMS#290016 test] Check empty CDS list"""
        pattern = re.compile('No CDS instances are registered.')
        output = RHUIManagerCds.list(self.rs.Instances["RHUA"][0])
        match = pattern.match(output)
        nose.tools.ok_(match is not None)

    def _cleanup(self):
        pass

if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
