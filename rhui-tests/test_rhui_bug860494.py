#! /usr/bin/python -tt

import nose

from patchwork.expect import *
from rhuilib.rhui_testcase import *


class test_bug_860494(RHUITestcase):
    def _setup(self):
        pass

    def _test(self):
        '''[Bug#860494 test] Check nss-db-gen cert validity '''
        for cert in ["broker", "ca"]:
            Expect.ping_pong(self.rs.Instances["RHUA"][0], "rpm -q rh-rhui-tools --queryformat \"%{DESCRIPTION}\\n\"", "Red Hat Update Infrastructure \(RHUI\) is a collection of technologies that.*offers cloud providers the ability to easily deploy Red Hat solutions into.*their environments. The rh-rhui-tools package has a series of tools necessary.*to configure the RHUI.")

    def _cleanup(self):
        pass

if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
