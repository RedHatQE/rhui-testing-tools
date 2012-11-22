import logging
import yaml

from rhuilib.connection import Connection


class RHUIsetup:
    '''
    Stateful object to represent whole RHUI setup (all RHUA, CDS and CLI instances)
    '''
    def __init__(self):
        self.RHUA = []
        self.CDS = []
        self.CLI = []
        self.PROXY = []
        self.config = {}

    def __del__(self):
        '''
        Close all connections
        '''
        for connection in self.PROXY + self.CLI + self.CDS + self.RHUA:
            connection.sftp.close()
            connection.cli.close()

    def reconnect_all(self):
        '''
        Re-establish connection to all instances
        '''
        for connection in self.PROXY + self.CLI + self.CDS + self.RHUA:
            connection.reconnect()

    def addInstance(self, instances_list, role, instance, username="root", key_filename=None):
        logging.debug("Adding " + role + " with private_hostname " + instance['private_hostname'] + ", public_hostname " + instance['public_hostname'])
        instances_list.append(Connection(instance, username, key_filename))

    def setup_from_yamlfile(self, yamlfile="/etc/rhui-testing.yaml"):
        '''
        Setup from yaml config
        '''
        logging.debug("Loading config from " + yamlfile)
        fd = open(yamlfile, 'r')
        yamlconfig = yaml.load(fd)
        for instance in yamlconfig['Instances']:
            if instance['role'].upper() == "RHUA":
                self.addInstance(self.RHUA, "RHUA", instance)
            elif instance['role'].upper() == "CDS":
                self.addInstance(self.CDS, "CDS", instance)
            elif instance['role'].upper() == "CLI":
                self.addInstance(self.CLI, "CLI", instance)
            elif instance['role'].upper() == "PROXY":
                self.addInstance(self.PROXY, "PROXY", instance)
        if 'Config' in yamlconfig.keys():
            logging.debug("Config found: " + str(yamlconfig['Config']))
            self.config = yamlconfig['Config'].copy()
        fd.close()
