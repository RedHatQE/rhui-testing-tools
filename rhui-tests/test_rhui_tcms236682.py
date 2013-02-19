#! /usr/bin/python -tt

import nose

from patchwork.expect import *
from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *


class test_tcms_236682(RHUITestcase, RHUI_has_RH_cert):
    def _setup(self):
        '''[TCMS#236682 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.Instances["RHUA"][0])

    def _test(self):
        '''[TCMS#236682 test] Upload broken certificate '''
        if self.cert[:1] == '/':
            Expect.enter(self.rs.Instances["RHUA"][0], "mkdir -p `dirname " + self.cert + "` && echo SUCCESS")
            Expect.expect(self.rs.Instances["RHUA"][0], "[^ ]SUCCESS")
        self.rs.Instances["RHUA"][0].sftp.put(self.cert, self.cert)
        Expect.enter(self.rs.Instances["RHUA"][0], "cat " + self.cert + " | sed 's,a,b,' > " + self.cert + ".broken && echo SUCCESS")
        Expect.expect(self.rs.Instances["RHUA"][0], "[^ ]SUCCESS")
        Expect.enter(self.rs.Instances["RHUA"][0], "rhui-manager cert upload --cert " + self.cert + ".broken")
        Expect.expect(self.rs.Instances["RHUA"][0], "[^ ]The given certificate appears malformed.  See the log file for more information.")

    def _cleanup(self):
        pass

if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
