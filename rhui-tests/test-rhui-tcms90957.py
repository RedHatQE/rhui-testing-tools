#! /usr/bin/python -tt

import nose
import time

from rhuilib.util import *
from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_cds import *


class test_tcms_90957(RHUITestcase, RHUI_has_two_CDSes):
    def _setup(self):
        '''[TCMS#90957 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.RHUA[0])

        '''[TCMS#90957 setup] Add cdses'''
        RHUIManagerCds.add_cds(self.rs.RHUA[0], "Cluster1", self.rs.CDS[0].private_hostname)
        RHUIManagerCds.add_cds(self.rs.RHUA[0], "Cluster1", self.rs.CDS[1].private_hostname)

    def _test(self):
        '''[TCMS#90957 test] Shut down CDS0 '''
        Expect.ping_pong(self.rs.CDS[0], "service pulp-cds stop && echo SUCCESS", "[^ ]SUCCESS", 60)
        time.sleep(10)

        '''[TCMS#90957 test] Test client with second cds only '''
        Expect.ping_pong(self.rs.RHUA[0], "rhui-manager status | grep '" + self.rs.CDS[0].private_hostname + " ' | grep 'DOWN' && echo SUCCESS", "[^ ]SUCCESS", 10)
        Expect.ping_pong(self.rs.RHUA[0], "rhui-manager status | grep '" + self.rs.CDS[1].private_hostname + " ' | grep 'UP' && echo SUCCESS", "[^ ]SUCCESS", 10)

        '''[TCMS#90957 test] Start CDS0 '''
        Expect.ping_pong(self.rs.CDS[0], "service pulp-cds start && echo SUCCESS", "[^ ]SUCCESS", 60)

    def _cleanup(self):
        '''[TCMS#90957 cleanup] Remove cdses '''
        RHUIManagerCds.delete_cds(self.rs.RHUA[0], "Cluster1", [self.rs.CDS[0].private_hostname, self.rs.CDS[1].private_hostname])


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
