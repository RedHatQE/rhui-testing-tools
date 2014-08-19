#! /usr/bin/python -tt

""" RHUI installer script """

from paramiko import SSHClient, AutoAddPolicy
import argparse
import sys
import time
import tempfile
import logging
import os
import random
import string
import yaml
import subprocess
import threading

from stitches import structure

from rhuilib.s3 import download_from_s3
from rhuilib.util import Util


class UpdateThread(threading.Thread):
    '''
    Instance updater
    '''
    def __init__(self, connection):
        threading.Thread.__init__(self)
        self.connection = connection

    def run(self):
        self.connection.run_sync("yum -y update", True)


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
        if args.updateos:
            uthread = UpdateThread(self)
            uthread.start()
            uthread.name = "UpdateThread-%s" % hostname

    def __repr__(self):
        return (self.__class__.__name__ + ":" + self.hostname + ":" + self.public_ip + ":" + self.private_ip)

    def run_sync(self, command, required=False, timeout=3600):
        stdin, stdout, stderr = self.exec_command(command)
        output = stdout.read()
        logger.debug("Executing: '" + command + "' on " + self.hostname)
        t = 0
        while t < timeout:
            if stdout.channel.exit_status_ready():
                break
            t += 1
            time.sleep(1)
        if t == timeout:
            logger.error("Command " + command + " execution failed due to timeout %i" % timeout)
            sys.exit(1)
        status = stdout.channel.recv_exit_status()
        logger.debug("STDOUT: " + output)
        logger.debug("STDERR: " + stderr.read())
        logger.debug("STATUS: " + str(status))
        if required and status != 0:
            logger.error("Command " + command + " execution failed, exiting")
            sys.exit(1)
        stdin.close()
        stdout.close()
        stderr.close()
        return output


class StorageThread(threading.Thread):
    '''
    Storage creator
    '''
    def __init__(self, connection):
        threading.Thread.__init__(self)
        self.connection = connection

    def run(self):
        for device in self.connection.run_sync("ls -1 /dev/xvd*").strip().split('\n'):
            if device != "":
                # searching for the first unused block device
                if self.connection.run_sync("grep " + device + " /proc/mounts").strip() == "":
                    self.connection.ephemeral_device = device
                    logger.debug("Using " + device + " as additional storage")
                    self.connection.run_sync("mkfs.ext3 " + device, True)
                    break


class RHUI_Instance(Instance):
    '''
    Class to represent RHUI instance (RHUA or CDS)
    '''
    def __init__(self, hostname, private_ip, public_ip, iso):
        Instance.__init__(self, hostname, private_ip, public_ip)
        self.iso = iso
        self.version = "1.0"
        self.ephemeral_device = None
        if not args.nostorage:
            sthread = StorageThread(self)
            sthread.start()
            sthread.name = "StorageThread-%s" % hostname

    def setup(self):
        logger.info("Common RHUI instance setup for " + self.hostname)
        remote_iso = "/root/" + os.path.basename(self.iso)
        logger.debug("Will mount " + self.iso + " to /mnt")
        self.run_sync("umount /mnt")
        # hardening according to bug 892394
        logger.debug("setting umask 027 for init")
        # self.run_sync("echo 'umask 027' >> /etc/sysconfig/init", True)
        self.sftp.put(self.iso, remote_iso)
        self.run_sync("mount -o loop " + remote_iso + " /mnt", True)
        # Setting up iptables
        logger.debug("Will allow tcp connection to ports 5674, 443")
        self.run_sync("iptables -I INPUT -p tcp --destination-port 443 -j ACCEPT", True)
        self.run_sync("iptables -I INPUT -p tcp --destination-port 5674 -j ACCEPT", True)
        self.run_sync("service iptables save", True)
        # setting time
        self.run_sync("yum install -y ntp", True)
        self.run_sync("service ntpd start", True)
        self.run_sync("ntpd -gq ||:", True)
        self.run_sync("service ntpd restart", True)
        self.run_sync("chkconfig ntpd on", True)

    def set_confrpm_name(self, name):
        if name[-1:] == "\n":
            name = name[:-1]
        logger.debug("Setting up conf rpm name to " + name + " for " + self.hostname)
        self.confrpm = name

    def ephemeral_mount(self, mountpoint):
        if self.ephemeral_device:
            self.run_sync("mkdir " + mountpoint + " ||:", True)
            self.run_sync("chmod 755 " + mountpoint, True)
            self.run_sync("mount " + self.ephemeral_device + " " + mountpoint, True)
            self.run_sync("echo " + self.ephemeral_device + "\t" + mountpoint + "\text3\tdefaults\t0 0 >> /etc/fstab", True)

    def install_coverage(self, master_hostname):
        logger.debug("Will install python coverage")
        coverrpm = download_from_s3("python-coverage-")
        moncovrpm = download_from_s3("python-moncov-")
        if coverrpm != "" and moncovrpm != "":
            self.sftp.put("/root/" + coverrpm, "/root/" + coverrpm)
            self.run_sync("yum -y install /root/" + coverrpm, True)

            self.sftp.put("/root/" + moncovrpm, "/root/" + moncovrpm)
            self.run_sync("yum -y install /root/" + moncovrpm, True)

            self.run_sync("sed -i s,localhost,%s, /etc/coveragerc" % master_hostname, True)
            self.run_sync("sed -i s,localhost,%s, /etc/moncov.yaml" % master_hostname, True)
            logger.debug("Coverage installed")
        else:
            logger.debug("Could not find python-coverage or python-moncov in S3")


