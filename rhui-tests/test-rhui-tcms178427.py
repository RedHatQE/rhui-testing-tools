#! /usr/bin/python -tt

import nose

from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *


class test_rhui_tcms178427(RHUITestcase):
    def __init__(self):
        RHUITestcase.__init__(self)
        '''[TCMS#178427 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.RHUA)

    def test_rhui_tcms178427(self):
        '''[TCMS#178427 test] Test home screen content '''
        cds_screen_items = \
            """.*l\s* list all CDS clusters and instances managed by the RHUI\s*\r\n\s*i\s* display detailed information on a CDS cluster\s*\r\n\s*a\s* register \(add\) a new CDS instance\s*\r\n\s*m\s* move CDS\(s\) to a different cluster\s*\r\n\s*d\s* unregister \(delete\) a CDS instance from the RHUI\s*\r\n\s*s\s* associate a repository with a CDS cluster\s*\r\n\s*u\s* unassociate a repository from a CDS cluster\s*\r\n.*=> """
        Expect.ping_pong(self.rs.RHUA, "rhui-manager", "rhui \(home\) => ")
        Expect.ping_pong(self.rs.RHUA, "c", cds_screen_items)
        Expect.ping_pong(self.rs.RHUA, 'q', "root@")

    def __del__(self):
        RHUITestcase.__del__()


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
