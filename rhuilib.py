import paramiko
import re
import time
import logging
import socket
import sys
import tempfile

class ExpectFailed(Exception):
    pass

class Instance():
    def __init__(self, hostname, username="root", key_filename=None):
        self.hostname = hostname
        self.username = username
        self.key_filename = key_filename
        self.cli = paramiko.SSHClient()
        self.cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.cli.connect(hostname=hostname, username=username, key_filename=key_filename)
        self.channel = self.cli.invoke_shell()
        self.sftp = self.cli.open_sftp()
        self.channel.setblocking(0)

    def expect_list(self, regexp_list, timeout=5):
        result = ""
        count = 0
        while count < timeout:
            try:
                recv_part = self.channel.recv(16384)
                logging.debug("RCV: "+recv_part)
                result += recv_part
            except socket.timeout:
                pass

            for (regexp, retvalue) in regexp_list:
                if re.match(regexp, result):
                    return retvalue
            time.sleep(1)
            count += 1
        raise ExpectFailed()

    def expect(self, strexp, timeout=5):
        return self.expect_list([(re.compile(".*" + strexp + ".*",re.DOTALL),True)])
    
    def enter(self, command):
        return self.channel.send(command+"\n")

class RHUA(Instance):
    '''
    Class to represent RHUA instance
    '''
    def getCaPassword(self):
         tf = tempfile.NamedTemporaryFile(delete=False)
         tf.close()
         self.sftp.get("/etc/rhui/pem/ca.pwd",tf.name)
         fd = open(tf.name,'r')
         password = fd.read()
         if password[-1:]=='\n':
             password = password[:-1]
         return password

    def initialRun(self, crt="/etc/rhui/pem/ca.crt", key="/etc/rhui/pem/ca.key", days="", username="admin", password="admin"):
        self.enter("rhui-manager")
        state = self.expect_list([(re.compile(".*Full path to the new signing CA certificate:.*",re.DOTALL),1), (re.compile(".*rhui \(home\) =>.*",re.DOTALL),2)])
        if state == 1:
            self.enter(crt)
            self.expect("Full path to the new signing CA certificate private key:")
            self.enter(key)
            self.expect("regenerated using rhui-manager.*:")
            self.enter(days)
            self.expect("Enter pass phrase for.*:")
            self.enter(self.getCaPassword())
            self.expect("RHUI Username:")
            self.enter(username)
            self.expect("RHUI Password:")
            self.enter(password)
            self.expect("rhui \(home\) =>")
        else:
            # initial step was already performed by someone
            self.enter("q")

    def addCds(self, cluster, cdsname, hostname="", displayname=""):
        self.enter("rhui-manager")
        self.expect("rhui \(home\) =>")
        self.enter("c")
        self.expect("rhui \(cds\) =>")
        self.enter("a")
        self.expect("Hostname of the CDS to register:")
        self.enter(cdsname)
        self.expect("Client hostname \(hostname clients will use to connect to the CDS\).*:")
        self.enter(hostname)
        self.expect("Display name for the CDS.*:")
        self.enter(displayname)
        self.expect("Enter a CDS cluster name:")
        self.enter(cluster)
        self.expect("Proceed\? \(y/n\)")
        self.enter("y")
        self.expect("rhui \(cds\) =>")
        self.enter("q")


class CDS(Instance):
    '''
    Class to represent CDS instance
    '''
    pass


class CLI(Instance):
    '''
    Class to represent CLI instance
    '''
    pass


class RHUIsetup():
    def __init__(self):
        self.RHUA = None
        self.CDS = []
        self.CLI = []
    
    def setRHUA(self, hostname, username="root", key_filename=None):
        logging.debug("Adding RHUA with hostname " + hostname)
        self.RHUA = RHUA(hostname, username, key_filename)
    
    def addCDS(self, hostname, username="root", key_filename=None):
        logging.debug("Adding CDS with hostname " + hostname)
        self.CDS.append(CDS(hostname, username, key_filename))

    def addCLI(self, hostname, username="root", key_filename=None):
        logging.debug("Adding CLI with hostname " + hostname)
        self.CLI.append(CDS(hostname, username, key_filename))

    def setupFromRolesfile(self, rolesfile="/etc/testing_roles"):
        fd = open(rolesfile,'r')
        for line in fd.readlines():
            [Role, Hostname, PublicIP, PrivateIP] = line.split('\t')
            if Role.upper()=="RHUA":
                self.setRHUA(Hostname)
            elif Role.upper()=="CDS":
                self.addCDS(Hostname)
            elif Role.upper()=="CLI":
                self.addCLI(Hostname)
        fd.close()


if __name__=="__main__":
    logging.error("What do you think I am? A program?")
    sys.exit(1)
    
