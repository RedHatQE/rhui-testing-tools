#! /usr/bin/python -tt

import nose

from rhuilib.expect import *
from rhuilib.rhuisetup import *


class test_bug_867803(object):
    def __init__(self):
        self.rs = RHUIsetup()
        self.rs.setup_from_yamlfile()

    def __del__(self):
        self.rs.__del__()

    def test_01_rhui_debug(self):
        ''' Check rhui-debug behaivour '''
        Expect.ping_pong(self.rs.RHUA, "", "root@")
        Expect.ping_pong(self.rs.RHUA, "python /usr/share/rh-rhua/rhui-debug.py | grep '/var/log/httpd/' | wc -l", "0\r\n")


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
