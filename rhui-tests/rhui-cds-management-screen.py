#! /usr/bin/python -tt

import logging
import argparse
from nose.tools import *

from rhuilib.util import *
from rhuilib.rhuisetup import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_cds import *
from rhuilib.rhuimanager_client import *
from rhuilib.rhuimanager_repo import *
from rhuilib.rhuimanager_sync import *
from rhuilib.rhuimanager_identity import *
from rhuilib.rhuimanager_users import *
from rhuilib.rhuimanager_entitlements import *

cds_screen_items=[ \
    """l.* list all CDS clusters and instances managed by the RHUI""",
    """i.* display detailed information on a CDS cluster""",
    """a.* register \(add\) a new CDS instance""",
    """m.* move CDS\(s\) to a different cluster""",
    """d.* unregister \(delete\) a CDS instance from the RHUI""",
    """s.* associate a repository with a CDS cluster""",
    """u.* unassociate a repository from a CDS cluster"""]

argparser = argparse.ArgumentParser(description='RHUI CDS Management Screen')
argparser.add_argument('--debug', action='store_const', const=True,
                       default=False, help='debug mode')
argparser.add_argument('--cert',
                       help='use supplied RH enablement certificate')
args = argparser.parse_args()

if args.debug:
    loglevel = logging.DEBUG
else:
    loglevel = logging.INFO

logging.basicConfig(level=loglevel, format='%(asctime)s %(levelname)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

rs = RHUIsetup()
rs.setup_from_rolesfile()
RHUIManager.initial_run(rs.RHUA)
Expect.enter(rs.RHUA, "rhui-manager")
Expect.expect(rs.RHUA, "rhui \(home\) => ")
Expect.enter(rs.RHUA, "c")

for screen_item in cds_screen_expression:
    Expect.expect(rs.RHUA, screen_item)
Expect.expect(rs.RHUA, "rhui \(cds\) => ")
RHUIManager.quit(rs.RHUA)
