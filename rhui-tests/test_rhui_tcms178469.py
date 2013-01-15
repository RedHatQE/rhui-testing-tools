#! /usr/bin/python -tt

import nose

from rhuilib.util import *
from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_cds import *
from rhuilib.rhuimanager_client import *
from rhuilib.rhuimanager_repo import *
from rhuilib.rhuimanager_sync import *


class test_tcms_178469(RHUITestcase, RHUI_has_two_CDSes):
    def _setup(self):
        '''[TCMS#178469 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.Instances["RHUA"][0])

        '''[TCMS#178469 setup] Add cdses '''
        RHUIManagerCds.add_cds(self.rs.Instances["RHUA"][0], "Cluster1", self.rs.Instances["CDS"][0].private_hostname)
        RHUIManagerCds.add_cds(self.rs.Instances["RHUA"][0], "Cluster2", self.rs.Instances["CDS"][1].private_hostname)

        '''[TCMS#178469 setup] Create custom repo '''
        self.rs.Instances["RHUA"][0].sftp.put("/usr/share/rhui-testing-tools/testing-data/public.key", "/root/public.key")
        RHUIManagerRepo.add_custom_repo(self.rs.Instances["RHUA"][0], "repo1", entitlement="y", custom_gpg="/root/public.key")

        '''[TCMS#178469 setup] Associate custom repos with cluster '''
        RHUIManagerCds.associate_repo_cds(self.rs.Instances["RHUA"][0], "Cluster1", ["repo1"])
        RHUIManagerCds.associate_repo_cds(self.rs.Instances["RHUA"][0], "Cluster2", ["repo1"])

        '''[TCMS#178469 setup] Upload signed rpm to custom repo '''
        self.rs.Instances["RHUA"][0].sftp.put("/usr/share/rhui-testing-tools/testing-data/custom-signed-rpm-1-0.1.fc17.noarch.rpm", "/root/custom-signed-rpm-1-0.1.fc17.noarch.rpm")
        RHUIManagerRepo.upload_content(self.rs.Instances["RHUA"][0], ["repo1"], "/root/custom-signed-rpm-1-0.1.fc17.noarch.rpm")

        '''[TCMS#178469 setup] Upload unsigned rpm to custom repo '''
        self.rs.Instances["RHUA"][0].sftp.put("/usr/share/rhui-testing-tools/testing-data/custom-unsigned-rpm-1-0.1.fc17.noarch.rpm", "/root/custom-unsigned-rpm-1-0.1.fc17.noarch.rpm")
        RHUIManagerRepo.upload_content(self.rs.Instances["RHUA"][0], ["repo1"], "/root/custom-unsigned-rpm-1-0.1.fc17.noarch.rpm")

        '''[TCMS#178469 setup] Sync cdses '''
        self._sync_cds([self.rs.Instances["CDS"][0].private_hostname, self.rs.Instances["CDS"][1].private_hostname])

    def _test(self):
        '''[TCMS#178469 test] Check repo content on cdses '''
        for cds in self.rs.Instances["CDS"]:
            Expect.ping_pong(cds, "test -f /var/lib/pulp-cds/repos/repo1/custom-signed-rpm-1-0.1.fc17.noarch.rpm && echo SUCCESS", "[^ ]SUCCESS")

        '''[TCMS#178469 test] Delete custom repos '''
        RHUIManagerRepo.delete_repo(self.rs.Instances["RHUA"][0], ["repo1"])

        '''[TCMS#178469 test] Sync cdses '''
        self._sync_cds([self.rs.Instances["CDS"][0].private_hostname, self.rs.Instances["CDS"][1].private_hostname])

        '''[TCMS#178469 test] Check repo content on cdses '''
        for cds in self.rs.Instances["CDS"]:
            Expect.ping_pong(cds, "test -f /var/lib/pulp-cds/repos/repo1/custom-signed-rpm-1-0.1.fc17.noarch.rpm || echo FAILURE", "[^ ]FAILURE")

    def _cleanup(self):
        '''[TCMS#178469 cleanup] Remove cdses '''
        RHUIManagerCds.delete_cds(self.rs.Instances["RHUA"][0], "Cluster1", [self.rs.Instances["CDS"][0].private_hostname])
        RHUIManagerCds.delete_cds(self.rs.Instances["RHUA"][0], "Cluster2", [self.rs.Instances["CDS"][1].private_hostname])


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
