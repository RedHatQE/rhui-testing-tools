import paramiko
import re
import time
import logging
import socket
import sys
import tempfile
import random
import string


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
                logging.debug("RCV: " + recv_part)
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
        return self.expect_list([(re.compile(".*" + strexp + ".*", re.DOTALL), True)], timeout)

    def match(self, regexp, group=1, timeout=5):
        result = ""
        count = 0
        while count < timeout:
            try:
                recv_part = self.channel.recv(16384)
                logging.debug("RCV: " + recv_part)
                result += recv_part
            except socket.timeout:
                pass

            match = regexp.match(result)
            if match and match.group(group):
                logging.debug("matched: " + match.group(group))
                return match.group(group)
            time.sleep(1)
            count += 1
        raise ExpectFailed()

    def enter(self, command):
        return self.channel.send(command + "\n")

    def generateGpgKey(self, keytype="DSA", keysize="1024", keyvalid="0", realname="Key Owner", email="kowner@example.com", comment="comment"):
        ''' It takes too long to wait for this operation to complete... use pre-created keys instead '''
        self.enter("cat > /tmp/gpgkey << EOF")
        self.enter("Key-Type: " + keytype)
        self.enter("Key-Length: " + keysize)
        self.enter("Subkey-Type: ELG-E")
        self.enter("Subkey-Length: " + keysize)
        self.enter("Name-Real: " + realname)
        self.enter("Name-Comment: " + comment)
        self.enter("Name-Email: " + email)
        self.enter("Expire-Date: " + keyvalid)
        self.enter("%commit")
        self.enter("%echo done")
        self.enter("EOF")
        self.expect("root@")

        self.enter("gpg --gen-key --no-random-seed-file --batch /tmp/gpgkey")
        for i in range(1, 200):
            self.enter(''.join(random.choice(string.ascii_lowercase) for x in range(200)))
            time.sleep(1)
            try:
                self.expect("gpg: done")
                break
            except ExpectFailed:
                continue

    def removeConfigurationRpm(self):
        self.enter("")
        self.expect("root@")
        self.enter("yum remove `rpm -qf --queryformat %{NAME} /etc/yum/pluginconf.d/rhui-lb.conf`")
        if self.expect_list([(re.compile(".*Is this ok \[y/N\]:.*", re.DOTALL), True),
                             (re.compile(".*Error: Need to pass a list of pkgs to remove.*root@.*", re.DOTALL), False)],35) == True:
            self.enter("y")
            self.expect("Complete.*root@",30)

    def installRpmFromMaster(self, rpmpath):
        self.enter("mkdir -p `dirname " + rpmpath + "`")
        self.expect("root@")
        self.sftp.put(rpmpath,rpmpath)
        self.enter("yum install "+rpmpath)
        self.expect("Is this ok \[y/N\]:")
        self.enter("y")
        self.expect("Complete.*root@",30)


