#! /usr/bin/python -tt

import nose

from rhuilib.util import *
from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_cds import *
from rhuilib.rhuimanager_repo import *
from rhuilib.pulp_admin import PulpAdmin
from rhuilib.cds import RhuiCds


class test_tcms_178464(RHUITestcase):
    def _setup(self):
        '''[TCMS#178464 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.Instances["RHUA"][0])

        '''[TCMS#178464 setup] Add cds '''
        RHUIManagerCds.add_cds(self.rs.Instances["RHUA"][0], "Cluster1", self.rs.Instances["CDS"][0].private_hostname)

        '''[TCMS#178464 setup] Create custom repo '''
        RHUIManagerRepo.add_custom_repo(self.rs.Instances["RHUA"][0], "repo1")

        '''[TCMS#178464 setup] Associate repos with clusters '''
        RHUIManagerCds.associate_repo_cds(self.rs.Instances["RHUA"][0], "Cluster1", ["repo1"])

    def _test(self):
        '''[TCMS#178464 test] Check cds info screen '''
        cds = RhuiCds(
                hostname=self.rs.Instances["CDS"][0].private_hostname,
                cluster="Cluster1",
                repos=["repo1"]
                )
        nose.tools.assert_equal(RHUIManagerCds.info(self.rs.Instances["RHUA"][0], ["Cluster1"]), [cds])

        '''[TCMS#178464 test] Check pulp-admin cds list '''
        nose.tools.assert_equals(PulpAdmin.cds_list(self.rs.Instances["RHUA"][0]),
                RHUIManagerCds.info(self.rs.Instances["RHUA"][0], ["Cluster1"]))

        '''[TCMS#178464 test] Check certs created for custom repo '''
        Expect.ping_pong(self.rs.Instances["RHUA"][0], "test -f /etc/pki/pulp/content/repo1/consumer-repo1.cert && echo SUCCESS", "[^ ]SUCCESS")
        Expect.ping_pong(self.rs.Instances["RHUA"][0], "test -f /etc/pki/pulp/content/repo1/consumer-repo1.ca && echo SUCCESS", "[^ ]SUCCESS")

    def _cleanup(self):
        '''[TCMS#178464 cleanup] Remove cds '''
        RHUIManagerCds.delete_cds(self.rs.Instances["RHUA"][0], "Cluster1", [self.rs.Instances["CDS"][0].private_hostname])

        '''[TCMS#178464 cleanup] Delete custom repos '''
        RHUIManagerRepo.delete_repo(self.rs.Instances["RHUA"][0], ["repo1"])


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
