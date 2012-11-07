#! /usr/bin/python -tt

import nose

from rhuilib.expect import *
from rhuilib.rhui_testcase import *


class test_tcms_54561(RHUITestcase):
    def test_01_check_selinux(self):
        """[TCMS#54561 test] checking selinux on RHUA and CDS instances"""
        for instance in [self.rs.RHUA] + self.rs.CDS:
            Expect.ping_pong(instance, 'getenforce', 'Enforcing')
            Expect.ping_pong(instance, 'cat /etc/sysconfig/selinux | grep "SELINUX=[^ ]"', 'SELINUX=enforcing')


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
