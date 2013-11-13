#! /usr/bin/python -tt

import nose
import re

from patchwork.expect import *
from rhuilib.util import *
from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_identity import *


class test_tcms_116076(RHUITestcase):
    def _setup(self):
        """[TCMS#116076 setup] Do initial rhui-manager run"""
        RHUIManager.initial_run(self.rs.Instances["RHUA"][0])

    def _test(self):
        """[TCMS#116076 test] Get /etc/pki/rhui/identity.crt md5sum"""
        Expect.enter(self.rs.Instances["RHUA"][0], 'echo "###START###" && md5sum /etc/pki/rhui/identity.crt | cut -f 1 -d " " && echo "###STOP###"')
        md5_1 = Expect.match(self.rs.Instances["RHUA"][0], re.compile('.*###START###\r\n(.*)\r\n###STOP###.*', re.DOTALL))[0]

        """[TCMS#116076 test] Generate new identity"""
        RHUIManagerIdentity.generate_new(self.rs.Instances["RHUA"][0])

        """[TCMS#116076 test] Generate new identity"""
        Expect.ping_pong(self.rs.Instances["RHUA"][0], 'echo $(($(echo $(openssl x509 -in /etc/pki/rhui/identity.crt -noout -dates | grep notAfter | sed s,.*=,,) | cut -f 4 -d " ")-$(date +%Y)))', '20')

        """[TCMS#116076 test] Get /etc/pki/rhui/identity.crt new md5sum"""
        Expect.enter(self.rs.Instances["RHUA"][0], 'echo "###START###" && md5sum /etc/pki/rhui/identity.crt | cut -f 1 -d " " && echo "###STOP###"')
        md5_2 = Expect.match(self.rs.Instances["RHUA"][0], re.compile('.*###START###\r\n(.*)\r\n###STOP###.*', re.DOTALL))[0]

        """[TCMS#116076 test] Compare checksums"""
        Expect.ping_pong(self.rs.Instances["RHUA"][0], "[ %s != %s ] && echo SUCCESS" % (md5_1, md5_2), '[^ ]SUCCESS')

    def _cleanup(self):
        """[TCMS#116076 cleanup] Do nothing"""
        pass


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
