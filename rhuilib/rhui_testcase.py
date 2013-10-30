import os
import nose
import logging

from patchwork import structure
from patchwork.expect import *
from rhuilib.rhuimanager import *
from rhuilib.rhuimanager_sync import *


class RHUITestcase(object):
    @classmethod
    def setupAll(typeinstance):
        if "RHUI_TEST_DEBUG" is os.environ and os.environ["RHUI_TEST_DEBUG"] != "":
            loglevel = logging.DEBUG
        else:
            loglevel = logging.INFO
        logging.basicConfig(level=loglevel, format='%(asctime)s %(levelname)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
        typeinstance.rs = structure.Structure()
        typeinstance.rs.setup_from_yamlfile(yamlfile="/etc/rhui-testing.yaml", output_shell=True)
        typelist = [typeinstance]
        for cls in typelist:
            logging.debug("Exploring class " + str(cls))
            logging.debug("Adding base classes: " + str(list(cls.__bases__)) + " to typelist")
            for new_cls in list(cls.__bases__):
                if not new_cls in typelist:
                    logging.debug("Appending " + str(new_cls) + " to classlist")
                    typelist.append(new_cls)
            logging.debug("Checking for 'check' method of " + str(cls))
            if hasattr(cls, "check"):
                logging.debug("Calling 'check' for " + str(cls))
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
        if (not "RHUA" in self.rs.Instances.keys()) or len(self.rs.Instances["RHUA"]) < 1:
            raise nose.exc.SkipTest("can't test without RHUA!")
        try:
            RHUIManagerSync.sync_cds(self.rs.Instances["RHUA"][0], cdslist)
        except ExpectFailed:
            # The CDS is not available for syncing so most probably it's syncing right now
            # Trying to check the status
            Expect.enter(self.rs.Instances["RHUA"][0], "b")
            RHUIManager.quit(self.rs.Instances["RHUA"][0])
        for cds in cdslist:
            cdssync = ["UP", "In Progress", "", ""]
            while cdssync[1] == "In Progress":
                time.sleep(10)
                cdssync = RHUIManagerSync.get_cds_status(self.rs.Instances["RHUA"][0], cds)
            nose.tools.assert_equal(cdssync[3], "Success")

    def _sync_repo(self, repolist):
        if (not "RHUA" in self.rs.Instances.keys()) or len(self.rs.Instances["RHUA"]) < 1:
            raise nose.exc.SkipTest("can't test without RHUA!")
        try:
            RHUIManagerSync.sync_repo(self.rs.Instances["RHUA"][0], repolist)
        except ExpectFailed:
            # The repo is not available for syncing so most probably it's syncing right now
            # Trying to check the status
            Expect.enter(self.rs.Instances["RHUA"][0], "b")
            RHUIManager.quit(self.rs.Instances["RHUA"][0])
        for repo in repolist:
            reposync = ["In Progress", "", ""]
            while reposync[0] in ["In Progress", "Never"]:
                time.sleep(10)
                reposync = RHUIManagerSync.get_repo_status(self.rs.Instances["RHUA"][0], repo)
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
        if (not "CDS" in rs.Instances.keys()) or len(rs.Instances["CDS"]) < 2:
            raise nose.exc.SkipTest("can't test without having at least two CDSes!")


class RHUI_has_three_CDSes(object):
    @classmethod
    def check(self, rs):
        if (not "CDS" in rs.Instances.keys()) or len(rs.Instances["CDS"]) < 3:
            raise nose.exc.SkipTest("can't test without having at least three CDSes!")


class RHUI_has_two_CLIs_RHEL6(object):
    @classmethod
    def check(typeinstance, rs):
        if (not "CLI" in rs.Instances.keys()) or len(rs.Instances["CLI"]) < 2:
            raise nose.exc.SkipTest("can't test without having at least two CLIs!")
        typeinstance.rhel6client1 = None
        typeinstance.rhel6client2 = None
        for cli in rs.Instances["CLI"]:
            if 'OS' in cli.parameters.keys():
                if not typeinstance.rhel6client1 and cli.parameters['OS'] == "RHEL6":
                    typeinstance.rhel6client1 = cli
                elif not typeinstance.rhel6client2 and cli.parameters['OS'] == "RHEL6":
                    typeinstance.rhel6client2 = cli
        if not typeinstance.rhel6client1:
            raise nose.exc.SkipTest("No RHEL6 clients (two required), skipping test")
        if not typeinstance.rhel6client2:
            raise nose.exc.SkipTest("Only one RHEL6 client (two required), skipping test")


class RHUI_has_RHEL6_CLI(object):
    @classmethod
    def check(typeinstance, rs):
        if (not "CLI" in rs.Instances.keys()) or len(rs.Instances["CLI"]) < 1:
            raise nose.exc.SkipTest("can't test without having at least one CLI!")
        typeinstance.rhel6client = None
        for cli in rs.Instances["CLI"]:
            if 'OS' in cli.parameters.keys():
                if cli.parameters['OS'] == "RHEL6":
                    typeinstance.rhel6client = cli
                    break
        if not typeinstance.rhel6client:
            raise nose.exc.SkipTest("No RHEL6 clients, skipping test")


class RHUI_has_RHEL5_and_RHEL6_CLIs(object):
    @classmethod
    def check(typeinstance, rs):
        if (not "CLI" in rs.Instances.keys()) or len(rs.Instances["CLI"]) < 2:
            raise nose.exc.SkipTest("can't test without having at least two CLIs!")
        typeinstance.rhel5client = None
        typeinstance.rhel6client = None
        for cli in rs.Instances["CLI"]:
            if 'OS' in cli.parameters.keys():
                if not typeinstance.rhel6client and cli.parameters['OS'] == "RHEL6":
                    typeinstance.rhel6client = cli
                elif not typeinstance.rhel5client and cli.parameters['OS'] == "RHEL5":
                    typeinstance.rhel5client = cli
        if not typeinstance.rhel6client:
            raise nose.exc.SkipTest("No RHEL6 clients, skipping test")
        if not typeinstance.rhel5client:
            raise nose.exc.SkipTest("No RHEL5 clients, skipping test")


class RHUI_has_PROXY(object):
    @classmethod
    def check(self, rs):
        if (not "PROXY" in rs.Instances.keys()) or len(rs.Instances["PROXY"]) < 1:
            raise nose.exc.SkipTest("can't test without proxy!")
