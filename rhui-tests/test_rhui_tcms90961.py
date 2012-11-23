#! /usr/bin/python -tt

import nose
import time

from rhuilib.util import *
from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_entitlements import *


class test_tcms_90961(RHUITestcase, RHUI_has_RH_cert):
    def _setup(self):
        '''[TCMS#90961 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.RHUA[0])

    def _test(self):
        self.rs.RHUA[0].sftp.put(self.cert, "/root/test_90961.pem")

        '''[TCMS#90961 test] Test client with second cds only '''
        Expect.ping_pong(self.rs.RHUA[0], "rhui-manager cert upload --cert /root/test_90961.pem | grep 'Red Hat Update Infrastructure 2' && echo SUCCESS", "[^ ]SUCCESS", 10)

    def _cleanup(self):
        '''[TCMS#90961 cleanup] Remove RH certificate from RHUI '''
        RHUIManager.remove_rh_certs(self.rs.RHUA[0])


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
