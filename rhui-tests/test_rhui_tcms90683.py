#! /usr/bin/python -tt

import nose

from rhuilib.util import *
from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_cds import *


class test_tcms_90683(RHUITestcase):
    def _setup(self):
        '''[TCMS#90683 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.Instances["RHUA"][0])

    def _test(self):
        '''[TCMS#90683 test] Stop pulp-cds '''
        Expect.ping_pong(self.rs.Instances["CDS"][0], "service pulp-cds stop && echo SUCCESS", "[^ ]SUCCESS", 30)

        '''[TCMS#90683 test] Change gopher password location '''
        Expect.ping_pong(self.rs.Instances["CDS"][0], "sed -i 's,^secret_file = .*$,secret_file = /var/lib/pulp-cds/.gofer/newsecret,' /etc/gofer/plugins/cdsplugin.conf && echo SUCCESS", "[^ ]SUCCESS")

        '''[TCMS#90683 test] Start pulp-cds '''
        Expect.ping_pong(self.rs.Instances["CDS"][0], "service pulp-cds start && echo SUCCESS", "[^ ]SUCCESS", 30)

        '''[TCMS#90683 setup] Add cdses '''
        RHUIManagerCds.add_cds(self.rs.Instances["RHUA"][0], "Cluster1", self.rs.Instances["CDS"][0].private_hostname)

        '''[TCMS#90683 test] Check for new file '''
        Expect.ping_pong(self.rs.Instances["CDS"][0], "[ -f /var/lib/pulp-cds/.gofer/newsecret ] && echo SUCCESS", "[^ ]SUCCESS", 30)

    def _cleanup(self):
        '''[TCMS#90683 cleanup] Remove cds '''
        RHUIManagerCds.delete_cds(self.rs.Instances["RHUA"][0], "Cluster1", [self.rs.Instances["CDS"][0].private_hostname])

        '''[TCMS#90683 cleanup] Stop pulp-cds '''
        Expect.ping_pong(self.rs.Instances["CDS"][0], "service pulp-cds stop && echo SUCCESS", "[^ ]SUCCESS", 30)

        '''[TCMS#90683 cleanup] Change gopher password location '''
        Expect.ping_pong(self.rs.Instances["CDS"][0], "sed -i 's,^secret_file = .*$,secret_file = /var/lib/pulp-cds/.gofer/secret,' /etc/gofer/plugins/cdsplugin.conf && echo SUCCESS", "[^ ]SUCCESS")

        '''[TCMS#90683 cleanup] Start pulp-cds '''
        Expect.ping_pong(self.rs.Instances["CDS"][0], "service pulp-cds start && echo SUCCESS", "[^ ]SUCCESS", 30)


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
