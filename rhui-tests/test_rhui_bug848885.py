#! /usr/bin/python -tt

import nose
import re

from patchwork.expect import *
from rhuilib.util import *
from rhuilib.rhui_testcase import *


class test_bug_848885(RHUITestcase, RHUI_has_PROXY):
    def _setup(self):
        '''[Bug#848885 setup] Figure out the version of configuration rpm'''
        Expect.enter(self.rs.Instances["RHUA"][0], "rpm -q --queryformat \"###%{VERSION}###\" " + self.rs.Instances["RHUA"][0].private_hostname)

        version_old = Expect.match(self.rs.Instances["RHUA"][0],  re.compile(".*###([0-9]+\.[0-9]+)###.*", re.DOTALL))[0]

        version_new = str(float(version_old)+0.1)

        Expect.ping_pong(self.rs.Instances["RHUA"][0], "rm -f /tmp/bug848885.ver && echo -n " + version_old + " > /tmp/bug848885.ver && echo SUCCESS", "[^ ]SUCCESS")

        '''[Bug#848885 setup] Generate new configuration RPMs '''
        Util.generate_answers(self.rs, version=version_new, generate_certs=False, proxy_host=self.rs.Instances["PROXY"][0].private_hostname, proxy_port=None, proxy_user="rhua", proxy_password=None)

        Expect.ping_pong(self.rs.Instances["RHUA"][0], "rhui-installer /etc/rhui/answers && echo SUCCESS", "[^ ]SUCCESS", 30)

        '''[Bug#848885 setup] Update configuration RPM '''
        Expect.ping_pong(self.rs.Instances["RHUA"][0], "rpm -U /etc/rhui/confrpm/" + self.rs.Instances["RHUA"][0].private_hostname + "-" + version_new + "-*.rpm && echo SUCCESS", "[^ ]SUCCESS", 60)

    def _test(self):
        '''[Bug#848885 setup] Check for proxy_port/proxy_pass settings (shouldn't be set) '''
        Expect.expect_retval(self.rs.Instances["RHUA"][0], "grep -P \"^(proxy_port|proxy_pass)\" /etc/pulp/pulp.conf  /etc/rhui/rhui-tools.conf", 1)

    def _cleanup(self):
        '''[Bug#848885 cleanup] Restore configuration RPM '''
        Expect.expect_retval(self.rs.Instances["RHUA"][0], "[ -f /tmp/bug848885.ver ] && rpm -U --oldpackage /etc/rhui/confrpm/" + self.rs.Instances["RHUA"][0].private_hostname + "-`cat /tmp/bug848885.ver`-*.rpm", timeout=60)

        Expect.expect_retval(self.rs.Instances["RHUA"][0], "rm -f /tmp/bug848885.ver ||:")


if __name__ == "__main__":
    nose.run(defaultTest=__name__, argv=[__file__, '-v'])
