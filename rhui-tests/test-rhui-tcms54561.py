#! /usr/bin/python -tt

import argparse
import nose

from rhuilib.expect import *
from rhuilib.rhuisetup import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_cds import *


class test_tcms_54561(object):
    def __init__(self):
        argparser = argparse.ArgumentParser(description='RHUI TCMS testcase test-rhui-54561')
        args = argparser.parse_args()
        self.rs = RHUIsetup()
        self.rs.setup_from_rolesfile()

    def test_01_check_selinux(self):
        """checking selinux on RHUA and CDS instances"""
        for instance in [self.rs.RHUA] + self.rs.CDS:
            Expect.enter(instance, 'getenforce')
            Expect.expect(instance, 'Enforcing')
            Expect.enter(instance, 'cat /etc/sysconfig/selinux | grep "SELINUX=[^ ]"')
            Expect.expect(instance, 'SELINUX=enforcing')


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
