#! /usr/bin/python -tt

import nose

from rhuilib.util import *
from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_repo import *
from rhuilib.rhuimanager_sync import *
from rhuilib.rhuimanager_entitlements import *


class test_bug_847306(RHUITestcase, RHUI_has_RH_cert):
    def _setup(self):
        '''[Bug#847306 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.Instances["RHUA"][0])

        '''[Bug#847306 setup] Upload RH content certificate '''
        RHUIManagerEntitlements.upload_content_cert(self.rs.Instances["RHUA"][0], self.cert)

        '''[Bug#847306 setup] Add rh repo '''
        RHUIManagerRepo.add_rh_repo_all(self.rs.Instances["RHUA"][0])

    def _test(self):
        '''[Bug#847306 test] Delete repos '''
        RHUIManager.screen(self.rs.Instances["RHUA"][0], "repo")
        Expect.enter(self.rs.Instances["RHUA"][0], "d")
        Expect.expect(self.rs.Instances["RHUA"][0], "Enter value")
        Expect.enter(self.rs.Instances["RHUA"][0], "a")

        Expect.expect(self.rs.Instances["RHUA"][0], "Enter value")
        Expect.enter(self.rs.Instances["RHUA"][0], "c")

        Expect.expect(self.rs.Instances["RHUA"][0], "Proceed")
        Expect.enter(self.rs.Instances["RHUA"][0], "y")
        Expect.expect(self.rs.Instances["RHUA"][0], "rhui \(repo\) =>", 60)

        Expect.enter(self.rs.Instances["RHUA"][0], "<")
        Expect.expect(self.rs.Instances["RHUA"][0], "rhui \(home\) =>")

        Expect.enter(self.rs.Instances["RHUA"][0], "s")

        Expect.expect(self.rs.Instances["RHUA"][0], "rhui \(sync\) =>")

        '''[Bug#847306 test] Try sync screen '''
        Expect.enter(self.rs.Instances["RHUA"][0], "sr")
        Expect.expect(self.rs.Instances["RHUA"][0], "Select one or more repositories.*for more commands:", 60)
        Expect.enter(self.rs.Instances["RHUA"][0], "c")
        Expect.expect(self.rs.Instances["RHUA"][0], "The following repositories will be scheduled for synchronization:")
        Expect.enter(self.rs.Instances["RHUA"][0], "y")
        RHUIManager.quit(self.rs.Instances["RHUA"][0])

    def _cleanup(self):
        '''[Bug#847306 cleanup] Remove RH certificate '''
        RHUIManager.remove_rh_certs(self.rs.Instances["RHUA"][0])


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
