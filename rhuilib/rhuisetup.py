import logging
import yaml

from rhuilib.connection import Connection


class RHUIsetup:
    '''
    Stateful object to represent whole RHUI setup (all RHUA, CDS and CLI instances)
    '''
    def __init__(self):
        self.RHUA = None
        self.CDS = []
        self.CLI = []
        self.config = {}

    def __del__(self):
        '''
        Close all connections
        '''
        for instance in self.CDS + self.CLI + [self.RHUA]:
            instance.sftp.close()
            instance.cli.close()

    def setRHUA(self, hostname, username="root", key_filename=None):
        '''
        set RHUA instance
        '''
        logging.debug("Adding RHUA with hostname " + hostname)
        self.RHUA = Connection(hostname, username, key_filename)

    def addCDS(self, hostname, username="root", key_filename=None):
        '''
        add CDS instance
        '''
        logging.debug("Adding CDS with hostname " + hostname)
        self.CDS.append(Connection(hostname, username, key_filename))

    def addCLI(self, hostname, username="root", key_filename=None):
        '''
        add CLI instance
        '''
        logging.debug("Adding CLI with hostname " + hostname)
        self.CLI.append(Connection(hostname, username, key_filename))

    def setup_from_yamlfile(self, yamlfile="/etc/rhui-testing.yaml"):
        '''
        Setup from yaml config
        '''
        logging.debug("Loading config from " + yamlfile)
        fd = open(yamlfile, 'r')
        yamlconfig = yaml.load(fd)
        for instance in yamlconfig['Instances']:
            if instance['role'].upper() == "RHUA":
                self.setRHUA(instance['hostname'])
            elif instance['role'].upper() == "CDS":
                self.addCDS(instance['hostname'])
            elif instance['role'].upper() == "CLI":
                self.addCLI(instance['hostname'])
        if 'Config' in yamlconfig.keys():
            logging.debug("Config found: " + yamlconfig['Config'])
            self.config = yamlconfig['Config'].copy()
        fd.close()
