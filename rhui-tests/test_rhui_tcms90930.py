#! /usr/bin/python -tt

import nose
import re

from rhuilib.util import *
from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_repo import *
from rhuilib.rhuimanager_sync import *
from rhuilib.pulp_admin import *

class test_rhui_tcms90930(RHUITestcase):
    def _setup(self):
        '''[TCMS#90930 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.Instances["RHUA"][0])

        '''[TCMS#90930 setup] Upload RH content certificate '''
        RHUIManagerEntitlements.upload_content_cert(self.rs.Instances["RHUA"][0], self.cert)
        
        '''[TCMS#90930 setup] Create repo'''
        RHUIManagerRepo.add_rh_repo_by_repo(self.rs.Instances["RHUA"][0], ["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])

    def _test(self):
        '''[TCMS#90930 test] Check repo status'''
        sync = RHUIManagerSync.get_repo_status(self.rs.Instances["RHUA"][0], "Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)")
        nose.tools.assert_equal(sync[1], "Never")
        nose.tools.assert_equal(sync[2], "Never")

    def _cleanup(self):
        '''[TCMS#90930 cleanup] Remove repo'''
        RHUIManagerRepo.delete_repo(self.rs.Instances["RHUA"][0], ["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])
        
        '''[TCMS#90930 cleanup] Remove RH certificate from RHUI'''
        RHUIManager.remove_rh_certs(self.rs.Instances["RHUA"][0])
        
if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])

