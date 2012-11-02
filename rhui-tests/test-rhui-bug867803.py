#! /usr/bin/python -tt

import argparse
import nose

from rhuilib.expect import *
from rhuilib.rhuisetup import *


class test_bug_867803(object):
    def __init__(self):
        argparser = argparse.ArgumentParser(description='RHUI bug 867803')
        args = argparser.parse_args()
        self.rs = RHUIsetup()
        self.rs.setup_from_rolesfile()

    def __del__(self):
        self.rs.__del__()

    def test_01_rhui_debug(self):
        ''' Check rhui-debug behaivour '''
        Expect.enter(self.rs.RHUA, "")
        Expect.expect(self.rs.RHUA, "root@")
        Expect.enter(self.rs.RHUA, "python /usr/share/rh-rhua/rhui-debug.py | grep '/var/log/httpd/' | wc -l")
        Expect.expect(self.rs.RHUA, "0\r\n")


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
