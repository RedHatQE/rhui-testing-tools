""" RHUI testcase """

import os
import nose
import logging
import time

from patchwork import structure
from patchwork.expect import Expect, ExpectFailed
from rhuilib.rhuimanager import RHUIManager
from rhuilib.rhuimanager_sync import RHUIManagerSync
from rhuilib.util import Util


class RHUITestcase(object):
    """ RHUI testcase """
    # pylint: disable=E1101

    @classmethod
    def setupAll(cls):
        """ Setup """
        if "RHUI_TEST_DEBUG" is os.environ and os.environ["RHUI_TEST_DEBUG"] != "":
            loglevel = logging.DEBUG
        else:
            loglevel = logging.INFO
        logging.basicConfig(level=loglevel, format='%(asctime)s %(levelname)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
        cls.rs = structure.Structure()
        cls.rs.setup_from_yamlfile(yamlfile="/etc/rhui-testing.yaml", output_shell=True)
        typelist = [cls]
        for class_name in typelist:
            logging.debug("Exploring class " + str(class_name))
            logging.debug("Adding base classes: " + str(list(class_name.__bases__)) + " to typelist")
            for new_cls in list(class_name.__bases__):
                if not new_cls in typelist:
                    logging.debug("Appending " + str(new_cls) + " to classlist")
                    typelist.append(new_cls)
            logging.debug("Checking for 'check' method of " + str(class_name))
            if hasattr(class_name, "check"):
                logging.debug("Calling 'check' for " + str(class_name))
                class_name.check(cls.rs)

    @classmethod
    def teardownAll(cls):
        """ Teardown """
        cls.rs.__del__()

    def __init__(self):
        if hasattr(self, "_init"):
            self._init()

    def test_01_setup(self):
        """ Setup """
        if hasattr(self, "_setup"):
            self._setup()

    def test_02_test(self):
        """ Test """
        if hasattr(self, "_test"):
            self._test()

    def test_03_cleanup(self):
        """ Cleanup """
        if hasattr(self, "_cleanup"):
            self.rs.reconnect_all()
            self._cleanup()

    def _sync_cds(self, cdslist):
        """ Sync cds """
        if (not "RHUA" in self.rs.Instances.keys()) or len(self.rs.Instances["RHUA"]) < 1:
            raise nose.exc.SkipTest("can't test without RHUA!")
        try:
            RHUIManagerSync.sync_cds(self.rs.Instances["RHUA"][0], cdslist)
        except ExpectFailed:
            # The CDS is not available for syncing so most probably it's syncing right now
            # Trying to check the status
            Expect.enter(self.rs.Instances["RHUA"][0], "b")
            RHUIManager.quit(self.rs.Instances["RHUA"][0])
        self._sync_wait_cds(cdslist)

    def _sync_wait_cds(self, cdslist):
        """ Sync CDS and wait """
        # waits for the cds sync conclusion
        for cds in cdslist:
            cdssync = ["UP", "In Progress", "", ""]
            while cdssync[1] == "In Progress":
                time.sleep(10)
                cdssync = RHUIManagerSync.get_cds_status(self.rs.Instances["RHUA"][0], cds)
            nose.tools.assert_equal(cdssync[3], "Success")

    def _sync_repo(self, repolist):
        """ Sync repo """
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
    """ Has RH-signed RPM """
    @classmethod
    def check(cls, rs):
        """ Check """
        if not 'rhrpm' in rs.config.keys():
            raise nose.exc.SkipTest("can't test without RH-signed RPM")
        cls.rhrpm = rs.config['rhrpm']
        (cls.rhrpmnvr, cls.rhrpmname) = Util.get_rpm_details(cls.rhrpm)


class RHUI_has_RH_cert(object):
    """ Has RH cert """
    @classmethod
    def check(cls, rs):
        """ Check """
        if not 'rhcert' in rs.config.keys():
            raise nose.exc.SkipTest("can't test without RH certificate")
        cls.cert = rs.config['rhcert']


class RHUI_has_two_CDSes(object):
    """ Has two CDSes """
    @classmethod
    def check(cls, rs):
        """ Check """
        if (not "CDS" in rs.Instances.keys()) or len(rs.Instances["CDS"]) < 2:
            raise nose.exc.SkipTest("can't test without having at least two CDSes!")


class RHUI_has_three_CDSes(object):
    """ Has three CDSes """
    @classmethod
    def check(cls, rs):
        """ Check """
        if (not "CDS" in rs.Instances.keys()) or len(rs.Instances["CDS"]) < 3:
            raise nose.exc.SkipTest("can't test without having at least three CDSes!")


class RHUI_has_two_CLIs_RHEL6(object):
    """ Has two RHEL6 CLIs """
    @classmethod
    def check(cls, rs):
        """ Check """
        if (not "CLI" in rs.Instances.keys()) or len(rs.Instances["CLI"]) < 2:
            raise nose.exc.SkipTest("can't test without having at least two CLIs!")
        cls.rhel6client1 = None
        cls.rhel6client2 = None
        for cli in rs.Instances["CLI"]:
            if 'OS' in cli.parameters.keys():
                if not cls.rhel6client1 and cli.parameters['OS'] == "RHEL6":
                    cls.rhel6client1 = cli
                elif not cls.rhel6client2 and cli.parameters['OS'] == "RHEL6":
                    cls.rhel6client2 = cli
        if not cls.rhel6client1:
            raise nose.exc.SkipTest("No RHEL6 clients (two required), skipping test")
        if not cls.rhel6client2:
            raise nose.exc.SkipTest("Only one RHEL6 client (two required), skipping test")


class RHUI_has_RHEL6_CLI(object):
    """ Has RHEL6 CLIs """
    @classmethod
    def check(cls, rs):
        """ Check """
        if (not "CLI" in rs.Instances.keys()) or len(rs.Instances["CLI"]) < 1:
            raise nose.exc.SkipTest("can't test without having at least one CLI!")
        cls.rhel6client = None
        for cli in rs.Instances["CLI"]:
            if 'OS' in cli.parameters.keys():
                if cli.parameters['OS'] == "RHEL6":
                    cls.rhel6client = cli
                    break
        if not cls.rhel6client:
            raise nose.exc.SkipTest("No RHEL6 clients, skipping test")


class RHUI_has_RHEL7_CLI(object):
    """ Has RHEL7 CLIs """
    @classmethod
    def check(cls, rs):
        """ Check """
        if (not "CLI" in rs.Instances.keys()) or len(rs.Instances["CLI"]) < 1:
            raise nose.exc.SkipTest("can't test without having at least one CLI!")
        cls.rhel7client = None
        for cli in rs.Instances["CLI"]:
            if 'OS' in cli.parameters.keys():
                if cli.parameters['OS'] == "RHEL7":
                    cls.rhel7client = cli
                    break
        if not cls.rhel7client:
            raise nose.exc.SkipTest("No RHEL7 clients, skipping test")


class RHUI_has_RHEL5_and_RHEL6_CLIs(object):
    """ Has two RHEL5 and RHEL6 CLIs """
    @classmethod
    def check(cls, rs):
        """ Check """
        if (not "CLI" in rs.Instances.keys()) or len(rs.Instances["CLI"]) < 2:
            raise nose.exc.SkipTest("can't test without having at least two CLIs!")
        cls.rhel5client = None
        cls.rhel6client = None
        for cli in rs.Instances["CLI"]:
            if 'OS' in cli.parameters.keys():
                if not cls.rhel6client and cli.parameters['OS'] == "RHEL6":
                    cls.rhel6client = cli
                elif not cls.rhel5client and cli.parameters['OS'] == "RHEL5":
                    cls.rhel5client = cli
        if not cls.rhel6client:
            raise nose.exc.SkipTest("No RHEL6 clients, skipping test")
        if not cls.rhel5client:
            raise nose.exc.SkipTest("No RHEL5 clients, skipping test")


class RHUI_has_PROXY(object):
    """ Has proxy """
    @classmethod
    def check(cls, rs):
        """ Check """
        if (not "PROXY" in rs.Instances.keys()) or len(rs.Instances["PROXY"]) < 1:
            raise nose.exc.SkipTest("can't test without proxy!")
