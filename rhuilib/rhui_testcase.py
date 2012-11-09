import nose

from rhuilib.rhuisetup import *
from rhuilib.rhuimanager_sync import *


class RHUITestcase(object):
    @classmethod
    def setupAll(typeinstance):
        typeinstance.rs = RHUIsetup()
        typeinstance.rs.setup_from_yamlfile()

    @classmethod
    def teardownAll(typeinstance):
        typeinstance.rs.__del__()

    def __init__(self):
        if hasattr(self, "_init"):
            self._init()

    def test_01_setup(self):
        if hasattr(self, "_setup"):
            self._setup()

    def test_02_test(self):
        if hasattr(self, "_test"):
            self._test()

    def test_03_cleanup(self):
        if hasattr(self, "_cleanup"):
            self._cleanup()

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
