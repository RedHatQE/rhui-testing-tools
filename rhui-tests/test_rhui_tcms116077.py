#! /usr/bin/python -tt

import nose

from rhuilib.util import *
from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_identity import *
from rhuilib.rhuimanager_cds import *
from rhuilib.rhuimanager_repo import *


class test_tcms_116077(RHUITestcase):
    def _setup(self):
        """[TCMS#116077 setup] Do initial rhui-manager run"""
        RHUIManager.initial_run(self.rs.Instances["RHUA"][0])

        """[TCMS#116076 setup] Generate new identity"""
        RHUIManagerIdentity.generate_new(self.rs.Instances["RHUA"][0])

    def _test(self):
        '''[TCMS#116077 test] Add cdses '''
        RHUIManagerCds.add_cds(self.rs.Instances["RHUA"][0], "Cluster1", self.rs.Instances["CDS"][0].private_hostname)

        '''[TCMS#116077 test] Create custom repo '''
        RHUIManagerRepo.add_custom_repo(self.rs.Instances["RHUA"][0], "repo1")

        '''[TCMS#116077 test] Associate custom repo with cluster '''
        RHUIManagerCds.associate_repo_cds(self.rs.Instances["RHUA"][0], "Cluster1", ["repo1"])

        '''[TCMS#116077 test] Upload content to custom repo '''
        RHUIManagerRepo.upload_content(self.rs.Instances["RHUA"][0], ["repo1"], "/etc/rhui/confrpm")

        '''[TCMS#116077 test] Sync cdses '''
        self._sync_cds([self.rs.Instances["CDS"][0].private_hostname])

    def _cleanup(self):
        '''[TCMS#116077 cleanup] Remove cds '''
        RHUIManagerCds.delete_cds(self.rs.Instances["RHUA"][0], "Cluster1", [self.rs.Instances["CDS"][0].private_hostname])

        '''[TCMS#116077 cleanup] Delete custom repo '''
        RHUIManagerRepo.delete_repo(self.rs.Instances["RHUA"][0], ["repo1"])


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
