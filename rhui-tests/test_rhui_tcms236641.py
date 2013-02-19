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


class test_tcms_236641(RHUITestcase):
    def _setup(self):
        '''[TCMS#236641 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.Instances["RHUA"][0])

        '''[TCMS#236641 setup] Add cds '''
        RHUIManagerCds.add_cds(self.rs.Instances["RHUA"][0], "Cluster1", self.rs.Instances["CDS"][0].private_hostname)

        '''[TCMS#236641 setup] Remove rhui configuration rpm from client '''
        for cli in self.rs.Instances["CLI"]:
            Util.remove_conf_rpm(cli)

        '''[TCMS#236641 setup] Create custom repo '''
        RHUIManagerRepo.add_custom_repo(self.rs.Instances["RHUA"][0], "cp_1", entitlement="y", redhat_gpg="n")

        '''[TCMS#236641 setup] Associate repos with cluster '''
        RHUIManagerCds.associate_repo_cds(self.rs.Instances["RHUA"][0], "Cluster1", ["cp_1"])

        '''[TCMS#236641 setup] Sync cds '''
        self._sync_cds([self.rs.Instances["CDS"][0].private_hostname])

        '''[TCMS#236641 setup] Generate entitlement certificate '''
        RHUIManagerClient.generate_ent_cert(self.rs.Instances["RHUA"][0], "Cluster1", ["cp_1"], "cert-cp_1", "/root/", validity_days="", cert_pw=None)

        '''[TCMS#236641 setup] Create configuration rpm '''
        RHUIManagerClient.create_conf_rpm(self.rs.Instances["RHUA"][0], "Cluster1", self.rs.Instances["CDS"][0].private_hostname, "/root", "/root/cert-cp_1.crt", "/root/cert-cp_1.key", "cp_1", "3.0")

        '''[TCMS#236641 setup] Install configuration rpm to client '''
        Util.install_rpm_from_rhua(self.rs.Instances["RHUA"][0], self.rs.Instances["CLI"][0], "/root/cp_1-3.0/build/RPMS/noarch/cp_1-3.0-1.noarch.rpm")

    def _test(self):
        '''[TCMS#236641 test] Installing RH rpm from RH repo to the client '''
        Expect.ping_pong(self.rs.Instances["CLI"][0], "yum repolist | grep cp_1 && echo SUCCESS", "[^ ]SUCCESS", 60)

    def _cleanup(self):
        '''[TCMS#236641 cleanup] Removing configuration rpm from the client '''
        Util.remove_conf_rpm(self.rs.Instances["CLI"][0])

        '''[TCMS#236641 cleanup] Remove cds '''
        RHUIManagerCds.delete_cds(self.rs.Instances["RHUA"][0], "Cluster1", [self.rs.Instances["CDS"][0].private_hostname])

        '''[TCMS#236641 cleanup] Delete custom repo '''
        RHUIManagerRepo.delete_repo(self.rs.Instances["RHUA"][0], ["cp_1"])


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
