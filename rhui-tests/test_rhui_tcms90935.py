#! /usr/bin/python -tt

import nose
import re

from rhuilib.util import *
from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_cds import *
from rhuilib.rhuimanager_repo import *
from rhuilib.rhuimanager_client import *
from rhuilib.pulp_admin import *

class test_rhui_tcms90935(RHUITestcase):
    def _setup(self):
        '''[TCMS#90935 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.Instances["RHUA"][0])

        '''[TCMS#90935 setup] Add cds'''
        RHUIManagerCds.add_cds(self.rs.Instances["RHUA"][0], "Cluster1", self.rs.Instances["CDS"][0].private_hostname)
        
        '''[TCMS#90935 setup] Create custom repo'''
        RHUIManagerRepo.add_custom_repo(self.rs.Instances["RHUA"][0], "repo90935")
        
        '''[TCMS#90935 setup] Associate repo with cluster'''
        RHUIManagerCds.associate_repo_cds(self.rs.Instances["RHUA"][0], "Cluster1", ["repo90935"])
        
        '''[TCMS#90935 setup] Generate entitlement certificate'''
        RHUIManagerClient.generate_ent_cert(self.rs.Instances["RHUA"][0], "Cluster1", ["repo90935"], "cert-repo90935", "/root/", validity_days="", cert_pw=None)
        
        '''[TCMS#90935 setup] Create configuration rpm '''
        RHUIManagerClient.create_conf_rpm(self.rs.Instances["RHUA"][0], "Cluster1", self.rs.Instances["CDS"][0].private_hostname, "/root", "/root/cert-repo90935.crt", "/root/cert-repo90935.key", "repo90935", "3.0")
        
    def _test(self):
        '''[TCMS#90935 test] Check if the configuration rpm exists'''
        Expect.ping_pong(self.rs.Instances["RHUA"][0], "test -e /root/repo90935-3.0 && echo SUCCESS", "[^ ]SUCCESS")

    def _cleanup(self):
        '''[TCMS#90935 cleanup] Remove cds'''
        RHUIManagerCds.delete_cds(self.rs.Instances["RHUA"][0], "Cluster1", [self.rs.Instances["CDS"][0].private_hostname])
        
        '''[TCMS#90935 cleanup] Remove custom repo'''
        RHUIManagerRepo.delete_repo(self.rs.Instances["RHUA"][0], ["repo90935"])
        
if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])

