#! /usr/bin/python -tt

import nose

from rhuilib.util import *
from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_cds import *
from rhuilib.rhuimanager_client import *
from rhuilib.rhuimanager_repo import *
from rhuilib.rhuimanager_sync import *
from rhuilib.rhuimanager_entitlements import *


class test_bug_833007(RHUITestcase):
    def _setup(self):
        '''[Bug#833007 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.Instances["RHUA"][0])

        '''[Bug#833007 setup] Add cds '''
        RHUIManagerCds.add_cds(self.rs.Instances["RHUA"][0], "Cluster1", self.rs.Instances["CDS"][0].private_hostname)

        '''[Bug#833007 setup] Remove rhui configuration rpm from client '''
        Util.remove_conf_rpm(self.rs.Instances["CLI"][0])

        '''[Bug#833007 setup] Create custom repo '''
        RHUIManagerRepo.add_custom_repo(self.rs.Instances["RHUA"][0], "repo833007", entitlement="y", redhat_gpg="n")

        '''[Bug#833007 setup] Associate repos with cluster '''
        RHUIManagerCds.associate_repo_cds(self.rs.Instances["RHUA"][0], "Cluster1", ["repo833007"])

        '''[Bug#833007 setup] Sync cds '''
        self._sync_cds([self.rs.Instances["CDS"][0].private_hostname])

        '''[Bug#833007 setup] Generate entitlement certificate '''
        RHUIManagerClient.generate_ent_cert(self.rs.Instances["RHUA"][0], "Cluster1", ["repo833007"], "cert-repo833007", "/root/", validity_days="", cert_pw=None)

        '''[Bug#833007 setup] Create configuration rpm '''
        RHUIManagerClient.create_conf_rpm(self.rs.Instances["RHUA"][0], "Cluster1", self.rs.Instances["CDS"][0].private_hostname, "/root", "/root/cert-repo833007.crt", "/root/cert-repo833007.key", "repo833007", "3.0")

        '''[Bug#833007 setup] Install configuration rpm to client '''
        Util.install_rpm_from_rhua(self.rs.Instances["RHUA"][0], self.rs.Instances["CLI"][0], "/root/repo833007-3.0/build/RPMS/noarch/repo833007-3.0-1.noarch.rpm")

    def _test(self):
        '''[Bug#833007 test] Stop CDS '''
        Expect.ping_pong(self.rs.Instances["CDS"][0], "service pulp-cds stop && echo SUCCESS", "[^ ]SUCCESS", 60)

        '''[Bug#833007 test] Installing RH rpm from RH repo to the client '''
        Expect.ping_pong(self.rs.Instances["CLI"][0], "yum repolist", "Could not contact any CDS load balancers:", 60)

    def _cleanup(self):
        '''[Bug#833007 cleanup] Start CDS '''
        Expect.ping_pong(self.rs.Instances["CDS"][0], "service pulp-cds start && echo SUCCESS", "[^ ]SUCCESS", 60)

        '''[Bug#833007 cleanup] Removing configuration rpm from the client '''
        Util.remove_conf_rpm(self.rs.Instances["CLI"][0])

        '''[Bug#833007 cleanup] Remove cds '''
        RHUIManagerCds.delete_cds(self.rs.Instances["RHUA"][0], "Cluster1", [self.rs.Instances["CDS"][0].private_hostname])

        '''[Bug#833007 cleanup] Delete custom repo '''
        RHUIManagerRepo.delete_repo(self.rs.Instances["RHUA"][0], ["repo833007"])


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
