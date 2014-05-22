#! /usr/bin/python -tt

import nose

from stitches.expect import *
from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.util import *


class test_tcms_236670(RHUITestcase):
    def _setup(self):
        '''[TCMS#236670 setup] Remove old certificates '''
        Expect.ping_pong(self.rs.Instances["RHUA"][0], "rm -rf /etc/pki/rhui/entitlement-ca.crt /etc/pki/rhui/entitlement-ca-key.pem /etc/pki/rhui/identity.crt /etc/pki/rhui/identity.key /root/.rhui && echo SUCCESS", "[^ ]SUCCESS")

    def _test(self):
        '''[TCMS#236670 test] Doing initial run with wrong password'''
        Expect.enter(self.rs.Instances["RHUA"][0], "rhui-manager")
        Expect.enter(self.rs.Instances["RHUA"][0], "/etc/rhui/pem/ca.crt")
        Expect.expect(self.rs.Instances["RHUA"][0], "Full path to the new signing CA certificate private key:")
        Expect.enter(self.rs.Instances["RHUA"][0], "/etc/rhui/pem/ca.key")
        Expect.expect(self.rs.Instances["RHUA"][0], "regenerated using rhui-manager.*:")
        Expect.enter(self.rs.Instances["RHUA"][0], "")
        Expect.expect(self.rs.Instances["RHUA"][0], "Enter pass phrase for.*:")
        Expect.enter(self.rs.Instances["RHUA"][0], "wrong_password")
        Expect.expect(self.rs.Instances["RHUA"][0], "Error creating identity certificate, check the log file for more information")

    def _cleanup(self):
        '''[TCMS#236670 cleanup] Doing safe initial run'''
        Expect.ping_pong(self.rs.Instances["RHUA"][0], "rm -rf /etc/pki/rhui/entitlement-ca.crt /etc/pki/rhui/entitlement-ca-key.pem /etc/pki/rhui/identity.crt /etc/pki/rhui/identity.key /root/.rhui && echo SUCCESS", "[^ ]SUCCESS")
        RHUIManager.initial_run(self.rs.Instances["RHUA"][0])

if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
