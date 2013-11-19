#! /usr/bin/python -tt

import nose

from rhuilib.util import *
from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_repo import *
from rhuilib.rhuimanager_sync import *
from rhuilib.rhuimanager_entitlements import *


class test_bug_tcms323530(RHUITestcase, RHUI_has_RH_cert):
    ''' Bug#830679 test '''
    def _setup(self):
        '''[TCMS#323530 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.Instances["RHUA"][0])

        '''[TCMS#323530 setup] Copy cert to .txt file'''
        Expect.enter(self.rs.Instances["RHUA"][0], "")
        Expect.expect(self.rs.Instances["RHUA"][0], "root@")
        Expect.enter(self.rs.Instances["RHUA"][0], "cat " + self.cert + " > /tmp/cert_bug_830679.txt && echo SUCCESS")
        Expect.expect(self.rs.Instances["RHUA"][0], "[^ ]SUCCESS.*root@", 10)
        Expect.enter(self.rs.Instances["RHUA"][0], "head -c 2048 /dev/urandom > /tmp/crap_bug_830679.pem && echo SUCCESS")
        Expect.expect(self.rs.Instances["RHUA"][0], "[^ ]SUCCESS.*root@", 10)

    def _test(self):
        '''[TCMS#323530 test] Testing with propper renamed cert '''
        Expect.enter(self.rs.Instances["RHUA"][0], "")
        Expect.expect(self.rs.Instances["RHUA"][0], "root@")
        Expect.enter(self.rs.Instances["RHUA"][0], "rhui-manager cert upload --cert /tmp/cert_bug_830679.txt")
        Expect.expect(self.rs.Instances["RHUA"][0], "Red Hat Entitlements", 30)
        '''[TCMS#323530 test] Testing with propper renamed cert '''
        Expect.enter(self.rs.Instances["RHUA"][0], "rhui-manager cert upload --cert /tmp/crap_bug_830679.pem")
        Expect.expect(self.rs.Instances["RHUA"][0], "does not appear to be valid", 30)

    def _cleanup(self):
        '''[TCMS#323530 cleanup] Remove RH certificate '''
        RHUIManager.remove_rh_certs(self.rs.Instances["RHUA"][0])
        Expect.enter(self.rs.Instances["RHUA"][0], "")
        Expect.expect(self.rs.Instances["RHUA"][0], "root@")
        Expect.enter(self.rs.Instances["RHUA"][0], "rm -f /tmp/cert_bug_830679.txt /tmp/crap_bug_830679.pem && echo SUCCESS")
        Expect.expect(self.rs.Instances["RHUA"][0], "[^ ]SUCCESS.*root@", 10)


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
