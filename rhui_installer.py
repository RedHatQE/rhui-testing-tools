#! /usr/bin/python -tt

from paramiko import SSHClient, AutoAddPolicy
import argparse
import sys
import time
import tempfile
import logging
import os
import random
import string

class Instance(SSHClient):
    '''
    Instance to run commands via ssh
    '''
    def __init__(self, hostname, private_ip, public_ip):
        SSHClient.__init__(self)
        self.hostname = hostname
        self.public_ip = public_ip
        self.private_ip = private_ip
        self.load_system_host_keys()
        self.set_missing_host_key_policy(AutoAddPolicy())
        self.connect(hostname=hostname, username="root")
        self.sftp = self.open_sftp()

    def __repr__(self):
        return (self.__class__.__name__+":"+self.hostname+":"+self.public_ip+":"+self.private_ip)

    def run_sync(self, command, required=False):
        stdin, stdout, stderr = self.exec_command(command)
        output = stdout.read()
        logging.debug("Executing: '"+command+"' on "+self.hostname)
        status = stdout.channel.recv_exit_status()
        logging.debug("STDOUT: "+output)
        logging.debug("STDERR: "+stderr.read())
        logging.debug("STATUS: "+str(status))
        if required and status!=0:
            logging.debug("Command execution failed, exiting")
            sys.exit(1)
        stdin.close()
        stdout.close()
        stderr.close()
        return output

class RHUI_Instance(Instance):
    '''
    Class to represent RHUI instance (RHUA or CDS)
    '''
    def __init__(self, hostname, private_ip, public_ip, iso):
        Instance.__init__(self, hostname, private_ip, public_ip)
        self.iso=iso
        self.version="1.0"

    def setup(self):
        logging.info("Setting up RHUI instance "+self.hostname)
        remote_iso="/root/"+os.path.basename(self.iso)
        logging.debug("Will mount " + self.iso + " to /mnt")
        self.run_sync("umount /mnt")
        self.sftp.put(self.iso, remote_iso)
        self.run_sync("mount -o loop " + remote_iso + " /mnt", True)
        # Setting up iptables
        logging.debug("Will allow tcp connection to ports 5674, 443")
        self.run_sync("iptables -I INPUT -p tcp --destination-port 443 -j ACCEPT", True)
        self.run_sync("iptables -I INPUT -p tcp --destination-port 5674 -j ACCEPT", True)
        self.run_sync("service iptables save", True)

    def set_confrpm_name(self, name):
        if name[-1:] == "\n":
            name = name[:-1]
        logging.debug("Setting up conf rpm name to " + name + " for "+self.hostname)
        self.confrpm = name


class RHUA(RHUI_Instance):
    '''
    Class to represent RHUA instance
    '''
    def setup(self, cds_list):
        logging.info("Setting up RHUA instance "+self.hostname)
        answersfile = tempfile.NamedTemporaryFile(delete=False)
        capassword = ''.join(random.choice(string.ascii_lowercase) for x in range(10))
        RHUI_Instance.setup(self)
        logging.debug("Running /mnt/install_RHUA.sh")
        self.run_sync("cd /mnt && ./install_RHUA.sh", True)
        self.run_sync("mkdir /etc/rhui/pem ||:", True)
        self.run_sync("mkdir /etc/rhui/confrpm ||:", True)
        # Creating CA
        logging.debug("Creating CA")
        self.run_sync("echo " + capassword + " > /etc/rhui/pem/ca.pwd", True)
        self.run_sync("echo 10 > /etc/rhui/pem/ca.srl", True)
        self.run_sync("openssl req  -new -x509 -extensions v3_ca -keyout /etc/rhui/pem/ca.key -subj \"/C=US/ST=NC/L=Raleigh/CN="+self.hostname+" CA\" -out /etc/rhui/pem/ca.crt -days 365 -passout \"pass:" + capassword + "\"", True)
        # Creating answers file
        logging.debug("Creating answers file "+answersfile.name)
        answersfile.write("[general]\n")
        answersfile.write("version: " + self.version + "\n")
        answersfile.write("dest_dir: /etc/rhui/confrpm\n")
        answersfile.write("qpid_ca: /etc/rhui/qpid/ca.crt\n")
        answersfile.write("qpid_client: /etc/rhui/qpid/client.crt\n")
        answersfile.write("qpid_nss_db: /etc/rhui/qpid/nss\n")
        for server in [self]+cds_list:
            # Creating server certs for RHUA and CDSs
            logging.debug("Creating cert for "+server.hostname)
            self.run_sync("openssl genrsa -out /etc/rhui/pem/" + server.hostname + ".key 2048", True)
            self.run_sync("openssl req -new -key /etc/rhui/pem/" + server.hostname + ".key -subj \"/C=US/ST=NC/L=Raleigh/CN=" + server.hostname + "\" -out /etc/rhui/pem/" + server.hostname + ".csr", True)
            self.run_sync("openssl x509 -req -days 365 -CA /etc/rhui/pem/ca.crt -CAkey /etc/rhui/pem/ca.key -passin \"pass:" + capassword + "\" -in /etc/rhui/pem/" + server.hostname + ".csr -out /etc/rhui/pem/" + server.hostname + ".crt", True)
            logging.debug("Adding " + server.hostname + " to answers")
            if server.__class__==RHUA:
                answersfile.write("[rhua]\n")
            else:
                answersfile.write("[" + server.hostname + "]\n")
            answersfile.write("hostname: " + server.hostname + "\n")
            answersfile.write("rpm_name: " + server.hostname + "\n")
            answersfile.write("ssl_cert: /etc/rhui/pem/" + server.hostname + ".crt\n")
            answersfile.write("ssl_key: /etc/rhui/pem/" + server.hostname + ".key\n")
            answersfile.write("ca_cert: /etc/rhui/pem/ca.crt\n")
        answersfile.close()
        # Creating configuration RPMs
        logging.debug("Putting answers to /etc/rhui/answers on " + server.hostname)
        self.sftp.put(answersfile.name, "/etc/rhui/answers")
        logging.debug("Running rhui-installer")
        self.run_sync("rhui-installer /etc/rhui/answers", True)
        for server in [self]+cds_list:
            #Setting conf RPM names
            rpmname = self.run_sync("ls -1 /etc/rhui/confrpm/" + server.hostname + "-" + self.version + "-*.rpm | head -1")
            server.set_confrpm_name(rpmname)
        # Installing RHUA
        logging.debug("Installing RHUI conf rpm")
        self.run_sync("rpm -e " + self.hostname)
        self.run_sync("rpm -i " + self.confrpm, True)
        logging.info("RHUA " + self.hostname + " setup finished")

