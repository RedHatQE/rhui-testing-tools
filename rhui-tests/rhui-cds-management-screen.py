#! /usr/bin/python -tt

import  yaml, pexpect, sys, pxssh
from rhui_navigator import RhuiNavigator

rhui = None
screen = None
session = None

cds_screen_items=[ \
    """l.* list all CDS clusters and instances managed by the RHUI""",
    """i.* display detailed information on a CDS cluster""",
    """a.* register \(add\) a new CDS instance""",
    """m.* move CDS\(s\) to a different cluster""",
    """d.* unregister \(delete\) a CDS instance from the RHUI""",
    """s.* associate a repository with a CDS cluster""",
    """u.* unassociate a repository from a CDS cluster"""]

session = pexpect.spawn("ssh root@rhua.example.com", logfile=sys.stdout)
session.expect("[$#] ")
session.sendline("rhui-manager")
session.expect("=> ")

with open('conf/Screens-nested.yaml') as fd:
    screen =  yaml.load(fd)

rhui = RhuiNavigator(session=session, screen=screen)


with rhui.navigating('c'):
    for screen_item in cds_screen_items:
        rhui.expect(screen_item)


rhui.quit()
session.close()
