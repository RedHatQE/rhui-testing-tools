#! /usr/bin/python -tt

import nose

from patchwork.expect import *
from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_cds import *


class test_bug_871497(RHUITestcase):
    def _setup(self):
        '''[Bug#871497 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.Instances["RHUA"][0])

        '''[Bug#871497 setup] Add cds'''
        RHUIManagerCds.add_cds(self.rs.Instances["RHUA"][0], "Cluster1", self.rs.Instances["CDS"][0].private_hostname)

    def _test(self):
        '''[Bug#871497 test] Check cds list output '''
        RHUIManager.screen(self.rs.Instances["RHUA"][0], "cds")
        Expect.ping_pong(self.rs.Instances["RHUA"][0], "l", "-= RHUI Content Delivery Server Clusters =-.*Content Delivery Servers")

    def _cleanup(self):
        '''[Bug#871497 setup] Remove cds'''
        RHUIManagerCds.delete_cds(self.rs.Instances["RHUA"][0], "Cluster1", [self.rs.Instances["CDS"][0].private_hostname])

if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
