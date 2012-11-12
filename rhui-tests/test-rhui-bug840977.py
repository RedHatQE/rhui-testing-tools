#! /usr/bin/python -tt

import nose

from rhuilib.util import *
from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_cds import *
from rhuilib.rhuimanager_repo import *


class test_bug_840977(RHUITestcase):
    def _setup(self):
        '''[Bug#840977 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.RHUA)

        '''[Bug#840977 setup] Add cds '''
        RHUIManagerCds.add_cds(self.rs.RHUA, "Cluster1", self.rs.CDS[0].private_hostname)

        '''[Bug#840977 setup] Create protected repo '''
        RHUIManagerRepo.add_custom_repo(self.rs.RHUA, "custom_repo_1")

        '''[Bug#840977 setup] Create unprotected repo '''
        RHUIManagerRepo.add_custom_repo(self.rs.RHUA, "custom_repo_2", entitlement="n")

    def _test(self):
        '''[Bug#840977 test] Test repos assignment '''
        RHUIManager.screen(self.rs.RHUA, "cds")
        Expect.enter(self.rs.RHUA, "i")
        RHUIManager.select(self.rs.RHUA, ["Cluster1"])
        Expect.expect(self.rs.RHUA, "Repositories.*\(None\).*rhui \(cds\) =>")
        Expect.ping_pong(self.rs.RHUA, "q", "root@")

    def _cleanup(self):
        '''[Bug#840977 cleanup] Remove cds '''
        RHUIManagerCds.delete_cds(self.rs.RHUA, "Cluster1", [self.rs.CDS[0].private_hostname])

        '''[Bug#840977 cleanup] Delete custom repos '''
        RHUIManagerRepo.delete_repo(self.rs.RHUA, ["custom_repo_1", "custom_repo_2"])


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
