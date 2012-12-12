#! /usr/bin/python -tt

import nose
import re

from patchwork.expect import *
from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_cds import *
from rhuilib.pulp_admin import *
from rhuilib.cds import *


class test_tcms_178428(RHUITestcase):
    def _setup(self):
        '''[TCMS#178428 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.Instances["RHUA"][0])

        '''[TCMS#178428 setup] Add cds '''
        RHUIManagerCds.add_cds(self.rs.Instances["RHUA"][0], "Cluster1", self.rs.Instances["CDS"][0].private_hostname)

    def _test(self):
        '''[TCMS#178428 test] check the cds info screen'''
        rhui_cds = RhuiCds(name='cds1.example.com',
                           hostname='cds1.example.com',
                           description='RHUI CDS',
                           cluster='Cluster1',
                           repos=[],
                           client_hostname='cds1.example.com')

        nose.tools.assert_equal(RHUIManagerCds.info(self.rs.Instances["RHUA"][0], ["Cluster1"]), [rhui_cds])

        '''[TCMS#178428 test] Check pulp-admin cds list '''
        cdses = PulpAdmin.cds_list(self.rs.Instances["RHUA"][0])

        nose.tools.eq_(cdses, [rhui_cds])

    def _cleanup(self):
         '''[TCMS#178428 cleanup] remove a cds from single node cluster'''
         RHUIManagerCds.delete_cds(self.rs.Instances["RHUA"][0], "Cluster1", [self.rs.Instances["CDS"][0].private_hostname])

if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
