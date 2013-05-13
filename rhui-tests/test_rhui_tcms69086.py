#! /usr/bin/python -tt

import nose
import time

from rhuilib.util import *
from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_cds import *
from rhuilib.rhuimanager_client import *
from rhuilib.rhuimanager_repo import *
from rhuilib.rhuimanager_sync import *


class test_tcms_69086(RHUITestcase):
    def _setup(self):
        '''[TCMS#69086 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.Instances["RHUA"][0])
        
        '''[TCMS#69086 setup] Create custom repo '''
        RHUIManagerRepo.add_custom_repo(self.rs.Instances["RHUA"][0], "repo_tcms69086", redhat_gpg="n")
        
        '''[TCMS#69086 setup] Add cds '''
        RHUIManagerCds.add_cds(self.rs.Instances["RHUA"][0], "Cluster1", self.rs.Instances["CDS"][0].private_hostname)
        
        '''[TCMS#69086 setup] Associate custom repo with cluster '''
        RHUIManagerCds.associate_repo_cds(self.rs.Instances["RHUA"][0], "Cluster1", ["repo_tcms69086"])
        
        '''[TCMS#69086 setup] Generate entitlement certificate '''
        RHUIManagerClient.generate_ent_cert(self.rs.Instances["RHUA"][0], "Cluster1", ["repo_tcms69086"], "cert-repo_tcms69086", "/root/", validity_days="", cert_pw=None)
        
        '''[TCMS#69086 setup] Create configuration rpm '''
        RHUIManagerClient.create_conf_rpm(self.rs.Instances["RHUA"][0], "Cluster1", self.rs.Instances["CDS"][0].private_hostname, "/root", "/root/cert-repo_tcms69086.crt", "/root/cert-repo_tcms69086.key", "repo_tcms69086", "3.0")
        
        '''[TCMS#69086 setup] Remove rhui configuration rpm from client '''
        Util.remove_conf_rpm(self.rs.Instances["CLI"][0])
        
        '''[TCMS#69086 setup] Install configuration rpm to client'''
        Util.install_rpm_from_rhua(self.rs.Instances["RHUA"][0], self.rs.Instances["CLI"][0], "/root/repo_tcms69086-3.0/build/RPMS/noarch/repo_tcms69086-3.0-1.noarch.rpm")
        
        '''[TCMS#69086 setup] Create configuration rpm '''
        RHUIManagerClient.create_conf_rpm(self.rs.Instances["RHUA"][0], "Cluster1", self.rs.Instances["CDS"][0].private_hostname, "/root", "/root/cert-repo_tcms69086.crt", "/root/cert-repo_tcms69086.key", "repo_tcms69086", "3.1")
        
    def _test(self):
        '''[TCMS#69086 test] upload client configuration rpm '''
        Expect.ping_pong(self.rs.Instances["RHUA"][0], "rhui-manager packages upload --repo_id repo_tcms69086 --packages /root/repo_tcms69086-3.1/build/RPMS/noarch/repo_tcms69086-3.1-1.noarch.rpm && echo SUCCESS", "[^ ]SUCCESS", 10)

        '''[TCMS#69086 test] Sync cds '''
        RHUIManagerSync.sync_cds(self.rs.Instances["RHUA"][0], [self.rs.Instances["CDS"][0].private_hostname])
        
        time.sleep(10)
        
        '''[TCMS#69086 test] trying to install updated rpm on the client'''
        Expect.ping_pong(self.rs.Instances["CLI"][0], "yum install -y repo_tcms69086 && echo SUCCESS", "[^ ]SUCCESS", 60)
        
        '''[TCMS#69086 test] check client configuration rpm version'''
        Expect.ping_pong(self.rs.Instances["CLI"][0], "[ `rpm -q --queryformat \"%{VERSION}\" repo_tcms69086` = '3.1' ] && echo SUCCESS", "[^ ]SUCCESS")

    def _cleanup(self):
        '''[TCMS#69086 cleanup] Remove rhui configuration rpm from client '''
        Util.remove_conf_rpm(self.rs.Instances["CLI"][0])

        '''[TCMS#69086 cleanup] Remove cds '''
        RHUIManagerCds.delete_cds(self.rs.Instances["RHUA"][0], "Cluster1", [self.rs.Instances["CDS"][0].private_hostname])

        '''[TCMS#69086 cleanup] Delete custom repos '''
        RHUIManagerRepo.delete_repo(self.rs.Instances["RHUA"][0], ["repo_tcms69086"])


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
