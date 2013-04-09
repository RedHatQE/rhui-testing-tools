#! /usr/bin/python -tt

import nose
import re

from rhuilib.util import *
from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_repo import *
from rhuilib.pulp_admin import *

class test_rhui_tcms90725(RHUITestcase):
    def _setup(self):
        '''[TCMS#90725 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.Instances["RHUA"][0])

    def _test(self):
        '''[TCMS#90725 test] Check the repo list screen'''
        nose.tools.assert_equal(RHUIManagerRepo.list(self.rs.Instances["RHUA"][0]), [])

    def _cleanup(self):
        '''[TCMS#90725 cleanup]'''
        pass
        
if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
