#! /usr/bin/python -tt

import nose

from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_cds import *
from rhuilib.rhuimanager_client import *
from rhuilib.rhuimanager_repo import *


class test_bug_846386(RHUITestcase):
    def _setup(self):
        '''[Bug#846386 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.Instances["RHUA"][0])

        '''[Bug#846386 setup] Add cds '''
        RHUIManagerCds.add_cds(self.rs.Instances["RHUA"][0], "Cluster1", self.rs.Instances["CDS"][0].private_hostname)

        '''[Bug#846386 setup] Create protected repo '''
        RHUIManagerRepo.add_custom_repo(self.rs.Instances["RHUA"][0], "custom_repo_1")

        '''[Bug#846386 setup] Create unprotected repo '''
        RHUIManagerRepo.add_custom_repo(self.rs.Instances["RHUA"][0], "custom_repo_2", entitlement="n")

        '''[Bug#846386 setup] Upload content to unprotected repo '''
        RHUIManagerRepo.upload_content(self.rs.Instances["RHUA"][0], ["custom_repo_2"], "/etc/rhui/confrpm")

        '''[Bug#846386 setup] Associate cdses with cluster '''
        RHUIManagerCds.associate_repo_cds(self.rs.Instances["RHUA"][0], "Cluster1", ["custom_repo_1", "custom_repo_2"])

    def _test(self):
        '''[Bug#846386 test] Generate entitlement certificate '''
        RHUIManagerClient.generate_ent_cert(self.rs.Instances["RHUA"][0], "Cluster1", ["custom_repo_1"], "cert-repo1", "/root/", validity_days="", cert_pw=None)

        '''[Bug#846386 test] Create configuration rpm '''
        RHUIManagerClient.create_conf_rpm(self.rs.Instances["RHUA"][0], "Cluster1", self.rs.Instances["CDS"][0].private_hostname, "/root", "/root/cert-repo1.crt", "/root/cert-repo1.key", "repo1", "3.0", ["custom_repo_2"])

    def _cleanup(self):
        '''[Bug#846386 clenup] Remove cds '''
        RHUIManagerCds.delete_cds(self.rs.Instances["RHUA"][0], "Cluster1", [self.rs.Instances["CDS"][0].private_hostname])

        '''[Bug#846386 cleanup] Delete custom repos '''
        RHUIManagerRepo.delete_repo(self.rs.Instances["RHUA"][0], ["custom_repo_1", "custom_repo_2"])


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
