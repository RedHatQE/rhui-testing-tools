#! /usr/bin/python -tt

import nose

from rhuilib.util import *
from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_cds import *
from rhuilib.rhuimanager_client import *
from rhuilib.rhuimanager_repo import *
from rhuilib.rhuimanager_sync import *
from rhuilib.rhuimanager_entitlements import *


class test_0_update_212_unclean(RHUITestcase, RHUI_has_RH_cert):
    def _setup(self):
        '''[Update 2.1.2 unclean setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.Instances["RHUA"][0])

        '''[Update 2.1.2 unclean setup] Add cds '''
        RHUIManagerCds.add_cds(self.rs.Instances["RHUA"][0], "Cluster1", self.rs.Instances["CDS"][0].private_hostname)

        '''[Update 2.1.2 unclean setup] Upload RH content certificate '''
        RHUIManagerEntitlements.upload_content_cert(self.rs.Instances["RHUA"][0], self.cert)

        '''[Update 2.1.2 unclean setup] Add rh repo '''
        RHUIManagerRepo.add_rh_repo_by_repo(self.rs.Instances["RHUA"][0], ["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])

        '''[Update 2.1.2 unclean setup] Associate repos with cluster '''
        RHUIManagerCds.associate_repo_cds(self.rs.Instances["RHUA"][0], "Cluster1", ["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])

        '''[Update 2.1.2 unclean setup] Remove rhui configuration rpm from RHUA '''
        Util.remove_conf_rpm(self.rs.Instances["RHUA"][0])

        '''[Update 2.1.2 unclean setup] Sync RH repo '''
        self._sync_repo(["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])

        '''[Update 2.1.2 unclean setup] Sync cds '''
        self._sync_cds([self.rs.Instances["CDS"][0].private_hostname])

        '''[Update 2.1.2 unclean setup] Generate entitlement certificate '''
        RHUIManagerClient.generate_ent_cert(self.rs.Instances["RHUA"][0], "Cluster1", ["Red Hat Update Infrastructure 2 \(RPMs\)"], "cert-repo1", "/root/", validity_days="", cert_pw=None)

        '''[Update 2.1.2 unclean setup] Create configuration rpm '''
        RHUIManagerClient.create_conf_rpm(self.rs.Instances["RHUA"][0], "Cluster1", self.rs.Instances["CDS"][0].private_hostname, "/root", "/root/cert-repo1.crt", "/root/cert-repo1.key", "repo1", "3.0")

        '''[Update 2.1.2 unclean setup] Install configuration rpm to RHUA '''
        Expect.ping_pong(self.rs.Instances["RHUA"][0], "yum install -y /root/repo1-3.0/build/RPMS/noarch/repo1-3.0-1.noarch.rpm && echo SUCCESS", "[^ ]SUCCESS", 60)

        '''[Update 2.1.2 unclean setup] Install configuration rpm to all CDSes '''
        for cds in self.rs.Instances["CDS"]:
            Util.remove_conf_rpm(cds)
            Util.install_rpm_from_rhua(self.rs.Instances["RHUA"][0], cds, "/root/repo1-3.0/build/RPMS/noarch/repo1-3.0-1.noarch.rpm")

    def _test(self):
        '''[Update 2.1.2 unclean test] Upgrade RHUI '''
        Expect.ping_pong(self.rs.Instances["RHUA"][0], "yum -y update && echo SUCCESS", "[^ ]SUCCESS", 240)

        '''[Update 2.1.2 unclean test] Do pulp-migrate '''
        Expect.ping_pong(self.rs.Instances["RHUA"][0], "pulp-migrate && echo SUCCESS", "[^ ]SUCCESS", 60)

        '''[Update 2.1.2 unclean test] Modify pulp.conf '''
        Expect.ping_pong(self.rs.Instances["RHUA"][0], "sed -i 's,verify_checksum:.*$,verify_checksum: true,' /etc/pulp/pulp.conf && echo SUCCESS", "[^ ]SUCCESS", 60)
        Expect.ping_pong(self.rs.Instances["RHUA"][0], "sed -i 's,verify_size:.*$,verify_size: true,' /etc/pulp/pulp.conf && echo SUCCESS", "[^ ]SUCCESS", 60)

        '''[Update 2.1.2 unclean test] Stop pulp server '''
        Expect.ping_pong(self.rs.Instances["RHUA"][0], "service pulp-server stop && echo SUCCESS", "[^ ]SUCCESS", 20)

        '''[Update 2.1.2 unclean test] Do pulp-package-migrate '''
        Expect.ping_pong(self.rs.Instances["RHUA"][0], "echo Y | pulp-package-migrate --migrate -d /var/lib/pulp && echo SUCCESS", "[^ ]SUCCESS", 120)

        '''[Update 2.1.2 unclean test] Start pulp server '''
        Expect.ping_pong(self.rs.Instances["RHUA"][0], "service pulp-server start && echo SUCCESS", "[^ ]SUCCESS", 20)

        '''[Update 2.1.2 unclean test] Sync repos '''
        self._sync_repo(["Red Hat Update Infrastructure 2 \(RPMs\) \(6Server-x86_64\)"])

        '''[Update 2.1.2 unclean test] Modify pulp.conf '''
        Expect.ping_pong(self.rs.Instances["RHUA"][0], "sed -i 's,verify_checksum:.*$,verify_checksum: false,' /etc/pulp/pulp.conf && echo SUCCESS", "[^ ]SUCCESS", 60)
        Expect.ping_pong(self.rs.Instances["RHUA"][0], "sed -i 's,verify_size:.*$,verify_size: false,' /etc/pulp/pulp.conf && echo SUCCESS", "[^ ]SUCCESS", 60)

        '''[Update 2.1.2 unclean test] Restart pulp server '''
        Expect.ping_pong(self.rs.Instances["RHUA"][0], "service pulp-server restart && echo SUCCESS", "[^ ]SUCCESS", 20)

        '''[Update 2.1.2 unclean test] Update all CDSes '''
        for cds in self.rs.Instances["CDS"]:
            Expect.ping_pong(cds, "yum -y update && echo SUCCESS", "[^ ]SUCCESS", 240)

            '''[Update 2.1.2 unclean test] Modify pulp.conf '''
            Expect.ping_pong(self.rs.Instances["RHUA"][0], "sed -i 's,verify_checksum:.*$,verify_checksum: true,' /etc/pulp/cds.conf && echo SUCCESS", "[^ ]SUCCESS", 60)
            Expect.ping_pong(self.rs.Instances["RHUA"][0], "sed -i 's,verify_size:.*$,verify_size: true,' /etc/pulp/cds.conf && echo SUCCESS", "[^ ]SUCCESS", 60)

            Expect.ping_pong(cds, "service pulp-cds stop && echo SUCCESS", "[^ ]SUCCESS", 20)

            '''[Update 2.1.2 unclean test] Do pulp-package-migrate '''
            Expect.ping_pong(self.rs.Instances["RHUA"][0], "echo Y | pulp-package-migrate --migrate -d /var/lib/pulp-cds && echo SUCCESS", "[^ ]SUCCESS", 120)

            '''[Update 2.1.2 unclean test] Start goferd server '''
            Expect.ping_pong(cds, "service goferd start && echo SUCCESS", "[^ ]SUCCESS", 20)

            '''[Update 2.1.2 unclean test] Sync cds '''
            self._sync_cds([cds.private_hostname])

            '''[Update 2.1.2 unclean test] Modify pulp.conf '''
            Expect.ping_pong(self.rs.Instances["RHUA"][0], "sed -i 's,verify_checksum:.*$,verify_checksum: false,' /etc/pulp/cds.conf && echo SUCCESS", "[^ ]SUCCESS", 60)
            Expect.ping_pong(self.rs.Instances["RHUA"][0], "sed -i 's,verify_size:.*$,verify_size: false,' /etc/pulp/cds.conf && echo SUCCESS", "[^ ]SUCCESS", 60)

            '''[Update 2.1.2 unclean test] Restart pulp-cds'''
            Expect.ping_pong(cds, "service pulp-cds restart && echo SUCCESS", "[^ ]SUCCESS", 20)

    def _cleanup(self):
        '''[Update 2.1.2 unclean cleanup] Pass '''
        pass


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
