#! /usr/bin/python -tt

import nose

from stitches.expect import *
from rhuilib.rhui_testcase import *


class test_tcms_236672(RHUITestcase):
    def _setup(self):
        pass

    def _test(self):
        '''[TCMS#236672 test] Check rhui-debug behaivour '''
        Expect.ping_pong(self.rs.Instances["RHUA"][0], "", "root@")
        Expect.ping_pong(self.rs.Instances["RHUA"][0], "python /usr/share/rh-rhua/rhui-debug.py | grep '/var/log/httpd/' | wc -l", "0\r\n")

    def _cleanup(self):
        pass

if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
