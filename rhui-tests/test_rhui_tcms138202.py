#! /usr/bin/python -tt

import nose

from patchwork.expect import *
from rhuilib.rhui_testcase import *


class test_tcms_138202(RHUITestcase):
    def _setup(self):
        pass

    def _test(self):
        """[TCMS#138202 test] checking selinux on RHUA and CDS instances"""
        for instance in [self.rs.Instances["RHUA"][0]] + self.rs.Instances["CDS"]:
            Expect.ping_pong(instance, 'cat /etc/sysconfig/selinux | grep "SELINUX=[^ ]"', 'SELINUX=enforcing')
            Expect.ping_pong(instance, 'getenforce', 'Enforcing')
            Expect.ping_pong(instance, 'grep "avc:" /var/log/audit/audit.log | wc -l', "0")

    def _cleanup(self):
        pass

if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
