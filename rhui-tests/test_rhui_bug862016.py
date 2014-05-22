#! /usr/bin/python -tt

import nose
import re

from stitches.expect import *
from rhuilib.util import *
from rhuilib.rhui_testcase import *


class test_bug_862016(RHUITestcase, RHUI_has_PROXY):
    def _setup(self):
        pass

    def _test(self):
        '''[Bug#862016 setup] No yum section in /etc/rhui/rhui-tools.conf '''
        Expect.expect_retval(self.rs.Instances["RHUA"][0], "grep \"\[yum\]\" /etc/rhui/rhui-tools.conf", 1)

        '''[Bug#862016 setup] redhat section in /etc/rhui/rhui-tools.conf '''
        Expect.expect_retval(self.rs.Instances["RHUA"][0], "grep -B3 proxy_ /etc/rhui/rhui-tools.conf | grep \"\[redhat\]\"")

    def _cleanup(self):
        pass

if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
