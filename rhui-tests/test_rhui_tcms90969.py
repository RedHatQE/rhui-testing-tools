#! /usr/bin/python -tt

import nose

from rhuilib.util import *
from rhuilib.rhui_testcase import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_repo import *
from rhuilib.rhuimanager_entitlements import *


class test_tcms_90969(RHUITestcase):
    def _setup(self):
        '''[TCMS#90969 setup] Do initial rhui-manager run'''
        RHUIManager.initial_run(self.rs.Instances["RHUA"][0])

        '''[TCMS#90969 setup] Create new config'''
        Expect.ping_pong(self.rs.Instances["RHUA"][0], "cat /etc/rhui/rhui-tools.conf | sed 's,^hostname:.*$,hostname: unresolvablehostname,' > /root/test-tcms-90969.conf && echo SUCCESS", "[^ ]SUCCESS", 10)

    def _test(self):
        '''[TCMS#90969 test] Check rhui-manager --config '''
        Expect.ping_pong(self.rs.Instances["RHUA"][0], "rhui-manager --username admin --password admin --config /root/test-tcms-90969.conf | grep '^Network error' && echo SUCCESS", "[^ ]SUCCESS", 10)

    def _cleanup(self):
        '''[TCMS#90969 cleanup] Remove repos '''
        Expect.ping_pong(self.rs.Instances["RHUA"][0], "rm -f /root/test-tcms-90969.conf && echo SUCCESS", "[^ ]SUCCESS", 10)
 

if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
