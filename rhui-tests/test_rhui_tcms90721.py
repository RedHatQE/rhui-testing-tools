#! /usr/bin/python -tt

import nose

from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_users import *


class test_tcms_90721(RHUITestcase):
    def _setup(self):
        pass

    def _test(self):
        '''[TCMS#90721 test] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.Instances["RHUA"][0])

        '''[TCMS#90721 test] Change password '''
        RHUIManager.screen(self.rs.Instances["RHUA"][0], "users")
        Expect.enter(self.rs.Instances["RHUA"][0], "p")
        Expect.expect(self.rs.Instances["RHUA"][0], "Username:")
        Expect.enter(self.rs.Instances["RHUA"][0], "admin")
        Expect.expect(self.rs.Instances["RHUA"][0], "New Password:")
        Expect.enter(self.rs.Instances["RHUA"][0], "90721")
        Expect.expect(self.rs.Instances["RHUA"][0], "Re-enter Password:")
        Expect.enter(self.rs.Instances["RHUA"][0], "90721")
        Expect.expect(self.rs.Instances["RHUA"][0], "Password successfully updated")
        Expect.enter(self.rs.Instances["RHUA"][0], "logout")

        '''[TCMS#90721 test] re-login with new password'''
        RHUIManager.initial_run(self.rs.Instances["RHUA"][0], password="90721")

    def _cleanup(self):
        '''[TCMS#90721 cleanup] Reset password to the default'''
        RHUIManager.initial_run(self.rs.Instances["RHUA"][0], password="90721")
        RHUIManagerUsers.change_password(self.rs.Instances["RHUA"][0], "admin", "admin")


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])

