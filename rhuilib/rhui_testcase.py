from rhuilib.rhuisetup import RHUIsetup
from rhuilib.rhuimanager_sync import *


class RHUITestcase(object):
    """Provides just the generic configuration fixtures and a basic sync stuff"""
    @classmethod
    def setupAll(test):
        # all happens class-level; this is called just when loading a test
        # class
        test.rs = RHUIsetup()
        test.rs.setup_from_yamlfile()
   @classmethod
   def teardownAll(test):
       del(test.rs)

    def _sync_cds(self, cdslist):
        RHUIManagerSync.sync_cds(self.rs.RHUA, cdslist)
        for cds in cdslist:
            cdssync = ["UP", "In Progress", "", ""]
            while cdssync[1] == "In Progress":
                time.sleep(10)
                cdssync = RHUIManagerSync.get_cds_status(self.rs.RHUA, cds)
            nose.tools.assert_equal(cdssync[3], "Success")

    def _sync_repo(self, repolist):
        RHUIManagerSync.sync_repo(self.rs.RHUA, repolist)
        for repo in repolist:
            reposync = ["In Progress", "", ""]
            while reposync[0] == "In Progress":
                time.sleep(10)
                reposync = RHUIManagerSync.get_repo_status(self.rs.RHUA, repo)
                nose.tools.assert_equal(reposync[2], "Success")
