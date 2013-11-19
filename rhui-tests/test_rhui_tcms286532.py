#! /usr/bin/python -tt

import nose
import time

from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_cds import *
from rhuilib.rhuimanager_repo import *
from rhuilib.cds import RhuiCds


class test_tcms_286532(RHUITestcase):
    def _setup(self):

        '''[TCMS#286532 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.Instances["RHUA"][0])

        '''[TCMS#286532 setup] Add cds '''
        RHUIManagerCds.add_cds(self.rs.Instances["RHUA"][0], "Cluster1", self.rs.Instances["CDS"][0].private_hostname)

        '''[TCMS#286532 setup] Create custom repo'''
        RHUIManagerRepo.add_custom_repo(self.rs.Instances["RHUA"][0], "repo286532", path="/myrepos/repo286532/")

        '''[TCMS#286532 setup] Upload content to custom repo '''
        RHUIManagerRepo.upload_content(self.rs.Instances["RHUA"][0], ["repo286532"], "/etc/rhui/confrpm")

        '''[TCMS#248532 setup] Associate repo with cluster '''
        Expect.ping_pong(self.rs.Instances["RHUA"][0], "pulp-admin -u admin -p admin cds associate_repo --repoid=repo286532 --hostname=" + self.rs.Instances["CDS"][0].private_hostname + " && echo SUCCESS", "[^ ]SUCCESS", 10)

        '''[TCMS#248532 setup] Sync cds '''
        Expect.ping_pong(self.rs.Instances["RHUA"][0], "pulp-admin -u admin -p admin cds sync --hostname=" + self.rs.Instances["CDS"][0].private_hostname + " && echo SUCCESS", "[^ ]SUCCESS", 20)

        '''[TCMS#248532 setup] Unassociate repo '''
        Expect.ping_pong(self.rs.Instances["RHUA"][0], "pulp-admin -u admin -p admin cds unassociate_repo --repoid=repo286532 --hostname=" + self.rs.Instances["CDS"][0].private_hostname + " && echo SUCCESS", "[^ ]SUCCESS", 10)

        '''[TCMS#248532 setup] Sync cds '''
        time.sleep(10)
        Expect.ping_pong(self.rs.Instances["RHUA"][0], "pulp-admin -u admin -p admin cds sync --hostname=" + self.rs.Instances["CDS"][0].private_hostname + " && echo SUCCESS", "[^ ]SUCCESS", 10)

    def _test(self):

        '''[TCMS#248532 test] Check repo on CDS '''
        Expect.ping_pong(self.rs.Instances["CDS"][0], "[ -d /var/lib/pulp-cds/repos/myrepos/ ] || echo SUCCESS", "[^ ]SUCCESS")

    def _cleanup(self):

        '''[TCMS#286532 cleanup] Delete custom repo '''
        RHUIManagerRepo.delete_repo(self.rs.Instances["RHUA"][0], ["repo286532"])

        '''[TCMS#286532 cleanup] Delete repo from CDS /var/lib/pulp-cds/ '''
        Expect.ping_pong(self.rs.Instances["CDS"][0], " rm -r -f /var/lib/pulp-cds/repos/myrepos/ && echo SUCCESS", "[^ ]SUCCESS")

        '''[TCMS#286532 test] Stop httpd on CDS'''
        Expect.ping_pong(self.rs.Instances["CDS"][0], "service httpd stop && echo SUCCESS", "[^ ]SUCCESS", 30)

        '''[TCMS#286532 test] Delete orphaned packages '''
        Expect.ping_pong(self.rs.Instances["CDS"][0], "echo Y | pulp-purge-packages 2>&1 && echo SUCCESS", "[^ ]SUCCESS", 30)

        '''[TCMS#286532 cleanup] Start httpd on CDS'''
        Expect.ping_pong(self.rs.Instances["CDS"][0], "service httpd start ||: && echo SUCCESS", "[^ ]SUCCESS", 30)

        '''[TCMS#286532 cleanup] Remove cds '''
        RHUIManagerCds.delete_cds(self.rs.Instances["RHUA"][0], "Cluster1", [self.rs.Instances["CDS"][0].private_hostname])


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
