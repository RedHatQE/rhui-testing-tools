#! /usr/bin/python -tt

import nose

from rhuilib.util import *
from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_cds import *
from rhuilib.rhuimanager_repo import *


class test_tcms_178463(RHUITestcase):
    cluster = "cluster"
    repo = "repo"

    def __init__(self):
        RHUITestcase.__init__(self)
        '''[TCMS#178463 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.RHUA)

        '''[TCMS#178463 setup] Add cds creating a cluster'''
        RHUIManagerCds.add_cds(self.rs.RHUA, self.cluster, self.rs.CDS[0].hostname)

        '''[TCMS#178463 setup] Create custom repo'''
        RHUIManagerRepo.add_custom_repo(self.rs.RHUA, self.repo)

        '''[TCMS#178463 setup] Associate custom repo with a cluster'''
        RHUIManagerCds.associate_repo_cds(self.rs.RHUA, self.cluster, [self.repo])

    def test_tcms_178463(self):
        '''[TCMS#178463 test] Un-associate a custom repo from a cluster'''
        RHUIManagerCds.unassociate_repo_cds(self.rs.RHUA, self.cluster, [self.repo])

    def __del__(self):
        '''[TCMS#178463 teardown] Remove the custom repo'''
        RHUIManagerRepo.delete_repo(self.rs.RHUA, [self.repo])

        '''[TCMS#178463 teardown] Remove the cds'''
        RHUIManagerCds.delete_cds(self.rs.RHUA, self.cluster,
                [self.rs.CDS[0].hostname])

        RHUITestcase.__del__()


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
