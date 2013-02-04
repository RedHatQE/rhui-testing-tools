#! /usr/bin/python -tt

import nose
import re

from patchwork.expect import *
from rhuilib.util import *
from rhuilib.rhui_testcase import *


class test_bug_876423(RHUITestcase):
    def _setup(self):
        '''[Bug#876423 setup] Upload testing data'''
        self.rs.Instances["RHUA"][0].sftp.put("/usr/share/rhui-testing-tools/testing-data/bug876423_testcert.pem", "/root/bug876423_testcert.pem")

    def _test(self):
        '''[Bug#876423 test] Trying to upload forged certificate to RHUI '''
        Expect.ping_pong(self.rs.Instances["RHUA"][0], "rhui-manager cert upload --cert /root/bug876423_testcert.pem", "The given certificate contains one or more entitlements")

    def _cleanup(self):
        pass


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
