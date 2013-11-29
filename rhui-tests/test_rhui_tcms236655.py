#! /usr/bin/python -tt

import nose

from patchwork.expect import *
from rhuilib.rhui_testcase import *


class test_tcms_236655(RHUITestcase):
    def _setup(self):
        pass

    def _test(self):
        '''[TCMS#236655 test] Check nss-db-gen cert validity '''
        for cert in ["broker", "ca"]:
            Expect.ping_pong(self.rs.Instances["RHUA"][0], "echo \"Valid for:\" $(($(($(date -d \"`certutil -L -d /etc/pki/rhua/qpid-nss/ -n " + cert + " | grep \"Not After :\" | sed 's,.*Not After : ,,'`\" +%s) - $(date -d \"`certutil -L -d /etc/pki/rhua/qpid-nss/ -n " + cert + " | grep \"Not Before:\" | sed 's,.*Not Before: ,,'`\" +%s)))/3650/24/30))", "Valid for: 360")

    def _cleanup(self):
        pass

if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
