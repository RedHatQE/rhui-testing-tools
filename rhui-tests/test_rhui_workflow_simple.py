#! /usr/bin/python -tt

import nose

from rhuilib.util import *
from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_cds import *
from rhuilib.rhuimanager_client import *
from rhuilib.rhuimanager_repo import *
from rhuilib.rhuimanager_sync import *
from rhuilib.rhuimanager_identity import *
from rhuilib.rhuimanager_users import *
from rhuilib.rhuimanager_entitlements import *


class test_workflow_simple(RHUITestcase, RHUI_has_RH_cert):
    def _setup(self):
        '''[Simple Workflow setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.Instances["RHUA"][0])

    def _test(self):
        '''[Simple Workflow test] Add cdses '''
        for cds in self.rs.Instances["CDS"]:
            RHUIManagerCds.add_cds(self.rs.Instances["RHUA"][0], "Cluster1", cds.private_hostname)

        '''[Simple Workflow test] Remove rhui configuration rpm from client '''
        for cli in self.rs.Instances["CLI"]:
            Util.remove_conf_rpm(cli)

        '''[Simple Workflow test] Create custom repo '''
        RHUIManagerRepo.add_custom_repo(self.rs.Instances["RHUA"][0], "repo1")
        RHUIManagerRepo.add_custom_repo(self.rs.Instances["RHUA"][0], "repo2")

        '''[Simple Workflow test] Associate custom repo with cluster '''
        RHUIManagerCds.associate_repo_cds(self.rs.Instances["RHUA"][0], "Cluster1", ["repo1", "repo2"])

        '''[Simple Workflow test] Upload content to custom repo '''
        RHUIManagerRepo.upload_content(self.rs.Instances["RHUA"][0], ["repo1", "repo2"], "/etc/rhui/confrpm")

        '''[Simple Workflow test] Sync cdses '''
        cdslist = []
        for cds in self.rs.Instances["CDS"]:
            cdslist.append(cds.private_hostname)
        RHUIManagerSync.sync_cds(self.rs.Instances["RHUA"][0], cdslist)

        '''[Simple Workflow test] Generate entitlement certificate '''
        RHUIManagerClient.generate_ent_cert(self.rs.Instances["RHUA"][0], "Cluster1", ["repo1"], "cert-repo1", "/root/", validity_days="", cert_pw=None)

        #'''[Simple Workflow test] Sync cluster '''
        ##it's impossible to do cluster sync and individual cds sync at the same moment
        ##RHUIManagerSync.sync_cluster(self.rs.Instances["RHUA"][0],["Cluster1"])

        '''[Simple Workflow test] Upload RH content certificate '''
        RHUIManagerEntitlements.upload_content_cert(self.rs.Instances["RHUA"][0], self.cert)

        #'''[Simple Workflow test] Add rh repo by product '''
        ## skipping as this repos are really big
        ## RHUIManagerRepo.add_rh_repo_by_product(self.rs.Instances["RHUA"][0], ["Red Hat Enterprise Linux 6 Server - Supplementary from RHUI \(RPMs\)", "Red Hat Enterprise Linux 6 Server from RHUI \(RPMs\)"])

        '''[Simple Workflow test] Add rh repo by repo '''
        RHUIManagerRepo.add_rh_repo_by_repo(self.rs.Instances["RHUA"][0], ["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])

        ## '''[Simple Workflow test] Add all rh products '''
        ## RHUIManagerRepo.add_rh_repo_all(self.rs.Instances["RHUA"][0])

        '''[Simple Workflow test] Syncronize repo '''
        self._sync_repo(["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])
        self._sync_cds([self.rs.Instances["CDS"][0].private_hostname])

        '''[Simple Workflow test] Associate rh repo with cds '''
        RHUIManagerCds.associate_repo_cds(self.rs.Instances["RHUA"][0], "Cluster1", ["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])

        '''[Simple Workflow test] Generate entitlement certificate with rh content '''
        RHUIManagerClient.generate_ent_cert(self.rs.Instances["RHUA"][0], "Cluster1", ["repo1", "Red Hat Update Infrastructure 2 \(RPMs\)"], "cert-repo1", "/root/", validity_days="", cert_pw=None)

        '''[Simple Workflow test] Create configuration rpm '''
        RHUIManagerClient.create_conf_rpm(self.rs.Instances["RHUA"][0], "Cluster1", self.rs.Instances["CDS"][0].private_hostname, "/root", "/root/cert-repo1.crt", "/root/cert-repo1.key", "repo1", "3.0")

        '''[Simple Workflow test] Install configuration rpm to client'''
        Util.install_rpm_from_rhua(self.rs.Instances["RHUA"][0], self.rs.Instances["CLI"][0], "/root/repo1-3.0/build/RPMS/noarch/repo1-3.0-1.noarch.rpm")

        '''[Simple Workflow test] Generate new identity '''
        RHUIManagerIdentity.generate_new(self.rs.Instances["RHUA"][0])

        '''[Simple Workflow test] Change password '''
        RHUIManagerUsers.change_password(self.rs.Instances["RHUA"][0], "admin", "admin2")
        RHUIManagerUsers.change_password(self.rs.Instances["RHUA"][0], "admin", "admin")

    def _cleanup(self):
        '''[Simple Workflow cleanup] Remove cdses '''
        for cds in self.rs.Instances["CDS"]:
            RHUIManagerCds.delete_cds(self.rs.Instances["RHUA"][0], "Cluster1", [cds.private_hostname])

        '''[Simple Workflow cleanup] Delete custom repos '''
        RHUIManagerRepo.delete_repo(self.rs.Instances["RHUA"][0], ["repo1", "repo2", "Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])

        '''[Simple Workflow cleanup] Remove rh certificate '''
        RHUIManager.remove_rh_certs(self.rs.Instances["RHUA"][0])


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
