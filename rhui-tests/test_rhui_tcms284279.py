#! /usr/bin/python -tt

import nose

from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_repo import *
from rhuilib.rhuimanager_entitlements import *


class test_tcms284279(RHUITestcase, RHUI_has_RH_cert):
    ''' for more ditails see bz 957128
    3 scenarios has to be tested here:
    a) upload fake rpms from a directory
    b) upload fake rpm explicitly
    c) upload signed rpm from directory'''

    def _setup(self):
        """[TCMS#284279 setup] Do initial rhui-manager run"""
        RHUIManager.initial_run(self.rs.Instances["RHUA"][0])

        '''[TCMS#284279 setup] Upload RH content certificate '''
        RHUIManagerEntitlements.upload_content_cert(self.rs.Instances["RHUA"][0], self.cert)

        '''[TCMS#284279 setup] Create custom repo '''
        RHUIManagerRepo.add_custom_repo(self.rs.Instances["RHUA"][0], "repo284279")
        RHUIManagerRepo.add_custom_repo(self.rs.Instances["RHUA"][0], "repo_xxx")
        RHUIManagerRepo.add_custom_repo(self.rs.Instances["RHUA"][0], "repo_yyy")

        '''[TCMS#284279 setup] Add rh repo '''
        RHUIManagerRepo.add_rh_repo_by_repo(self.rs.Instances["RHUA"][0], ["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])

        '''[TCMS#284279 setup] Sync RH repo '''
        self._sync_repo(["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])

        """[TCMS#284279 setup] Create fake rpm"""
        for i in xrange(10):
            Expect.enter(self.rs.Instances["RHUA"][0], "touch /var/lib/pulp/repos/content/dist/rhel/rhui/server/6/6Server/x86_64/rhui/2/os/Packages/test%d.rpm && echo SUCCESS" % i)

        '''[TCMS#284279 setup] Upload content to custom repo284279 '''
        Expect.enter(self.rs.Instances["RHUA"][0], "q")
        RHUIManager.screen(self.rs.Instances["RHUA"][0], "repo")
        Expect.enter(self.rs.Instances["RHUA"][0], "u")
        RHUIManager.select(self.rs.Instances["RHUA"][0], ["repo284279"])
        Expect.expect(self.rs.Instances["RHUA"][0], "will be uploaded:")
        Expect.enter(self.rs.Instances["RHUA"][0], "/var/lib/pulp/repos/content/dist/rhel/rhui/server/6/6Server/x86_64/rhui/2/os/Packages/")
        RHUIManager.proceed_without_check(self.rs.Instances["RHUA"][0])
        RHUIManager.quit(self.rs.Instances["RHUA"][0], "", 200)

        """[TCMS#284279 setup] Create rpm files"""
        Expect.ping_pong(self.rs.Instances["RHUA"][0], "mkdir /root/rpms284279 && echo SUCCESS", "[^ ]SUCCESS")
        self.rs.Instances["RHUA"][0].sftp.put("/usr/share/rhui-testing-tools/testing-data/custom-signed-rpm-1-0.1.fc17.noarch.rpm", "/root/rpms284279/custom-signed-rpm-1-0.1.fc17.noarch.rpm")
        self.rs.Instances["RHUA"][0].sftp.put("/usr/share/rhui-testing-tools/testing-data/custom-unsigned-rpm-1-0.1.fc17.noarch.rpm", "/root/rpms284279/custom-unsigned-rpm-1-0.1.fc17.noarch.rpm")

        '''[TCMS#284279 setup] Upload content to custom repo_xxx '''
        RHUIManagerRepo.upload_content(self.rs.Instances["RHUA"][0], ["repo_xxx"], "/root/rpms284279")

        """[TCMS#284279 setup] Create fake rpm"""
        Expect.enter(self.rs.Instances["RHUA"][0], "touch /root/rpms284279/fake.rpm && echo SUCCESS")

        '''[TCMS#284279 setup] Upload content to custom repo_yyy'''
        RHUIManager.screen(self.rs.Instances["RHUA"][0], "repo")
        Expect.enter(self.rs.Instances["RHUA"][0], "u")
        RHUIManager.select(self.rs.Instances["RHUA"][0], ["repo_yyy"])
        Expect.expect(self.rs.Instances["RHUA"][0], "will be uploaded:")
        Expect.enter(self.rs.Instances["RHUA"][0], "/root/rpms284279/fake.rpm")
        Expect.expect(self.rs.Instances["RHUA"][0], "error: not an rpm package")
        Expect.enter(self.rs.Instances["RHUA"][0], "q")

    def _test(self):
        '''[TCMS#284279 test] Check the packages list for repo284279'''
        expected_list = RHUIManagerRepo.check_for_package(self.rs.Instances["RHUA"][0], "Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)", "")
        actual_list = RHUIManagerRepo.check_for_package(self.rs.Instances["RHUA"][0], "repo284279", "")
        nose.tools.assert_equal(len(set(expected_list) - set(actual_list)), 0)

        '''[TCMS#284279 test] Check the packages list for repo_xxx'''
        nose.tools.assert_equal(RHUIManagerRepo.check_for_package(self.rs.Instances["RHUA"][0], "repo_xxx", ""), ["custom-signed-rpm-1-0.1.fc17.noarch.rpm", "custom-unsigned-rpm-1-0.1.fc17.noarch.rpm"])

        '''[TCMS#284279 test] Check the packages list for repo_yyy'''
        nose.tools.assert_equal(RHUIManagerRepo.check_for_package(self.rs.Instances["RHUA"][0], "repo_yyy", ""), [])

    def _cleanup(self):
        '''[TCMS#284279 cleanup] Delete custom repos '''
        RHUIManagerRepo.delete_repo(self.rs.Instances["RHUA"][0], ["repo284279"])
        RHUIManagerRepo.delete_repo(self.rs.Instances["RHUA"][0], ["repo_xxx"])
        RHUIManagerRepo.delete_repo(self.rs.Instances["RHUA"][0], ["repo_yyy"])

        '''[TCMS#284279 cleanup] Delete RH repo '''
        RHUIManagerRepo.delete_repo(self.rs.Instances["RHUA"][0], ["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])

        '''[TCMS#284279 cleanup] Remove RH certs from RHUI '''
        RHUIManager.remove_rh_certs(self.rs.Instances["RHUA"][0])

        '''[TCMS#284279 cleanup] Remove rpms from RHUI '''
        Expect.ping_pong(self.rs.Instances["RHUA"][0], " rm -f -r /root/rpms284279 && echo SUCCESS", "[^ ]SUCCESS")


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
