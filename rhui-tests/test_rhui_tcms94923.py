#! /usr/bin/python -tt

import nose

from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_cds import *


class test_tcms_94923(RHUITestcase):
    def _setup(self):
        '''[TCMS#94923 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.Instances["RHUA"][0])

        '''[TCMS#94923 setup] Add cds '''
        RHUIManagerCds.add_cds(self.rs.Instances["RHUA"][0], "Cluster1", self.rs.Instances["CDS"][0].private_hostname)

    def _test(self):
        '''[TCMS#94923 test] Stop goferd '''
        Expect.ping_pong(self.rs.Instances["CDS"][0], "service goferd stop && echo SUCCESS", "[^ ]SUCCESS")

        '''[TCMS#94923 test] Forcibly remove CDS '''
        RHUIManagerCds.delete_cds(self.rs.Instances["RHUA"][0], "Cluster1", [self.rs.Instances["CDS"][0].private_hostname], True)

        '''[TCMS#94923 test] Check cds list '''
        if not RHUIManagerCds.list(self.rs.Instances["RHUA"][0]).startswith("No CDS instances are registered"):
            assert False

        '''[TCMS#94923 test] Remove cds password '''
        Expect.ping_pong(self.rs.Instances["CDS"][0], "rm -f /var/lib/pulp-cds/.gofer/secret && echo SUCCESS", "[^ ]SUCCESS")

        '''[TCMS#94923 test] Start goferd '''
        Expect.ping_pong(self.rs.Instances["CDS"][0], "service goferd start && echo SUCCESS", "[^ ]SUCCESS")

        '''[TCMS#94923 test] Add cds '''
        RHUIManagerCds.add_cds(self.rs.Instances["RHUA"][0], "Cluster1", self.rs.Instances["CDS"][0].private_hostname)

    def _cleanup(self):
        '''[TCMS#94923 cleanup] Remove cds '''
        RHUIManagerCds.delete_cds(self.rs.Instances["RHUA"][0], "Cluster1", [self.rs.Instances["CDS"][0].private_hostname])

if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
