#! /usr/bin/python -tt

import argparse
import nose

from rhuilib.rhuisetup import *
from rhuilib.rhuimanager import *


class test_rhui_cds_management_screen(object):
    def __init__(self):
        argparser = argparse.ArgumentParser(description='RHUI CDS Management Screen')
        args = argparser.parse_args()
        self.rs = RHUIsetup()
        self.rs.setup_from_rolesfile()

    def __del__(self):
        self.rs.__del__()

    def test_01_initial_run(self):
        ''' Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.RHUA)

    def test_02_home_screen(self):
        ''' Test home screen content '''
        cds_screen_items = \
            """.*l\s* list all CDS clusters and instances managed by the RHUI\s*\r\n\s*i\s* display detailed information on a CDS cluster\s*\r\n\s*a\s* register \(add\) a new CDS instance\s*\r\n\s*m\s* move CDS\(s\) to a different cluster\s*\r\n\s*d\s* unregister \(delete\) a CDS instance from the RHUI\s*\r\n\s*s\s* associate a repository with a CDS cluster\s*\r\n\s*u\s* unassociate a repository from a CDS cluster\s*\r\n.*=> """
        Expect.enter(self.rs.RHUA, "rhui-manager")
        Expect.expect(self.rs.RHUA, "rhui \(home\) => ")
        Expect.enter(self.rs.RHUA, "c")
        Expect.expect(self.rs.RHUA, cds_screen_items)
        Expect.enter(self.rs.RHUA, 'q')


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
