#! /usr/bin/python -tt

import nose

from patchwork.expect import *
from rhuilib.rhui_testcase import *


class test_bug_867803(RHUITestcase):
    def _setup(self):
        pass

    def _test(self):
        '''[Bug#867803 test] Check rhui-debug behaivour '''
        Expect.ping_pong(self.rs.Instances["RHUA"][0], "", "root@")
        Expect.ping_pong(self.rs.Instances["RHUA"][0], "python /usr/share/rh-rhua/rhui-debug.py | grep '/var/log/httpd/' | wc -l", "0\r\n")

    def _cleanup(self):
        pass

if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