class RHUA(RHUI_Instance):
    '''
    Class to represent RHUA instance
    '''
    def __init__(self, hostname, private_ip, public_ip, iso):
        RHUI_Instance.__init__(self, hostname, private_ip, public_ip, iso)
        self.proxy_password = ''.join(random.choice(string.ascii_lowercase) for x in range(8))

    def setup(self, cds_list, proxy_list, master_hostname):
        logger.info("Setting up RHUA instance " + self.hostname)
        capassword = ''.join(random.choice(string.ascii_lowercase) for x in range(10))
        RHUI_Instance.setup(self)
        self.ephemeral_mount("/var/lib/pulp")
        logger.debug("Running /mnt/install_RHUA.sh")
        self.run_sync("cd /mnt && ./install_RHUA.sh", True)
        self.run_sync("chown apache.apache /var/lib/pulp", True)
        self.run_sync("mkdir /etc/rhui/pem ||:", True)
        self.run_sync("mkdir /etc/rhui/confrpm ||:", True)
        # Creating CA
        logger.debug("Creating CA")
        self.run_sync("echo " + capassword + " > /etc/rhui/pem/ca.pwd", True)
        self.run_sync("echo 10 > /etc/rhui/pem/ca.srl", True)
        self.run_sync("openssl req  -new -x509 -extensions v3_ca -keyout /etc/rhui/pem/ca.key -subj \"/C=US/ST=NC/L=Raleigh/CN=" + self.hostname + " CA\" -out /etc/rhui/pem/ca.crt -days 365 -passout \"pass:" + capassword + "\"", True)
        # Creating answers
        logger.debug("Creating answers file")
        proxy_host = None
        if proxy_list != []:
            proxy_host = proxy_list[0].hostname
        Util.generate_answers(RS, version="1.0", generate_certs=True, proxy_host=proxy_host, proxy_port="3128", proxy_user="rhua", proxy_password=self.proxy_password, capassword=capassword)

        logger.debug("Running rhui-installer")
        self.run_sync("rhui-installer /etc/rhui/answers", True)
        for server in [self] + cds_list:
            #Setting conf RPM names
            rpmname = self.run_sync("ls -1 /etc/rhui/confrpm/" + server.hostname + "-" + self.version + "-*.rpm | head -1")
            server.set_confrpm_name(rpmname)
        # Installing coverage
        if args.coverage:
            self.install_coverage(master_hostname)
        # Installing RHUA
        logger.debug("Installing RHUI conf rpm")
        self.run_sync("rpm -e " + self.hostname)
        self.run_sync("rpm -i " + self.confrpm, True)
        if proxy_list != []:
            # Preventing access without proxy
            self.run_sync("iptables -A OUTPUT -p tcp -d 127.0.0.1 --dport 443 -j ACCEPT", True)
            for server in [self] + cds_list:
                # Allowing to connect to all CDSes and RHUA itself
                self.run_sync("iptables -A OUTPUT -d " + server.public_ip + " -j ACCEPT", True)
                self.run_sync("iptables -A OUTPUT -d " + server.private_ip + " -j ACCEPT", True)
            self.run_sync("iptables -A OUTPUT -p tcp --dport 443 -j REJECT", True)
            self.run_sync("service iptables save", True)
        logger.info("RHUA " + self.hostname + " setup finished")


