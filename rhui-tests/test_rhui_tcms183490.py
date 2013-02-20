#! /usr/bin/python -tt

import nose
import re

from patchwork.expect import *
from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_cds import *
from rhuilib.pulp_admin import *
from rhuilib.cds import *


class test_tcms_183490(RHUITestcase, RHUI_has_two_CDSes):
    def _setup(self):
        '''[TCMS#183490 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.Instances["RHUA"][0])

        '''[TCMS#183490 setup] Add cdses'''
        RHUIManagerCds.add_cds(self.rs.Instances["RHUA"][0], "Cluster1", self.rs.Instances["CDS"][0].private_hostname)
        RHUIManagerCds.add_cds(self.rs.Instances["RHUA"][0], "Cluster1", self.rs.Instances["CDS"][1].private_hostname)
        
        '''[TCMS#183490 setup] Move a cds'''
        RHUIManagerCds.move_cds(self.rs.Instances["RHUA"][0], [self.rs.Instances["CDS"][0].private_hostname], 'Cluster2')

    def _test(self):
        '''[TCMS#183490 test] Check the cdses info screen'''
        rhui_cds0 = RhuiCds(
                           hostname=self.rs.Instances["CDS"][0].private_hostname,
                           description='RHUI CDS',
                           cluster='Cluster2',
                           repos=[])
                           
        rhui_cds1 = RhuiCds(
                           hostname=self.rs.Instances["CDS"][1].private_hostname,
                           description='RHUI CDS',
                           cluster='Cluster1',
                           repos=[])

        nose.tools.assert_equal(sorted(RHUIManagerCds.info(self.rs.Instances["RHUA"][0], ["Cluster1", "Cluster2"])), sorted([rhui_cds0, rhui_cds1]))

        '''[TCMS#183490 test] Check pulp-admin and rhui cluster info are the same'''
        nose.tools.assert_equals(sorted(PulpAdmin.cds_list(self.rs.Instances["RHUA"][0])), sorted(RHUIManagerCds.info(self.rs.Instances["RHUA"][0], ['Cluster1', 'Cluster2'])))

    def _cleanup(self):
        '''[TCMS#183490 cleanup] Remove a cdses'''
        RHUIManagerCds.delete_cds(self.rs.Instances["RHUA"][0], "Cluster1", [self.rs.Instances["CDS"][1].private_hostname])
        RHUIManagerCds.delete_cds(self.rs.Instances["RHUA"][0], "Cluster2", [self.rs.Instances["CDS"][0].private_hostname])

if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
