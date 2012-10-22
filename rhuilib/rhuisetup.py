import logging

from rhuilib.connection import Connection


class RHUIsetup:
    def __init__(self):
        self.RHUA = None
        self.CDS = []
        self.CLI = []

    def setRHUA(self, hostname, username="root", key_filename=None):
        logging.debug("Adding RHUA with hostname " + hostname)
        self.RHUA = Connection(hostname, username, key_filename)

    def addCDS(self, hostname, username="root", key_filename=None):
        logging.debug("Adding CDS with hostname " + hostname)
        self.CDS.append(Connection(hostname, username, key_filename))

    def addCLI(self, hostname, username="root", key_filename=None):
        logging.debug("Adding CLI with hostname " + hostname)
        self.CLI.append(Connection(hostname, username, key_filename))

    def setup_from_rolesfile(self, rolesfile="/etc/testing_roles"):
        fd = open(rolesfile, 'r')
        for line in fd.readlines():
            [Role, Hostname, PublicIP, PrivateIP] = line.split('\t')
            if Role.upper() == "RHUA":
                self.setRHUA(Hostname)
            elif Role.upper() == "CDS":
                self.addCDS(Hostname)
            elif Role.upper() == "CLI":
                self.addCLI(Hostname)
        fd.close()