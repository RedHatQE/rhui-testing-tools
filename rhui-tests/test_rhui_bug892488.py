#! /usr/bin/python -tt

import nose
import re

from patchwork.expect import *
from rhuilib.util import *
from rhuilib.rhui_testcase import *


class test_bug_892488(RHUITestcase, RHUI_has_PROXY):
    def _setup(self):
        pass
    def _test(self):
        '''[Bug#892488 test] Check /etc/pulp/pulp.conf permissions '''
        Expect.expect_retval(self.rs.Instances["RHUA"][0], "ls -la /etc/pulp/pulp.conf | grep \"^-rw-r-----\"")

        '''[Bug#892488 test] Check for /var/log/pulp permissions '''
        Expect.expect_retval(self.rs.Instances["RHUA"][0], "ls -ld /var/log/pulp | grep \"^drwxr-x---\"")

    def _cleanup(self):
        pass


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
