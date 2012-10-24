#! /usr/bin/python -tt

import logging
import argparse

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

argparser = argparse.ArgumentParser(description='RHUI simple workflow')
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

cdslist = []
for cds in rs.CDS:
    cdslist.append(cds.hostname)
    RHUIManagerCds.add_cds(rs.RHUA, "Cluster1", cds.hostname)

for cli in rs.CLI:
    Util.remove_conf_rpm(cli)

RHUIManagerRepo.add_custom_repo(rs.RHUA, "repo1")
RHUIManagerRepo.add_custom_repo(rs.RHUA, "repo2")
RHUIManagerCds.associate_repo_cds(rs.RHUA, "Cluster1", ["repo1", "repo2"])
RHUIManagerRepo.upload_content(rs.RHUA, ["repo1", "repo2"], "/etc/rhui/confrpm")
RHUIManagerSync.sync_cds(rs.RHUA, cdslist)

RHUIManagerClient.generate_ent_cert(rs.RHUA, "Cluster1", ["repo1"], "cert-repo1", "/root/", validity_days="", cert_pw=None)

##it's impossible to do cluster sync and individual cds sync at the same moment
##RHUIManagerSync.sync_cluster(rs.RHUA,["Cluster1"])

if args.cert:
    RHUIManagerEntitlements.upload_content_cert(rs.RHUA, args.cert)
    RHUIManagerRepo.add_rh_repo_by_product(rs.RHUA, ["Red Hat Enterprise Linux 6 Server - Supplementary from RHUI \(RPMs\)", "Red Hat Enterprise Linux 6 Server from RHUI \(RPMs\)"])
    RHUIManagerRepo.add_rh_repo_by_repo(rs.RHUA, ["Red Hat Enterprise Linux 5 Server from RHUI \(RPMs\) \(5Server-i386\)", "Red Hat Enterprise Linux 5 Server from RHUI \(RPMs\) \(5Server-x86_64\)"])
    RHUIManagerRepo.add_rh_repo_all(rs.RHUA)
    RHUIManagerSync.sync_repo(rs.RHUA, ["Red Hat Enterprise Linux 5 Server from RHUI \(RPMs\) \(5Server-i386\)", "Red Hat Enterprise Linux 5 Server from RHUI \(RPMs\) \(5Server-x86_64\)", "Red Hat Enterprise Linux 6 Server from RHUI \(RPMs\) \(6Server-x86_64\)"])
    RHUIManagerCds.associate_repo_cds(rs.RHUA, "Cluster1", ["Red Hat Enterprise Linux 6 Server from RHUI \(RPMs\) \(6Server-x86_64\)"])
    RHUIManagerClient.generate_ent_cert(rs.RHUA, "Cluster1", ["repo1", "Red Hat Enterprise Linux 6 Server from RHUI \(RPMs\)"], "cert-repo1", "/root/", validity_days="", cert_pw=None)

RHUIManagerClient.create_conf_rpm(rs.RHUA, "Cluster1", cdslist[0], "/root", "/root/cert-repo1.crt", "/root/cert-repo1.key", "repo1", "3.0")
rs.RHUA.sftp.get("/root/repo1-3.0/build/RPMS/noarch/repo1-3.0-1.noarch.rpm", "/root/repo1-3.0-1.noarch.rpm")
Util.install_rpm_from_master(rs.CLI[0], "/root/repo1-3.0-1.noarch.rpm")

RHUIManagerIdentity.generate_new(rs.RHUA)
RHUIManagerUsers.change_password(rs.RHUA, "admin", "admin2")

# delete testing - uncomment if necessary
# for cds in rs.CDS:
#    RHUIManagerCds.delete_cds(rs.RHUA, "Cluster1", [cds.hostname])
# RHUIManagerRepo.delete_custom_repo(rs.RHUA, ["repo1", "repo2"])
