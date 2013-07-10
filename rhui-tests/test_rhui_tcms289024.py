#! /usr/bin/python -tt

import nose

from rhuilib.util import *
from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_identity import *

class test_rhui_tcms289024(RHUITestcase):
    def _setup(self):
        '''[TCMS#289024 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.Instances["RHUA"][0])

    def _test(self):
        '''[TCMS#289024 test] Generate new identity cert '''
        RHUIManagerIdentity.generate_new(self.rs.Instances["RHUA"][0])

    def _cleanup(self):
        pass

if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