class CdsThread(threading.Thread):
    '''
    CDS installer thread
    '''
    def __init__(self, connection, rhua, master_hostname):
        threading.Thread.__init__(self)
        self.connection = connection
        self.rhua = rhua
        self.master_hostname = master_hostname

    def run(self):
        logger.info("Setting up CDS instance " + self.connection.hostname + " associated with RHUA " + self.rhua.hostname)
        RHUI_Instance.setup(self.connection)
        self.connection.ephemeral_mount("/var/lib/pulp-cds")
        self.connection.run_sync("echo 'umask 027' >> /etc/sysconfig/init", True)
        self.connection.run_sync("cd /mnt && ./install_CDS.sh", True)
        self.connection.run_sync("chown apache.apache /var/lib/pulp-cds", True)
        rpmfile = tempfile.NamedTemporaryFile(delete=False)
        rpmfile.close()
        logger.debug("will transfer " + self.connection.confrpm + " from RHUA to " + rpmfile.name)
        self.rhua.sftp.get(self.connection.confrpm, rpmfile.name)
        logger.debug("will transfer " + rpmfile.name + " to CDS " + rpmfile.name)
        self.connection.sftp.put(rpmfile.name, rpmfile.name)
        logger.debug("will install " + rpmfile.name + " on CDS")
        # Installing coverage
        if args.coverage:
            self.connection.run_sync("yum -y install /mnt/Packages/pymongo-* /mnt/Packages/python-bson-*")
            self.connection.install_coverage(self.master_hostname)
        self.connection.run_sync("rpm -i " + rpmfile.name)
        logger.info("CDS " + self.connection.hostname + " setup finished")


class CDS(RHUI_Instance):
    '''
    Class to represent CDS instance
    '''
    def setup(self, rhua, master_hostname):
        cthread = CdsThread(self, rhua, master_hostname)
        cthread.start()
        cthread.name = "CdsThread-%s" % hostname


class CLI(Instance):
    '''
    Class to represent CLI instance
    '''
    def setup(self):
        # setting time
        self.run_sync("yum install -y ntp", True)
        self.run_sync("service ntpd start", True)
        self.run_sync("ntpd -gq ||:", True)
        self.run_sync("service ntpd restart", True)
        self.run_sync("chkconfig ntpd on", True)


class PROXY(Instance):
    '''
    Class to represent PROXY instance
    '''
    def setup(self, rhua):
        logger.info("Setting up PROXY instance " + self.hostname + " for RHUA " + rhua.hostname)
        self.run_sync("yum -y install squid httpd-tools", True)
        self.run_sync("htpasswd -bc /etc/squid/passwd rhua " + rhua.proxy_password, True)
        self.run_sync("echo 'auth_param basic program /usr/lib64/squid/ncsa_auth /etc/squid/passwd' > /etc/squid/squid.conf.new", True)
        self.run_sync("echo 'acl auth proxy_auth REQUIRED' >> /etc/squid/squid.conf.new", True)
        self.run_sync("cat /etc/squid/squid.conf | sed 's,allow localnet,allow auth,' >> /etc/squid/squid.conf.new", True)
        self.run_sync("mv -f /etc/squid/squid.conf.new /etc/squid/squid.conf", True)
        self.run_sync("service squid start", True)
        self.run_sync("chkconfig squid on", True)
        self.run_sync("iptables -I INPUT -s " + rhua.hostname + " -p tcp --destination-port 3128 -j ACCEPT", True)
        self.run_sync("service iptables save", True)
        # setting time
        self.run_sync("yum install -y ntp", True)
        self.run_sync("service ntpd start", True)
        self.run_sync("ntpd -gq ||:", True)
        self.run_sync("service ntpd restart", True)
        self.run_sync("chkconfig ntpd on", True)


def wait_for_threads(name):
    try:
        # waiting for storage threads
        threads_exist = True
        while threads_exist:
            threads_exist = False
            for thread in threading.enumerate():
                if thread is not threading.currentThread() and thread.name.startswith(name):
                    threads_exist = True
                    thread.join(2)
    except KeyboardInterrupt:
        print "Got CTRL-C, exiting"
        for thread in threading.enumerate():
            if thread is not threading.currentThread() and thread.isAlive():
                try:
                    thread._Thread__stop()
                except:
                    print(str(thread.getName()) + ' could not be terminated')
        sys.exit(1)


argparser = argparse.ArgumentParser(description='Create RHUI install')
argparser.add_argument('--coverage', action='store_const', const=True,
                       default=False, help='install python-coverage to measure code coverage')
argparser.add_argument('--debug', action='store_const', const=True,
                       default=False, help='debug output to the console (in addition to /var/log/rhui-installer.log)')
argparser.add_argument('--iso', required=True,
                       help='use supplied ISO file')
argparser.add_argument('--nostorage', action='store_const', const=True,
                       default=False, help='do not mount ephemeral device (speed up setup process)')
argparser.add_argument('--updateos', action='store_const', const=True,
                       default=False, help='update OS before running RHUI install')
argparser.add_argument('--yamlfile',
                       default="/etc/rhui-testing.yaml", help='use specified YAML config file')
