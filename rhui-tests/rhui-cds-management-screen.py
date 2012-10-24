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

cds_screen_items= \
    """.*l\s* list all CDS clusters and instances managed by the RHUI\s*\r\n\s*i\s* display detailed information on a CDS cluster\s*\r\n\s*a\s* register \(add\) a new CDS instance\s*\r\n\s*m\s* move CDS\(s\) to a different cluster\s*\r\n\s*d\s* unregister \(delete\) a CDS instance from the RHUI\s*\r\n\s*s\s* associate a repository with a CDS cluster\s*\r\n\s*u\s* unassociate a repository from a CDS cluster\s*\r\n.*=> """

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

Expect.expect(rs.RHUA, cds_screen_items)
Expect.enter(rs.RHUA, 'q')
