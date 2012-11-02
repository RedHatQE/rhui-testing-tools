#! /usr/bin/python -tt

import argparse, nose, re

from rhuilib.expect import *
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


class Cds(object):
    repos_path = '/var/lib/pulp-cds/repos'
    def __init__(self, connection, clientname=None, displayname=None):
        self.connection = connection
        self.hostname = connection.hostname
        if clientname is None:
            self.clientname = self.hostname
        if displayname is None:
            self.displayname = self.hostname
    def get_reponames(self):
        '''return list of names made of contents of /var/lib/pulp-cds/repos'''
        (stdin, stdout, stderr) = self.connection.exec_command(
            "ls %s" % self.repos_path)
        return [ x.strip() for x in stdout.read().split('\n')]

class test_178468(object):
    repo = "repo-1"
    cluster = "cluster-1"
    def __init__(self):
        argparser = argparse.ArgumentParser(description=\
                '178468: Synchronize Unassociated Repositories')
        args = argparser.parse_args()
        self.rs = RHUIsetup()
        self.rs.setup_from_rolesfile()
        self.cds = Cds(self.rs.CDS[0])

    def test_01_initial_run(self):
        '''[setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.RHUA)

    def test_02_add_cds(self):
        '''[setup] Add cds creating a cluster'''
        RHUIManagerCds.add_cds(self.rs.RHUA, self.cluster, self.cds.hostname)

    def test_03_add_custom_repo(self):
        '''[setup] Create custom repo'''
        RHUIManagerRepo.add_custom_repo(self.rs.RHUA, self.repo)

    def test_04_associate_custom_repo(self):
        '''[setup] Associate custom repo with a cluster'''
        RHUIManagerCds.associate_repo_cds(self.rs.RHUA, self.cluster, [self.repo])
    
    def test_05_upload_content(self):
        '''[setup] Upload content to custom repo '''
        RHUIManagerRepo.upload_content(self.rs.RHUA, [self.repo], "/etc/rhui/confrpm")

    def test_06_sync_cds(self):
        '''[setup] Sync cdses having uploaded content'''
        RHUIManagerSync.sync_cds(self.rs.RHUA, [self.cds.hostname])

    def test_07_assert_repo_on_cds(self):
        '''[test] assert repo contents is present on the CDS'''
        nose.tools.ok_(self.repo in self.cds.get_reponames())
        
    def test_08_un_associate_custom_repo(self):
        '''[test] Un-associate a custom repo from a cluster'''
        RHUIManagerCds.unassociate_repo_cds(self.rs.RHUA, self.cluster, [self.repo])

    def test_09_sync_cds(self):
        '''[test] Sync cdses having unassociated repo'''
        RHUIManagerSync.sync_cds(self.rs.RHUA, [self.cds.hostname])

    def test_10_assetr_repo_on_cds_no_more(self):
        '''[test] assert repo contents is present on the CDS no more'''
        nose.tools.ok_(self.repo not in self.cds.get_reponames())

    def test_11_remove_custom_repo(self):
        '''[teardown] Remove the custom repo'''
        RHUIManagerRepo.delete_repo(self.rs.RHUA, [self.repo])

    def test_12_remove_cds(self):
        """[teardown] check removing a cds from single node cluster"""
        RHUIManagerCds.delete_cds(self.rs.RHUA, "cluster-1", [self.rs.CDS[0].hostname])

if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