class RHUA(Instance):
    '''
    Class to represent RHUA instance
    '''
    def getCaPassword(self):
        tf = tempfile.NamedTemporaryFile(delete=False)
        tf.close()
        self.sftp.get("/etc/rhui/pem/ca.pwd", tf.name)
        fd = open(tf.name, 'r')
        password = fd.read()
        if password[-1:] == '\n':
            password = password[:-1]
        return password

    def rhui_select(self, value_list):
        for value in value_list:
            match = self.match(re.compile(".*-\s+([0-9]+)\s+:.*\s+" + value + "\s*\n.*for more commands:.*", re.DOTALL))
            self.enter(match)
            match = self.match(re.compile(".*x\s+([0-9]+)\s+:.*\s+" + value + "\s*\n.*for more commands:.*", re.DOTALL))
            self.enter("l")
        self.enter("c")

    def rhui_select_one(self, value):
        match = self.match(re.compile(".*([0-9]+)\s+-\s+" + value + "\s*\n.*to abort:.*", re.DOTALL))
        self.enter(match)

    def rhui_quit(self):
        self.expect("rhui \(.*\) =>")
        self.enter("q")

    def rhui_proceed(self):
        self.expect("Proceed\? \(y/n\)")
        self.enter("y")

    def rhui_screen(self, screen):
        self.enter("rhui-manager")
        self.expect("rhui \(home\) =>")
        if screen in ["repo", "cds", "sync"]:
            key = screen[:1]
        elif screen == "client":
            key = "e"
        self.enter(key)
        self.expect("rhui \(" + screen + "\) =>")

    def initialRun(self, crt="/etc/rhui/pem/ca.crt", key="/etc/rhui/pem/ca.key", cert_pw=None, days="", username="admin", password="admin"):
        self.enter("rhui-manager")
        state = self.expect_list([(re.compile(".*Full path to the new signing CA certificate:.*", re.DOTALL), 1), (re.compile(".*rhui \(home\) =>.*", re.DOTALL), 2)])
        if state == 1:
            self.enter(crt)
            self.expect("Full path to the new signing CA certificate private key:")
            self.enter(key)
            self.expect("regenerated using rhui-manager.*:")
            self.enter(days)
            self.expect("Enter pass phrase for.*:")
            if cert_pw:
                self.enter(cert_pw)
            else:
                self.enter(self.getCaPassword())
            self.expect("RHUI Username:")
            self.enter(username)
            self.expect("RHUI Password:")
            self.enter(password)
            self.expect("rhui \(home\) =>")
        else:
            # initial step was already performed by someone
            self.enter("q")

    def addCds(self, clustername, cdsname, hostname="", displayname=""):
        self.rhui_screen("cds")
        self.enter("a")
        self.expect("Hostname of the CDS to register:")
        self.enter(cdsname)
        self.expect("Client hostname \(hostname clients will use to connect to the CDS\).*:")
        self.enter(hostname)
        self.expect("Display name for the CDS.*:")
        self.enter(displayname)
        self.expect("Enter a CDS cluster name:")
        self.enter(clustername)
        self.rhui_proceed()
        self.rhui_quit()

    def deleteCds(self, clustername, cdslist):
        self.rhui_screen("cds")
        self.enter("d")
        self.rhui_select_one(clustername)
        self.rhui_select(cdslist)
        self.rhui_proceed()
        self.rhui_quit()

    def addCustomRepo(self, reponame, displayname="", path="", checksum_alg="1", entitlement="y", entitlement_path="", redhat_gpg="y", custom_gpg=None):
        self.rhui_screen("repo")
        self.enter("c")
        self.expect("Unique ID for the custom repository.*:")
        self.enter(reponame)
        self.expect("Display name for the custom repository.*:")
        self.enter(displayname)
        self.expect("Path at which the repository will be served.*:")
        self.enter(path)
        self.expect("Enter value.*:")
        self.enter(checksum_alg)
        self.expect("Should the repository require an entitlement certificate to access\? \(y/n\)")
        self.enter(entitlement)
        if entitlement == "y":
            self.expect("Path that should be used when granting an entitlement for this repository.*:")
            self.enter(entitlement_path)
        self.expect("packages are signed by a GPG key\? \(y/n\)")
        if redhat_gpg or custom_gpg:
            self.enter("y")
            self.expect("Will the repository be used to host any Red Hat GPG signed content\? \(y/n\)")
            self.enter(redhat_gpg)
            self.expect("Will the repository be used to host any custom GPG signed content\? \(y/n\)")
            if custom_gpg:
                self.enter("y")
                self.expect("Enter the absolute path to the public key of the GPG keypair:")
                self.enter(custom_gpg)
            else:
                self.enter("n")
        else:
            self.enter("n")
        self.rhui_proceed()
        self.expect("Successfully created repository.*rhui \(repo\) =>")
        self.enter("q")

    def deleteCustomRepo(self, repolist):
        self.rhui_screen("repo")
        self.enter("d")
        self.rhui_select(repolist)
        self.rhui_proceed()
        self.rhui_quit()

    def associateRepoCds(self, clustername, repolist):
        self.rhui_screen("cds")
        self.enter("s")
        self.rhui_select_one(clustername)
        self.rhui_select(repolist)
        self.rhui_proceed()
        self.rhui_quit()

    def uploadContent(self, repolist, path):
        self.rhui_screen("repo")
        self.enter("u")
        self.rhui_select(repolist)
        self.expect("will be uploaded:")
        self.enter(path)
        self.rhui_proceed()
        self.rhui_quit()

    def syncCds(self, cdslist):
        self.rhui_screen("sync")
        self.enter("sc")
        self.rhui_select(cdslist)
        self.rhui_proceed()
        self.rhui_quit()

    def syncCluster(self, clusterlist):
        self.rhui_screen("sync")
        self.enter("sl")
        self.rhui_select(clusterlist)
        self.rhui_proceed()
        self.rhui_quit()

    def generateEntitlementCert(self, clustername, repolist, certname, dirname, validity_days="", cert_pw=None):
        self.rhui_screen("client")
        self.enter("e")
        self.rhui_select_one(clustername)
        self.rhui_select(repolist)
        self.expect("Name of the certificate.*contained with it:")
        self.enter(certname)
        self.expect("Local directory in which to save the generated certificate.*:")
        self.enter(dirname)
        self.expect("Number of days the certificate should be valid.*:")
        self.enter(validity_days)
        self.rhui_proceed()
        self.expect("Enter pass phrase for.*:")
        if cert_pw:
            self.enter(cert_pw)
        else:
            self.enter(self.getCaPassword())
        self.rhui_quit()

    def createConfigurationRpm(self, clustername, primary_cds, dirname, certpath, certkey, rpmname, rpmversion=""):
        self.rhui_screen("client")
        self.enter("c")
        self.expect("Full path to local directory.*:")
        self.enter(dirname)
        self.expect("Name of the RPM:")
        self.enter(rpmname)
        self.expect("Version of the configuration RPM.*:")
        self.enter(rpmversion)
        self.expect("Full path to the entitlement certificate.*:")
        self.enter(certpath)
        self.expect("Full path to the private key for the above entitlement certificate:")
        self.enter(certkey)
        self.rhui_select_one(clustername)
        self.rhui_select_one(primary_cds)
        self.rhui_quit()


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
        self.CLI.append(CLI(hostname, username, key_filename))

    def setupFromRolesfile(self, rolesfile="/etc/testing_roles"):
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


if __name__ == "__main__":
    logging.error("What do you think I am? A program?")
    sys.exit(1)
