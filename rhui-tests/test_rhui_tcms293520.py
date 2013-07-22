#! /usr/bin/python -tt

import nose

from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_repo import *
from rhuilib.rhuimanager_sync import *
from rhuilib.rhuimanager_entitlements import *


class test_tcms_293520(RHUITestcase, RHUI_has_RH_cert):
    def _setup(self):
        '''[TCMS#293520 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.Instances["RHUA"][0])

        '''[TCMS#293520 setup] Upload RH content certificate '''
        RHUIManagerEntitlements.upload_content_cert(self.rs.Instances["RHUA"][0], self.cert)

        '''[TCMS#293520 setup] Add rh repo '''
        RHUIManagerRepo.add_rh_repo_by_repo(self.rs.Instances["RHUA"][0], ["Red Hat Enterprise Linux 6 Server from RHUI \(RPMs\) \(6Server-x86_64\)", "Red Hat Enterprise Linux 6 Server - Optional from RHUI \(RPMs\) \(6Server-x86_64\)"])

        '''[TCMS#293520 setup] Sync RH repo '''
        self._sync_repo(["Red Hat Enterprise Linux 6 Server from RHUI \(RPMs\) \(6Server-x86_64\)", "Red Hat Enterprise Linux 6 Server - Optional from RHUI \(RPMs\) \(6Server-x86_64\)"])

    def _test(self):
        '''[TCMS#293520 test] Check list of effected packaged in errata'''
        Expect.ping_pong(self.rs.Instances["RHUA"][0], "pulp-admin -u admin -p admin errata info --id=RHBA-2013:0329 | sed -n '/Effected/,/Reboot/p' | sed -e 's,Packages Effected,,' -e '$d' -e 's/\s//g' > /tmp/actual_list.txt && echo SUCCESS", "[^ ]SUCCESS", 10)
        self.rs.Instances["RHUA"][0].sftp.get('/tmp/actual_list.txt', '/tmp/actual_list.txt')
        output = open('/tmp/actual_list.txt', 'r')
        result = output.read()
        result = result.replace(",\n", "\n")
        packages = result.split("\n")
        packages.pop()
        expected_list = ['libssh2-devel-1.4.2-1.el6.i686.rpm', 'libssh2-docs-1.4.2-1.el6.x86_64.rpm', 'libssh2-devel-1.4.2-1.el6.x86_64.rpm', 'libssh2-1.4.2-1.el6.i686.rpm', 'libssh2-1.4.2-1.el6.x86_64.rpm']
        nose.tools.assert_equal(len(packages), len(expected_list))
        nose.tools.assert_equal(set(packages), set(expected_list))

    def _cleanup(self):
        '''[TCMS#293520 cleanup] Delete RH repo '''
        RHUIManagerRepo.delete_repo(self.rs.Instances["RHUA"][0], ["Red Hat Enterprise Linux 6 Server from RHUI \(RPMs\) \(6Server-x86_64\)", "Red Hat Enterprise Linux 6 Server - Optional from RHUI \(RPMs\) \(6Server-x86_64\)"])

        '''[TCMS#293520 cleanup] Remove RH certificate from RHUI '''
        RHUIManager.remove_rh_certs(self.rs.Instances["RHUA"][0])


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
