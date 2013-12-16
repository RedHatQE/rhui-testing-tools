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
from rhuilib.rhuimanager_entitlements import *
from rhuilib.cds import RhuiCds


class test_tcms_251851(RHUITestcase, RHUI_has_RH_cert):
    ''' Bug 916378 '''
    def _setup(self):
        '''[TCMS#251851 test] Change num_old_pkgs_keep setting'''
        Expect.ping_pong(self.rs.Instances["RHUA"][0], "sed -i \"s,num_old_pkgs_keep:.*$,num_old_pkgs_keep: 100,\" /etc/pulp/pulp.conf && echo SUCCESS", "[^ ]SUCCESS")
        Expect.ping_pong(self.rs.Instances["RHUA"][0], "service pulp-server restart && echo SUCCESS", "[^ ]SUCCESS", 30)

        '''[TCMS#251851 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.Instances["RHUA"][0])

        '''[TCMS#251851 setup] Upload RH content certificate '''
        RHUIManagerEntitlements.upload_content_cert(self.rs.Instances["RHUA"][0], self.cert)

        '''[TCMS#251851 setup] Add rh repo '''
        RHUIManagerRepo.add_rh_repo_by_repo(self.rs.Instances["RHUA"][0], ["Red Hat Update Infrastructure 2 \(Source RPMs\) \(6Server-x86_64\)"])

        '''[TCMS#251851 setup] Sync RH repo '''
        self._sync_repo(["Red Hat Update Infrastructure 2 \(Source RPMs\) \(6Server-x86_64\)"])

    def _test(self):
        '''[TCMS#251851 test] Stop httpd on RHUA'''
        Expect.ping_pong(self.rs.Instances["RHUA"][0], "service httpd stop && echo SUCCESS", "[^ ]SUCCESS", 30)

        '''[TCMS#251851 test] Stop httpd on RHUA'''
        Expect.ping_pong(self.rs.Instances["RHUA"][0], "rm -f /var/lib/pulp/repos/content/dist/rhel/rhui/server/6/6Server/x86_64/rhui/2/source/SRPMS/rh-rhui-tools-2.1.17-1.el6_3.src.rpm && echo SUCCESS", "[^ ]SUCCESS")

        '''[TCMS#251851 test] Check for pulp-purge-packages output '''
        Expect.ping_pong(self.rs.Instances["RHUA"][0], "echo Y | pulp-purge-packages 2>&1 | grep \"rh-rhui-tools.*deleted\" && echo SUCCESS", "[^ ]SUCCESS", 900)

    def _cleanup(self):
        '''[TCMS#251851 cleanup] Change num_old_pkgs_keep setting, restart pulp-server'''
        Expect.ping_pong(self.rs.Instances["RHUA"][0], "sed -i \"s,num_old_pkgs_keep:.*$,num_old_pkgs_keep: 2,\" /etc/pulp/pulp.conf && echo SUCCESS", "[^ ]SUCCESS")
        Expect.ping_pong(self.rs.Instances["RHUA"][0], "service pulp-server restart && echo SUCCESS", "[^ ]SUCCESS", 30)

        '''[TCMS#251851 cleanup] Delete RH repo '''
        RHUIManagerRepo.delete_repo(self.rs.Instances["RHUA"][0], ["Red Hat Update Infrastructure 2 \(Source RPMs\) \(6Server-x86_64\)"])

        '''[TCMS#251851 cleanup] Remove RH certificate from RHUI '''
        RHUIManager.remove_rh_certs(self.rs.Instances["RHUA"][0])


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