class CDS(RHUI_Instance):
    '''
    Class to represent CDS instance
    '''
    def setup(self, rhua):
        logging.info("Setting up CDS instance "+self.hostname + " associated with RHUA "+rhua.hostname)
        RHUI_Instance.setup(self)
        self.run_sync("cd /mnt && ./install_CDS.sh", True)
        rpmfile = tempfile.NamedTemporaryFile(delete=False)
        rpmfile.close()
        logging.debug("will transfer " + self.confrpm + " from RHUA to " + rpmfile.name)
        rhua.sftp.get(self.confrpm,rpmfile.name)
        logging.debug("will transfer " + rpmfile.name + " to CDS " + rpmfile.name)
        self.sftp.put(rpmfile.name,rpmfile.name)
        logging.debug("will install " + rpmfile.name + " on CDS")
        self.run_sync("rpm -i " + rpmfile.name)
        logging.info("CDS " + self.hostname + " setup finished")

class CLI(Instance):
    '''
    Class to represent CLI instance
    '''
    def setup(self, rhua):
        pass

argparser = argparse.ArgumentParser(description='Create RHUI install')
argparser.add_argument('--debug', action='store_const', const=True,
                       default=False, help='debug mode')
argparser.add_argument('--iso', required=True,
                       help='use supplied ISO file')
argparser.add_argument('--rolesfile',
                       default="/etc/testing_roles", help='use supplied testing roles file')
args = argparser.parse_args()

ISONAME = args.iso

if args.debug:
    loglevel = logging.DEBUG
else:
    loglevel = logging.INFO

logging.basicConfig(filename='/var/log/rhui-installer.log', level=loglevel, format='%(asctime)s %(levelname)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

rhua = []
cds = []
cli = []
try:
    froles = open(args.rolesfile,"r")
    for line in froles.readlines():
        if line[-1:]=='\n':
            line=line[:-1]
        [role, hostname, public_ip, private_ip] = line.split("\t")
        role=role.upper()
        if role=="RHUA":
            instance = RHUA(hostname, public_ip, private_ip, args.iso)
            rhua.append(instance)
        elif role=="CDS":
            instance = CDS(hostname, public_ip, private_ip, args.iso)
            cds.append(instance)
        elif role=="CLI":
            instance = CLI(hostname, public_ip, private_ip)
            cli.append(instance)
        elif role=="MASTER":
            logging.debug("Skipping master node "+hostname)
            pass
        else:
            logging.info("host with unknown role "+role+" "+hostname+", skipping")
    froles.close()
except Exception, e:
    logging.error("Failed to parse rolesfile " + args.rolesfile +
                  " " + str(e.__class__) + ': ' + str(e))
    sys.exit(1)
logging.debug("RHUA: "+repr(rhua))
logging.debug("CDSs: "+repr(cds))
logging.debug("CLIs: "+repr(cli))

if len(rhua)>1:
    logging.error("Don't know how to install RHUI with two or more RHUAs, exiting")
    sys.exit(1)
elif len(rhua)==0:
    logging.error("Don't know how to install RHUI without RHUA, exiting")
    sys.exit(1)

if len(cds)==0:
    logging.info("No CDSs found, will do only RHUA setup")

if len(cli)==0:
    logging.info("No CLIs found")

rhua[0].setup(cds)
for cds_instance in cds:
    cds_instance.setup(rhua[0])

