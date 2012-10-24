#!/usr/bin/python -tt
__all__ = []

import yaml, pexpect, sys
from rhui_manager import RhuiManager

session = pexpect.spawn("ssh root@rhua.example.com", logfile=sys.stdout)
session.expect("[$#] ")


with open('/root/rhui-testing-tools/lib/conf/Screens-nested.yaml') as fd:
    screen =  yaml.load(fd)

rhui = RhuiManager(session=session, screen=screen)
cds="cds1.example.com"
rhui.cds.add(cluster="cluster-1", display_name=cds, client_name=cds, host_name=cds)
rhui.quit()

session.close()
