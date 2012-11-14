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
        for connection in self.CDS + self.CLI + [self.RHUA]:
            connection.sftp.close()
            connection.cli.close()

    def reconnect_all(self):
        '''
        Re-establish connection to all instances
        '''
        for connection in self.CDS + self.CLI + [self.RHUA]:
            connection.reconnect()

    def setRHUA(self, instance, username="root", key_filename=None):
        '''
        set RHUA instance
        '''
        logging.debug("Adding RHUA with private_hostname " + instance['private_hostname'] + ", public_hostname " + instance['public_hostname'])
        self.RHUA = Connection(instance, username, key_filename)

    def addCDS(self, instance, username="root", key_filename=None):
        '''
        add CDS instance
        '''
        logging.debug("Adding CDS with private_hostname " + instance['private_hostname'] + ", public_hostname " + instance['public_hostname'])
        self.CDS.append(Connection(instance, username, key_filename))

    def addCLI(self, instance, username="root", key_filename=None):
        '''
        add CLI instance
        '''
        logging.debug("Adding CLI with private_hostname " + instance['private_hostname'] + ", public_hostname " + instance['public_hostname'])
        self.CLI.append(Connection(instance, username, key_filename))

    def setup_from_yamlfile(self, yamlfile="/etc/rhui-testing.yaml"):
        '''
        Setup from yaml config
        '''
        logging.debug("Loading config from " + yamlfile)
        fd = open(yamlfile, 'r')
        yamlconfig = yaml.load(fd)
        for instance in yamlconfig['Instances']:
            if instance['role'].upper() == "RHUA":
                self.setRHUA(instance)
            elif instance['role'].upper() == "CDS":
                self.addCDS(instance)
            elif instance['role'].upper() == "CLI":
                self.addCLI(instance)
        if 'Config' in yamlconfig.keys():
            logging.debug("Config found: " + str(yamlconfig['Config']))
            self.config = yamlconfig['Config'].copy()
        fd.close()
