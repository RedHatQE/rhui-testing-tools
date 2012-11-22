#! /usr/bin/python -tt

import nose
import logging

from rhuilib.util import *
from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_cds import *
from rhuilib.rhuimanager_repo import *
from rhuilib.pulp_admin import PulpAdmin
from rhuilib.cds import RhuiCds


class test_tcms_178442(RHUITestcase, RHUI_has_three_CDSes):
    def _setup(self):
        '''[TCMS#178442 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.RHUA[0])

        '''[TCMS#178442 setup] Add cdses: cds0, cds2 -> cluster1; cds1 -> cluster2'''
        RHUIManagerCds.add_cds(self.rs.RHUA[0], "Cluster1", self.rs.CDS[0].private_hostname)
        RHUIManagerCds.add_cds(self.rs.RHUA[0], "Cluster2", self.rs.CDS[1].private_hostname)
        RHUIManagerCds.add_cds(self.rs.RHUA[0], "Cluster1", self.rs.CDS[2].private_hostname)

        '''[TCMS#178442 setup] Create custom repo1 '''
        RHUIManagerRepo.add_custom_repo(self.rs.RHUA[0], "repo1")

        '''[TCMS#178442 setup] Associate repo1 with both the clusters'''
        RHUIManagerCds.associate_repo_cds(self.rs.RHUA[0], "Cluster1", ["repo1"])
        RHUIManagerCds.associate_repo_cds(self.rs.RHUA[0], "Cluster2", ["repo1"])

    def _test(self):
        '''[TCMS#178442 test] Move cds2 to cluster2'''
        RHUIManagerCds.move_cds(self.rs.RHUA[0], [self.rs.CDS[2].private_hostname], "Cluster2")

        '''[TCMS#178442 test] Check that cds2 moved to cluster2'''
        cds0 = RhuiCds(
                hostname=self.rs.CDS[0].private_hostname,
                cluster='Cluster1',
                repos=['repo1'])
        cds1 = RhuiCds(
                hostname=self.rs.CDS[1].private_hostname,
                cluster='Cluster2',
                repos=['repo1']
                )
        cds2 = RhuiCds(
                hostname=self.rs.CDS[2].private_hostname,
                cluster='Cluster2',
                repos=['repo1']
                )
        nose.tools.assert_equal(sorted(RHUIManagerCds.info(self.rs.RHUA[0],
            ["Cluster1", "Cluster2"])), sorted([cds0, cds1, cds2]))

        '''[TCMS#178442 test] Check pulp-admin and rhui cluster info are the same'''
        nose.tools.assert_equals(sorted(PulpAdmin.cds_list(self.rs.RHUA[0])),
                sorted(RHUIManagerCds.info(self.rs.RHUA[0], ['Cluster1',
                    'Cluster2'])))

    def _cleanup(self):
        '''[TCMS#178442 cleanup] Delete custom repos '''
        RHUIManagerRepo.delete_repo(self.rs.RHUA[0], ["repo1"])

        '''[TCMS#178442 cleanup] Remove cdses '''
        RHUIManagerCds.delete_cds(self.rs.RHUA[0], "Cluster1", [self.rs.CDS[0].private_hostname])
        RHUIManagerCds.delete_cds(self.rs.RHUA[0], "Cluster2", [self.rs.CDS[1].private_hostname])
        RHUIManagerCds.delete_cds(self.rs.RHUA[0], "Cluster2", [self.rs.CDS[2].private_hostname])


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
