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
    def __init__(self):
        RHUITestcase.__init__(self)
        '''[TCMS#178464 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.RHUA)

        '''[TCMS#178464 setup] Add cds '''
        RHUIManagerCds.add_cds(self.rs.RHUA, "Cluster1", self.rs.CDS[0].hostname)

        '''[TCMS#178464 setup] Create custom repo '''
        RHUIManagerRepo.add_custom_repo(self.rs.RHUA, "repo1")

        '''[TCMS#178464 setup] Associate repos with clusters '''
        RHUIManagerCds.associate_repo_cds(self.rs.RHUA, "Cluster1", ["repo1"])

    def test_tcms_178464(self):
        '''[TCMS#178464 test] Check cds info screen '''
        cds = RhuiCds(
                hostname=self.rs.CDS[0].hostname,
                cluster="Cluster1",
                repos=["repo1"]
                )
        nose.tools.assert_equal(RHUIManagerCds.info(self.rs.RHUA, ["Cluster1"]), [cds])

        '''[TCMS#178464 test] Check pulp-admin cds list '''
        nose.tools.assert_equals(PulpAdmin.cds_list(self.rs.RHUA),
                RHUIManagerCds.info(self.rs.RHUA, ["Cluster1"]))

        '''[TCMS#178464 test] Check certs created for custom repo '''
        Expect.ping_pong(self.rs.RHUA, "test -f /etc/pki/pulp/content/repo1/consumer-repo1.cert && echo SUCCESS", "[^ ]SUCCESS")
        Expect.ping_pong(self.rs.RHUA, "test -f /etc/pki/pulp/content/repo1/consumer-repo1.ca && echo SUCCESS", "[^ ]SUCCESS")

    def __del__(self):
        '''[TCMS#178464 cleanup] Remove cds '''
        RHUIManagerCds.delete_cds(self.rs.RHUA, "Cluster1", [self.rs.CDS[0].hostname])

        '''[TCMS#178464 cleanup] Delete custom repos '''
        RHUIManagerRepo.delete_repo(self.rs.RHUA, ["repo1"])

        RHUITestcase.__del__()


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
