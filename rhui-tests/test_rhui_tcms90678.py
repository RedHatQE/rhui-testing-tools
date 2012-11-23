#! /usr/bin/python -tt

import nose

from rhuilib.util import *
from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_cds import *
from rhuilib.rhuimanager_client import *
from rhuilib.rhuimanager_repo import *
from rhuilib.rhuimanager_sync import *


class test_tcms_90678(RHUITestcase):
    def _setup(self):
        '''[TCMS#90678 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.RHUA[0])

        '''[TCMS#90678 setup] Add cdses '''
        RHUIManagerCds.add_cds(self.rs.RHUA[0], "Cluster1", self.rs.CDS[0].private_hostname)

        '''[TCMS#90678 setup] Create custom repo '''
        RHUIManagerRepo.add_custom_repo(self.rs.RHUA[0], "repo1")

        '''[TCMS#90678 setup] Associate custom repo with cluster '''
        RHUIManagerCds.associate_repo_cds(self.rs.RHUA[0], "Cluster1", ["repo1"])

        '''[TCMS#90678 setup] Upload content to custom repo '''
        RHUIManagerRepo.upload_content(self.rs.RHUA[0], ["repo1"], "/etc/rhui/confrpm")

        '''[TCMS#90678 setup] Sync cdses '''
        self._sync_cds([self.rs.CDS[0].private_hostname])

    def _test(self):
        '''[TCMS#90678 test] Remove cds '''
        RHUIManagerCds.delete_cds(self.rs.RHUA[0], "Cluster1", [self.rs.CDS[0].private_hostname])

        '''[TCMS#90678 test] Check that there is no gofer secret '''
        Expect.ping_pong(self.rs.CDS[0], "[ ! -f /var/lib/pulp-cds/.gofer/secret ] && echo SUCCESS", "[^ ]SUCCESS")

    def _cleanup(self):
        '''[TCMS#90678 cleanup] Delete custom repo '''
        RHUIManagerRepo.delete_repo(self.rs.RHUA[0], ["repo1"])

if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
