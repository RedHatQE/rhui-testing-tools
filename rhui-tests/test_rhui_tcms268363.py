#! /usr/bin/python -tt

import nose

from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_cds import *
from rhuilib.rhuimanager_client import *
from rhuilib.rhuimanager_repo import *
from rhuilib.rhuimanager_sync import *
from rhuilib.rhuimanager_entitlements import *


class test_tcms268363(RHUITestcase):
    def _setup(self):
        '''[TCMS#268363 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.Instances["RHUA"][0])

        '''TCMS#268363 setup] Add cds '''
        RHUIManagerCds.add_cds(self.rs.Instances["RHUA"][0], "Cluster1", self.rs.Instances["CDS"][0].private_hostname)

        '''[TCMS#268363 setup] Create custom protected repo '''
        RHUIManagerRepo.add_custom_repo(self.rs.Instances["RHUA"][0], "repo268363")

        '''[TCMS#268363 setup] Associate repo with cluster '''
        RHUIManagerCds.associate_repo_cds(self.rs.Instances["RHUA"][0], "Cluster1", ["repo268363"])

        '''[TCMS#268363 setup] Generate entitlement certificate '''
        RHUIManagerClient.generate_ent_cert(self.rs.Instances["RHUA"][0], "Cluster1", ["repo268363"], "cert-repo268363", "/root/", validity_days="", cert_pw=None)

        '''[TCMS#268363 setup] Sync cluster '''
        RHUIManagerSync.sync_cluster(self.rs.Instances["RHUA"][0], ["Cluster1"])

    def _test(self):
        '''[TCMS#268363 test] check if the keys exist on CDS'''
        Expect.ping_pong(self.rs.Instances["CDS"][0], "test -f /etc/pki/pulp/content/repo268363/consumer-repo268363.cert && echo SUCCESS", "[^ ]SUCCESS")
        Expect.ping_pong(self.rs.Instances["CDS"][0], "test -f /etc/pki/pulp/content/repo268363/consumer-repo268363.ca && echo SUCCESS", "[^ ]SUCCESS")

        '''[TCMS#268363 test] Delete custom repo '''
        RHUIManagerRepo.delete_repo(self.rs.Instances["RHUA"][0], ["repo268363"])

        '''[TCMS#268363 test] Sync cluster '''
        RHUIManagerSync.sync_cluster(self.rs.Instances["RHUA"][0], ["Cluster1"])

        '''[TCMS#268363 test] check if keys are not present on CDS'''
        Expect.ping_pong(self.rs.Instances["CDS"][0], "test -f /etc/pki/pulp/content/repo268363/consumer-repo268363.ca || echo SUCCESS", "[^ ]SUCCESS")
        Expect.ping_pong(self.rs.Instances["CDS"][0], "test -f /etc/pki/pulp/content/repo268363/consumer-repo268363.cert || echo SUCCESS", "[^ ]SUCCESS")

    def _cleanup(self):
        '''[TCMS#268363 cleanup] Remove cds '''
        RHUIManagerCds.delete_cds(self.rs.Instances["RHUA"][0], "Cluster1", [self.rs.Instances["CDS"][0].private_hostname])



if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
