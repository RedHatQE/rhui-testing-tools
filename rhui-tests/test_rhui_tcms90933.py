#! /usr/bin/python -tt

import nose
import time

from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_cds import *
from rhuilib.rhuimanager_repo import *
from rhuilib.rhuimanager_sync import *

class test_rhui_tcms90933(RHUITestcase):
    def _setup(self):
        '''[TCMS#90933 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.Instances["RHUA"][0])

        '''[TCMS#90933 setup] Add cds'''
        RHUIManagerCds.add_cds(self.rs.Instances["RHUA"][0], "Cluster1", self.rs.Instances["CDS"][0].private_hostname)
        
        '''[TCMS#90933 setup] Sync cds'''
        self._sync_cds([self.rs.Instances["CDS"][0].private_hostname])

    def _test(self):
        '''[TCMS#90933 test] Check cds status '''
        sync = RHUIManagerSync.get_cds_status(self.rs.Instances["RHUA"][0], self.rs.Instances["CDS"][0].private_hostname)
        nose.tools.assert_equal(sync[3], "Success")

    def _cleanup(self):
        '''[TCMS#90933 cleanup] Remove cds '''
        RHUIManagerCds.delete_cds(self.rs.Instances["RHUA"][0], "Cluster1", [self.rs.Instances["CDS"][0].private_hostname])

if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
