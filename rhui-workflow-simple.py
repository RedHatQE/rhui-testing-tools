import rhuilib
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

rs = rhuilib.RHUIsetup()
rs.setupFromRolesfile()
rs.RHUA.initialRun()

# do not uncomment, will take too long to finish
#rs.RHUA.generateGpgKey()

cdslist = []
for cds in rs.CDS:
    cdslist.append(cds.hostname)
    rs.RHUA.addCds("Cluster1", cds.hostname)

for cli in rs.CLI:
    cli.removeConfigurationRpm()

rs.RHUA.addCustomRepo("repo1")
rs.RHUA.addCustomRepo("repo2")
rs.RHUA.associateRepoCds("Cluster1", ["repo1", "repo2"])
rs.RHUA.uploadContent(["repo1", "repo2"], "/etc/rhui/confrpm")
rs.RHUA.syncCds(cdslist)

#it's impossible to do cluster sync and individual cds sync at the same moment
#rs.RHUA.syncCluster(["Cluster1"])

rs.RHUA.generateEntitlementCert("Cluster1", ["repo1"], "cert-repo1", "/root/", validity_days="", cert_pw=None)
rs.RHUA.createConfigurationRpm("Cluster1", cdslist[0], "/root", "/root/cert-repo1.crt", "/root/cert-repo1.key", "repo1", "3.0")
rs.RHUA.sftp.get("/root/repo1-3.0/build/RPMS/noarch/repo1-3.0-1.noarch.rpm","/root/repo1-3.0-1.noarch.rpm")
rs.CLI[0].installRpmFromMaster("/root/repo1-3.0-1.noarch.rpm")

for cds in rs.CDS:
    rs.RHUA.deleteCds("Cluster1", [cds.hostname])
rs.RHUA.deleteCustomRepo(["repo1", "repo2"])
