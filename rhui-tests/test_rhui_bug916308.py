#! /usr/bin/python -tt

import nose
import time

from rhuilib.util import *
from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_cds import *
from rhuilib.rhuimanager_repo import *
from rhuilib.rhuimanager_sync import *
from rhuilib.rhuimanager_entitlements import *


class test_bug_916308(RHUITestcase, RHUI_has_RH_cert):
    def _setup(self):
        '''[Bug#916308 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.Instances["RHUA"][0])

        '''[Bug#916308 setup] Add cds '''
        RHUIManagerCds.add_cds(self.rs.Instances["RHUA"][0], "Cluster1", self.rs.Instances["CDS"][0].private_hostname)

        '''[Bug#916308 setup] Upload RH content certificate '''
        RHUIManagerEntitlements.upload_content_cert(self.rs.Instances["RHUA"][0], self.cert)

        '''[Bug#916308 setup] Add rh repo '''
        RHUIManagerRepo.add_rh_repo_by_repo(self.rs.Instances["RHUA"][0], ["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])

        '''[Bug#916308 setup] Associate repos with cluster '''
        RHUIManagerCds.associate_repo_cds(self.rs.Instances["RHUA"][0], "Cluster1", ["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])

        '''[Bug#916308 setup] Sync RH repo '''
        self._sync_repo(["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])

        '''[Bug#916308 setup] Sync cds '''
        self._sync_cds([self.rs.Instances["CDS"][0].private_hostname])

    def _test(self):
        '''[Bug#916308 test] Get modify time for repo '''
        Expect.enter(self.rs.Instances["CDS"][0], 'echo "###START###" && stat /var/lib/pulp-cds/repos/content/dist/rhel/rhui/server/6/6Server/x86_64/rhui/2/os/Packages | grep ^Modify && echo "###STOP###"')

        stat_1 = Expect.match(self.rs.Instances["CDS"][0], re.compile('.*###START###\r\n(.*)\r\n###STOP###.*', re.DOTALL))[0]

        '''[Bug#916308 test] Sync cds '''
        self._sync_cds([self.rs.Instances["CDS"][0].private_hostname])

        '''[Bug#916308 test] Get modify time for repo '''
        Expect.enter(self.rs.Instances["CDS"][0], 'echo "###START###" && stat /var/lib/pulp-cds/repos/content/dist/rhel/rhui/server/6/6Server/x86_64/rhui/2/os/Packages | grep ^Modify && echo "###STOP###"')

        stat_2 = Expect.match(self.rs.Instances["CDS"][0], re.compile('.*###START###\r\n(.*)\r\n###STOP###.*', re.DOTALL))[0]
        
        '''[Bug#916308 test] Compare '''
        nose.tools.ok_(stat_1 == stat_2)

    def _cleanup(self):
        '''[Bug#916308 cleanup] Remove cds '''
        RHUIManagerCds.delete_cds(self.rs.Instances["RHUA"][0], "Cluster1", [self.rs.Instances["CDS"][0].private_hostname])

        '''[Bug#916308 cleanup] Delete RH repo '''
        RHUIManagerRepo.delete_repo(self.rs.Instances["RHUA"][0], ["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])

        '''[Bug#916308 cleanup] Remove RH certs from RHUI '''
        RHUIManager.remove_rh_certs(self.rs.Instances["RHUA"][0])


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
