#! /usr/bin/python -tt

import nose
import time

from rhuilib.util import *
from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_entitlements import *


class test_tcms_90960(RHUITestcase, RHUI_has_RH_cert):
    def _setup(self):
        '''[TCMS#90960 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.Instances["RHUA"][0])

        '''[TCMS#90960 setup] Upload RH content certificate '''
        RHUIManagerEntitlements.upload_content_cert(self.rs.Instances["RHUA"][0], self.cert)

    def _test(self):
        '''[TCMS#90960 test] Test client with second cds only '''
        Expect.ping_pong(self.rs.Instances["RHUA"][0], "rhui-manager cert info | grep 'Red Hat Update Infrastructure 2' && echo SUCCESS", "[^ ]SUCCESS", 10)

    def _cleanup(self):
        '''[TCMS#90960 cleanup] Remove RH certificate from RHUI '''
        RHUIManager.remove_rh_certs(self.rs.Instances["RHUA"][0])


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
