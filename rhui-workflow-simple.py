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
rs.RHUA.addCustomRepo("repo1")
rs.RHUA.addCustomRepo("repo2")
rs.RHUA.associateRepoCds("Cluster1",["repo1", "repo2"])
rs.RHUA.uploadContent(["repo1", "repo2"], "/etc/rhui/confrpm")
rs.RHUA.syncCds(cdslist)

#it's impossible to do cluster sync and individual cds sync at the same moment
#rs.RHUA.syncCluster(["Cluster1"])

for cds in rs.CDS:
    rs.RHUA.deleteCds("Cluster1", [cds.hostname])
rs.RHUA.deleteCustomRepo(["repo1", "repo2"])
