import nose
import logging

from rhuilib.rhuisetup import *
from rhuilib.rhuimanager_sync import *


class RHUITestcase(object):
    @classmethod
    def setupAll(typeinstance):
        typeinstance.rs = RHUIsetup()
        typeinstance.rs.setup_from_yamlfile()
        for cls in list(typeinstance.__bases__) + [typeinstance]:
            logging.debug("Calling check for " + str(cls))
            if hasattr(cls, "check"):
                cls.check(typeinstance.rs)

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
            self.rs.reconnect_all()
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


class RHUI_has_RH_rpm(object):
    @classmethod
    def check(self, rs):
        if not 'rhrpm' in rs.config.keys():
            raise nose.exc.SkipTest("can't test without RH-signed RPM")
        self.rhrpm = rs.config['rhrpm']
        (self.rhrpmnvr, self.rhrpmname) = Util.get_rpm_details(self.rhrpm)


class RHUI_has_RH_cert(object):
    @classmethod
    def check(self, rs):
        if not 'rhcert' in rs.config.keys():
            raise nose.exc.SkipTest("can't test without RH certificate")
        self.cert = rs.config['rhcert']


class RHUI_has_two_CDSes(object):
    @classmethod
    def check(self, rs):
        if len(rs.CDS) < 2:
            raise nose.exc.SkipTest("can't test without having at least two CDSes!")


class RHUI_has_three_CDSes(object):
    @classmethod
    def check(self, rs):
        if len(rs.CDS) < 3:
            raise nose.exc.SkipTest("can't test without having at least three CDSes!")
