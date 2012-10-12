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
    def getCaPassword(self):
         tf = tempfile.NamedTemporaryFile(delete=False)
         tf.close()
         self.sftp.get("/etc/rhui/pem/ca.pwd",tf.name)
         fd = open(tf.name,'r')
         password = fd.read()
         if password[-1:]=='\n':
             password = password[:-1]
         return password


class CDS(Instance):
    pass


class CLI(Instance):
    pass


class RHUIsetup():
    def __init__(self):
        self.RHUA = None
        self.CDS = []
        self.CLI = []
    
    def setRHUA(self, hostname, username="root", key_filename=None):
        self.RHUA = RHUA(hostname, username, key_filename)
    
    def addCDS(self, hostname, username="root", key_filename=None):
        self.CDS.append(CDS(hostname, username, key_filename))

    def addCLI(self, hostname, username="root", key_filename=None):
        self.CLI.append(CDS(hostname, username, key_filename))

    def setupFromRolesfile(self, rolesfile="/etc/testing_roles"):
        fd = open(rolesfile,'r')
        for line in fd.readlines():
            [Role, Hostname, PublicIP, PrivateIP] = line.split('\t')
            if Role.upper()=="RHUA":
                self.setRHUA(Hostname)
            elif Role.upper=="CDS":
                self.addCDS(Hostname)
            elif Role.upper=="CLI":
                self.addCLI(Hostname)
        fd.close()


if __name__=="__main__":
    logging.error("What do you think I am? A program?")
    sys.exit(1)
    
