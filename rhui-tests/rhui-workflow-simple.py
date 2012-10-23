#! /usr/bin/python -tt

import logging

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

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

rs = RHUIsetup()
rs.setup_from_rolesfile()
RHUIManager.initial_run(rs.RHUA)

cdslist = []
for cds in rs.CDS:
    cdslist.append(cds.hostname)
    RHUIManagerCds.add_cds(rs.RHUA,"Cluster1", cds.hostname)

for cli in rs.CLI:
    Util.remove_conf_rpm(cli)

RHUIManagerRepo.add_custom_repo(rs.RHUA, "repo1")
RHUIManagerRepo.add_custom_repo(rs.RHUA, "repo2")
RHUIManagerCds.associate_repo_cds(rs.RHUA, "Cluster1", ["repo1", "repo2"])
RHUIManagerRepo.upload_content(rs.RHUA, ["repo1", "repo2"], "/etc/rhui/confrpm")
RHUIManagerSync.sync_cds(rs.RHUA, cdslist)

##it's impossible to do cluster sync and individual cds sync at the same moment
##RHUIManagerSync.sync_cluster(rs.RHUA,["Cluster1"])

RHUIManagerClient.generate_ent_cert(rs.RHUA, "Cluster1", ["repo1"], "cert-repo1", "/root/", validity_days="", cert_pw=None)
RHUIManagerClient.create_conf_rpm(rs.RHUA, "Cluster1", cdslist[0], "/root", "/root/cert-repo1.crt", "/root/cert-repo1.key", "repo1", "3.0")
rs.RHUA.sftp.get("/root/repo1-3.0/build/RPMS/noarch/repo1-3.0-1.noarch.rpm","/root/repo1-3.0-1.noarch.rpm")
Util.install_rpm_from_master(rs.CLI[0], "/root/repo1-3.0-1.noarch.rpm")

for cds in rs.CDS:
    RHUIManagerCds.delete_cds(rs.RHUA, "Cluster1", [cds.hostname])
RHUIManagerRepo.delete_custom_repo(rs.RHUA, ["repo1", "repo2"])
RHUIManagerIdentity.generate_new(rs.RHUA)
RHUIManagerUsers.change_password(rs.RHUA, "admin", "admin2")
