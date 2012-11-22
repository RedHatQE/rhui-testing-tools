#! /usr/bin/python -tt

import nose

from rhuilib.util import *
from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_cds import *
from rhuilib.rhuimanager_client import *
from rhuilib.rhuimanager_repo import *
from rhuilib.rhuimanager_sync import *


class test_tcms_90676(RHUITestcase):
    def _setup(self):
        '''[TCMS#90676 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.RHUA[0])

        '''[TCMS#90676 setup] Add cdses '''
        RHUIManagerCds.add_cds(self.rs.RHUA[0], "Cluster1", self.rs.CDS[0].private_hostname)

        '''[TCMS#90676 setup] Create custom repo '''
        RHUIManagerRepo.add_custom_repo(self.rs.RHUA[0], "repo1")

        '''[TCMS#90676 setup] Associate custom repo with cluster '''
        RHUIManagerCds.associate_repo_cds(self.rs.RHUA[0], "Cluster1", ["repo1"])

        '''[TCMS#90676 setup] Upload content to custom repo '''
        RHUIManagerRepo.upload_content(self.rs.RHUA[0], ["repo1"], "/etc/rhui/confrpm")

        '''[TCMS#90676 setup] Sync cdses '''
        self._sync_cds([self.rs.CDS[0].private_hostname])

    def _test(self):
        '''[TCMS#90676 test] Backup cds password '''
        Expect.ping_pong(self.rs.CDS[0], "cat /var/lib/pulp-cds/.gofer/secret > /var/lib/pulp-cds/.gofer/secret.old && echo SUCCESS", "[^ ]SUCCESS")

        '''[TCMS#90676 test] Set wrong cds password ''' 
        Expect.ping_pong(self.rs.CDS[0], "echo d4648caf-af85-43db-858d-743c840ae928 > /var/lib/pulp-cds/.gofer/secret && echo SUCCESS", "[^ ]SUCCESS")

        '''[TCMS#90676 test] Trying to sync cds with wrong password ''' 
        RHUIManagerSync.sync_cds(self.rs.RHUA[0], [self.rs.CDS[0].private_hostname])
        cdssync = ["UP", "In Progress", "", ""]
        while cdssync[1] == "In Progress":
            time.sleep(1)
            cdssync = RHUIManagerSync.get_cds_status(self.rs.RHUA[0], self.rs.CDS[0].private_hostname)
        nose.tools.assert_equal(cdssync[3], "Error")

    def _cleanup(self):
        '''[TCMS#90676 cleanup] Restore cds passeord '''
        Expect.ping_pong(self.rs.CDS[0], "cat /var/lib/pulp-cds/.gofer/secret.old > /var/lib/pulp-cds/.gofer/secret && echo SUCCESS", "[^ ]SUCCESS")

        '''[TCMS#90676 cleanup] Remove cds '''
        RHUIManagerCds.delete_cds(self.rs.RHUA[0], "Cluster1", [self.rs.CDS[0].private_hostname])

        '''[TCMS#90676 cleanup] Delete custom repo '''
        RHUIManagerRepo.delete_repo(self.rs.RHUA[0], ["repo1"])

if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
