#! /usr/bin/python -tt
import nose
import time

from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_cds import *
from rhuilib.rhuimanager_repo import *
from rhuilib.rhuimanager_sync import *


class test_rhui_tcms267309(RHUITestcase):
    def _setup(self):

        '''[TCMS#267309 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.Instances["RHUA"][0])

        '''[TCMS#267309 setup] Add cds '''
        RHUIManagerCds.add_cds(self.rs.Instances["RHUA"][0], "Cluster1", self.rs.Instances["CDS"][0].private_hostname)

        '''[TCMS#267309 setup] Create custom repo'''
        RHUIManagerRepo.add_custom_repo(self.rs.Instances["RHUA"][0], "repo267309")

        '''[TCMS#267309 setup] Associate custom repo with cluster'''
        RHUIManagerCds.associate_repo_cds(self.rs.Instances["RHUA"][0], "Cluster1", ["repo267309"])

        '''[TCMS#69086 test] upload unsigned rpm to custom repo'''
        Expect.ping_pong(self.rs.Instances["RHUA"][0], "rhui-manager packages upload --repo_id repo267309 --packages /etc/rhui/confrpm && echo SUCCESS", "[^ ]SUCCESS", 10)

        '''[TCMS#267309 setup] Sync CDS '''
        self._sync_cds([self.rs.Instances["CDS"][0].private_hostname])

    def _test(self):
        '''[TCMS#267309 test] Check repo content on cds '''
        time.sleep(10)
        Expect.ping_pong(self.rs.Instances["CDS"][0], "test -f /var/lib/pulp-cds/repos/repo267309/cds1.example.com-1.0-2.el6.noarch.rpm && echo SUCCESS", "[^ ]SUCCESS")
        Expect.ping_pong(self.rs.Instances["CDS"][0], "find /var/lib/pulp-cds/packages/ -name 'cds1.example.com-1.0-2.el6.noarch.rpm' | grep cds1.example.com-1.0-2.el6.noarch.rpm && echo SUCCESS", "[^ ]SUCCESS", 30)

    def _cleanup(self):
        '''[TCMS#267309 cleanup] Delete custom repo '''
        RHUIManagerRepo.delete_repo(self.rs.Instances["RHUA"][0], ["repo267309"])

        '''[TCMS#267309 setup] Sync CDS '''
        self.sync_cds([self.rs.Instances["CDS"][0].private_hostname])

        '''[TCMS#267309 test] Stop httpd on CDS'''
        Expect.ping_pong(self.rs.Instances["CDS"][0], "service httpd stop && echo SUCCESS", "[^ ]SUCCESS", 30)

        '''[TCMS#267309 test] Delete orphaned packages '''
        Expect.ping_pong(self.rs.Instances["CDS"][0], "echo Y | pulp-purge-packages 2>&1 && echo SUCCESS", "[^ ]SUCCESS", 30)

        '''[TCMS#248535 cleanup] Start httpd on CDS'''
        Expect.ping_pong(self.rs.Instances["CDS"][0], "service httpd start ||: && echo SUCCESS", "[^ ]SUCCESS", 30)

        '''[TCMS#267309 cleanup] Remove cds '''
        RHUIManagerCds.delete_cds(self.rs.Instances["RHUA"][0], "Cluster1", [self.rs.Instances["CDS"][0].private_hostname])

if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