args = argparser.parse_args()

ISONAME = args.iso
YAMLFILE = args.yamlfile

if args.debug:
    loglevel = logging.DEBUG
else:
    loglevel = logging.INFO

logger = logging.getLogger('rhui_installer')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('/var/log/rhui-installer.log')
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(loglevel)
formatter = logging.Formatter(fmt='%(asctime)s %(levelname)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
ch.setFormatter(formatter)
fh.setFormatter(formatter)
plogger = logging.getLogger("paramiko")
plogger.setLevel(logging.DEBUG)
plogger.addHandler(fh)
logger.addHandler(ch)
logger.addHandler(fh)

RS = structure.Structure()
RS.setup_from_yamlfile(yamlfile=YAMLFILE)

rhua = []
cds = []
cli = []
proxy = []
master_hostname = "localhost"
try:
    fd = open(args.yamlfile, "r")
    yamlconfig = yaml.load(fd)
    for instance in yamlconfig['Instances']:
        if instance['private_hostname']:
            hostname = instance['private_hostname']
        else:
            hostname = instance['public_hostname']
        public_ip = instance['public_ip']
        private_ip = instance['private_ip']
        role = instance['role'].upper()

        if role == "RHUA":
            logger.info("Adding RHUA instance " + hostname)
            instance = RHUA(hostname, private_ip, public_ip, args.iso)
            rhua.append(instance)
        elif role == "CDS":
            logger.info("Adding CDS instance " + hostname)
            instance = CDS(hostname, private_ip, public_ip, args.iso)
            cds.append(instance)
        elif role == "CLI":
            logger.info("Adding CLI instance " + hostname)
            instance = CLI(hostname, private_ip, public_ip)
            cli.append(instance)
        elif role == "PROXY":
            logger.info("Adding PROXY instance " + hostname)
            instance = PROXY(hostname, private_ip, public_ip)
            proxy.append(instance)
        elif role == "MASTER":
            logger.debug("Skipping master node " + hostname)
            master_hostname = private_ip
        else:
            logger.info("host with unknown role " + role + " " + hostname + ", skipping")
    fd.close()
except Exception, e:
    logger.error("Failed to parse config file " + args.yamlfile +
                  " " + str(e.__class__) + ': ' + str(e))
    sys.exit(1)
logger.debug("RHUA: " + repr(rhua))
logger.debug("CDSs: " + repr(cds))
logger.debug("CLIs: " + repr(cli))
logger.debug("PROXY: " + repr(proxy))

if len(rhua) > 1:
    logger.error("Don't know how to install RHUI with two or more RHUAs, exiting")
    sys.exit(1)
elif len(rhua) == 0:
    logger.error("Don't know how to install RHUI without RHUA, exiting")
    sys.exit(1)

if len(cds) == 0:
    logger.info("No CDSs found, will do only RHUA setup")

if len(cli) == 0:
    logger.info("No CLIs found")

if len(proxy) == 0:
    logger.info("No PROXY found, will do standard setup")

if args.coverage:
    subprocess.check_output(["yum", "-y", "install", "mongodb-server"])
    subprocess.check_output(["sed", "-i", "s,bind_ip = .*$,bind_ip = 0.0.0.0,", "/etc/mongodb.conf"])
    subprocess.check_output(["mkdir", "/var/lib/mongodb/journal"])
    subprocess.check_output(["chown", "mongodb.mongodb", "/var/lib/mongodb/journal"])
    for i in range(3):
        # Nasty hack to precreate mongo journals
        subprocess.check_output(["dd", "if=/dev/zero", "of=/var/lib/mongodb/journal/prealloc.%s" % i, "bs=1M", "count=1K"])
        subprocess.check_output(["chmod", "600", "/var/lib/mongodb/journal/prealloc.%s" % i])
        subprocess.check_output(["chown", "mongodb.mongodb", "/var/lib/mongodb/journal/prealloc.%s" % i])
    subprocess.check_output(["systemctl", "start", "mongod.service"])
    subprocess.check_output(["iptables", "-I", "INPUT", "-p", "tcp", "--destination-port", "27017", "-j", "ACCEPT"])
    subprocess.check_output(["/usr/libexec/iptables/iptables.init", "save"])

for proxy_instance in proxy:
    proxy_instance.setup(rhua[0])

wait_for_threads("UpdateThread")

wait_for_threads("StorageThread")

rhua[0].setup(cds, proxy, master_hostname)

for cds_instance in cds:
    cds_instance.setup(rhua[0], master_hostname)

for cli_instance in cli:
    cli_instance.setup()

wait_for_threads("CdsThread")
