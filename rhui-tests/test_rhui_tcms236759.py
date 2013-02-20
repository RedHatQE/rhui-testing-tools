#! /usr/bin/python -tt

import nose
import re

from patchwork.expect import *
from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *


class test_tcms_236759(RHUITestcase, RHUI_has_RH_cert):
    def _setup(self):
        '''[TCMS#236759 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.Instances["RHUA"][0])

    def _test(self):
        '''[TCMS#236759 test] Running rhui-debug.py on RHUA '''
        Expect.enter(self.rs.Instances["RHUA"][0], "python /usr/share/rh-rhua/rhui-debug.py")
        debugdir = Expect.match(self.rs.Instances["RHUA"][0], re.compile(".*Successfully created directory \[([^\]]*)\].*", re.DOTALL))
        for name in ["/root/.rhui/", "/etc/pulp/", "/etc/gofer/plugins/", "/var/log/pulp/", "/etc/rhui/rhui-tools.conf", "/etc/httpd/conf.d/pulp.conf", "/etc/yum/pluginconf.d/pulp-profile-update.conf", "/etc/pki/pulp/content/pulp-protected-repos"]:
            Expect.enter(self.rs.Instances["RHUA"][0], "ls -1 " + debugdir[0] + name + " && echo SUCCESS")
            Expect.expect(self.rs.Instances["RHUA"][0], "[^ ]SUCCESS")
        Expect.enter(self.rs.Instances["RHUA"][0], "ls -lR /var/lib/pulp | diff -u " + debugdir[0] + "/commands/ls_-lR_var.lib.pulp - && echo SUCCESS")
        Expect.expect(self.rs.Instances["RHUA"][0], "[^ ]SUCCESS")

        '''[TCMS#236759 test] Running rhui-debug.py on CDS '''
        Expect.enter(self.rs.Instances["CDS"][0], "python /usr/share/rh-rhua/rhui-debug.py --cds")
        debugdir = Expect.match(self.rs.Instances["CDS"][0], re.compile(".*Successfully created directory \[([^\]]*)\].*", re.DOTALL))
        for name in ["/etc/pulp/", "/etc/gofer/plugins/", "/var/log/pulp-cds/", "/etc/httpd/conf.d/pulp-cds.conf", "/var/log/gofer/agent.log"]:
            Expect.enter(self.rs.Instances["CDS"][0], "ls -1 " + debugdir[0] + name + " && echo SUCCESS")
            Expect.expect(self.rs.Instances["CDS"][0], "[^ ]SUCCESS")
        Expect.enter(self.rs.Instances["CDS"][0], "ls -lR /var/lib/pulp-cds | diff -u " + debugdir[0] + "/commands/ls_-lR_var.lib.pulp-cds - && echo SUCCESS")
        Expect.expect(self.rs.Instances["CDS"][0], "[^ ]SUCCESS")

    def _cleanup(self):
        pass

if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
