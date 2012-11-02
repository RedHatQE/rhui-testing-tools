#! /usr/bin/python -tt

import logging
import argparse
import nose

from rhuilib.util import *
from rhuilib.rhuisetup import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_cds import *
from rhuilib.rhuimanager_client import *
from rhuilib.rhuimanager_repo import *
from rhuilib.rhuimanager_sync import *
from rhuilib.rhuimanager_identity import *
from rhuilib.rhuimanager_users import *
from rhuilib.rhuimanager_entitlements import *


class test_tcms_178463(object):
    cluster="cluster"
    repo="repo"

    def __init__(self):
        argparser = argparse.ArgumentParser(description='RHUI TCMS testcase 178463: test un-associating a custom repository from a CDS cluster')
        args = argparser.parse_args()
        self.rs = RHUIsetup()
        self.rs.setup_from_rolesfile()

    def test_01_initial_run(self):
        '''[setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.RHUA)

    def test_02_add_cds(self):
        '''[setup] Add cds creating a cluster'''
        RHUIManagerCds.add_cds(self.rs.RHUA, self.cluster, self.rs.CDS[0].hostname)

    def test_03_add_custom_repo(self):
        '''[setup] Create custom repo'''
        RHUIManagerRepo.add_custom_repo(self.rs.RHUA, self.repo)

    def test_04_associate_custom_repo(self):
        '''[setup] Associate custom repo with a cluster'''
        RHUIManagerCds.associate_repo_cds(self.rs.RHUA, self.cluster, [self.repo])

    def test_05_un_associate_custom_repo(self):
        '''[test] Un-associate a custom repo from a cluster'''
        RHUIManagerCds.unassociate_repo_cds(self.rs.RHUA, self.cluster, [self.repo])

    def test_06_remove_custom_repo(self):
        '''[teardown] Remove the custom repo'''
        RHUIManagerRepo.delete_repo(self.rs.RHUA, [self.repo])

    def test_07_remove_cds(self):
        '''[teardown] Remove the cds'''
        RHUIManagerCds.delete_cds(self.rs.RHUA, self.cluster,
                [self.rs.CDS[0].hostname])

if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])

