#! /usr/bin/python -tt

import nose

from rhuilib.rhuimanager_identity import *
from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from stitches.expect import *


class test_tcms267060(RHUITestcase):
    def _setup(self):
        pass

    def _test(self):
        '''[TCMS#267060 test] generate new identity certificate'''
        RHUIManager.screen(self.rs.Instances["RHUA"][0], "identity")
        Expect.enter(self.rs.Instances["RHUA"][0], "g")
        Expect.expect(self.rs.Instances["RHUA"][0], "Proceed\? \[y/n\]")
        Expect.enter(self.rs.Instances["RHUA"][0], "y")
        Expect.expect(self.rs.Instances["RHUA"][0], "regenerated using rhui-manager.*:")
        Expect.enter(self.rs.Instances["RHUA"][0], "")
        Expect.expect(self.rs.Instances["RHUA"][0], "Enter pass phrase for.*:")
        Expect.enter(self.rs.Instances["RHUA"][0], "")

        '''[TCMS#267060 test] send to sleep the process pressing CRTL-Z'''
        self.rs.Instances["RHUA"][0].exec_command("kill -SIGTSTP `ps ax | grep rhui-manager | grep -v grep | cut -f 1 -d ' '`")
        self.rs.Instances["RHUA"][0].exec_command("fg %1")
        Expect.enter(self.rs.Instances["RHUA"][0], "")

        '''[TCMS#267060 test] check whether or not the process entered infinite loop'''
        Expect.expect(self.rs.Instances["RHUA"][0], ".*=>.*")
        Expect.enter(self.rs.Instances["RHUA"][0], "q")

    def _cleanup(self):

        '''[TCMS#267060 cleanup] kill rhui-manager '''
        self.rs.Instances["RHUA"][0].exec_command("kill -SIGKILL `ps ax | grep rhui-manager | grep -v grep | cut -f 1 -d ' '`")

        '''[TCMS#267060 cleanup] check rhui-manager is killed via finding the prompt of RHUA instance'''
        Expect.enter(self.rs.Instances["RHUA"][0], "")
        Expect.expect(self.rs.Instances["RHUA"][0],"root@rhua.*")


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
