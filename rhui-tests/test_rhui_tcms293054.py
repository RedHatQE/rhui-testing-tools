#! /usr/bin/python -tt

import nose
import re

from stitches.expect import *
from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_cds import *
from rhuilib.pulp_admin import *
from rhuilib.cds import *

class test_tcms_293054(RHUITestcase, RHUI_has_two_CDSes):
    def _setup(self):
        '''[TCMS#293054 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.Instances["RHUA"][0])

        '''[TCMS#293054 setup] Add cdses'''
        RHUIManagerCds.add_cds(self.rs.Instances["RHUA"][0], "Cluster1", self.rs.Instances["CDS"][0].private_hostname)
        RHUIManagerCds.add_cds(self.rs.Instances["RHUA"][0], "Cluster1", self.rs.Instances["CDS"][1].private_hostname)
        
        '''[TCMS#293054 setup] Remove a cds'''
        RHUIManagerCds.delete_cds(self.rs.Instances["RHUA"][0], "Cluster1", [self.rs.Instances["CDS"][0].private_hostname])

    def _test(self):
        '''[TCMS#293054 test] Check CDS info screen'''
        rhui_cds = RhuiCds(
                           hostname=self.rs.Instances["CDS"][1].private_hostname,
                           description='RHUI CDS',
                           cluster='Cluster1',
                           repos=[])

        nose.tools.assert_equal(RHUIManagerCds.info(self.rs.Instances["RHUA"][0], ["Cluster1"]), [rhui_cds])

        '''[TCMS#293054 test] Check pulp-admin and rhui cluster info are the same'''
        nose.tools.assert_equal(PulpAdmin.cds_list(self.rs.Instances["RHUA"][0]), RHUIManagerCds.info(self.rs.Instances["RHUA"][0], ['Cluster1']))

    def _cleanup(self):
        '''[TCMS#293054 cleanup] Remove cds'''
        RHUIManagerCds.delete_cds(self.rs.Instances["RHUA"][0], "Cluster1", [self.rs.Instances["CDS"][1].private_hostname])

if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
