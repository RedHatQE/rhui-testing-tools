#! /usr/bin/python -tt

import nose

from rhuilib.expect import *
from rhuilib.rhui_testcase import *


class test_bug_867803(RHUITestcase):
    def test_bug_867803(self):
        '''[Bug#867803 test] Check rhui-debug behaivour '''
        Expect.ping_pong(self.rs.RHUA, "", "root@")
        Expect.ping_pong(self.rs.RHUA, "python /usr/share/rh-rhua/rhui-debug.py | grep '/var/log/httpd/' | wc -l", "0\r\n")


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
