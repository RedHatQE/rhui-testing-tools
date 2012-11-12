#! /usr/bin/python -tt

import nose

from rhuilib.expect import *
from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_cds import *
from rhuilib.rhuimanager_repo import *
from rhuilib.util import *


class test_bug_789054(RHUITestcase):
    def _setup(self):
        '''[Bug#789054 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.RHUA)

        '''[Bug#789054 setup] Add cds '''
        RHUIManagerCds.add_cds(self.rs.RHUA, "Cluster1", self.rs.CDS[0].private_hostname)

        '''[Bug#789054 setup] Create custom repos '''
        RHUIManagerRepo.add_custom_repo(self.rs.RHUA, "repo1")
        RHUIManagerRepo.add_custom_repo(self.rs.RHUA, "repo2")
        RHUIManagerRepo.add_custom_repo(self.rs.RHUA, "repo3")

    def _test(self):
        '''[Bug#789054 setup] Associate custom repos with cluster '''
        RHUIManagerCds.associate_repo_cds(self.rs.RHUA, "Cluster1", ["repo1", "repo2", "repo3"])

        '''[Bug#789054 test] Generate entitlement certificate '''
        RHUIManager.screen(self.rs.RHUA, "client")
        Expect.enter(self.rs.RHUA, "e")
        RHUIManager.select_one(self.rs.RHUA, "Cluster1")
        RHUIManager.select(self.rs.RHUA, ["repo1", "repo2"])
        Expect.expect(self.rs.RHUA, "Name of the certificate.*contained with it:")
        Expect.ping_pong(self.rs.RHUA, "cert with spaces", "The name can not contain spaces")
        Expect.enter(self.rs.RHUA, "cert_without_spaces")
        Expect.expect(self.rs.RHUA, "Local directory in which to save the generated certificate.*:")
        Expect.enter(self.rs.RHUA, "/tmp")
        Expect.expect(self.rs.RHUA, "Number of days the certificate should be valid.*:")
        Expect.enter(self.rs.RHUA, "")
        RHUIManager.proceed_with_check(self.rs.RHUA, "Repositories to be included in the entitlement certificate:", ["repo1", "repo2"], ["Custom Entitlements", "Red Hat Repositories"])
        Expect.expect(self.rs.RHUA, "Enter pass phrase for.*:")
        Expect.enter(self.rs.RHUA, Util.get_ca_password(self.rs.RHUA))
        RHUIManager.quit(self.rs.RHUA)

    def _cleanup(self):
        '''[Bug#789054 cleanup] Remove cds '''
        RHUIManagerCds.delete_cds(self.rs.RHUA, "Cluster1", [self.rs.CDS[0].private_hostname])

        '''[Bug#789054 cleanup] Delete custom repos '''
        RHUIManagerRepo.delete_repo(self.rs.RHUA, ["repo1", "repo2", "repo3"])


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
