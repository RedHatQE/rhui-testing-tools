""" Utility functions """


import os
import tempfile
import time
import random
import string

from stitches.expect import Expect, ExpectFailed


class Util(object):
    '''
    Utility functions for instances
    '''
    @staticmethod
    def uncolorify(instr):
        """ Remove colorification """
        res = instr.replace("\x1b", "")
        res = res.replace("[91m", "")
        res = res.replace("[92m", "")
        res = res.replace("[93m", "")
        res = res.replace("[0m", "")
        return res

    @staticmethod
    def generate_gpg_key(connection, keytype="DSA", keysize="1024", keyvalid="0", realname="Key Owner", email="kowner@example.com", comment="comment"):
        '''
        Generate GPG keypair

        WARNING!!!
        It takes too long to wait for this operation to complete... use pre-created keys instead!
        '''
        Expect.enter(connection, "cat > /tmp/gpgkey << EOF")
        Expect.enter(connection, "Key-Type: " + keytype)
        Expect.enter(connection, "Key-Length: " + keysize)
        Expect.enter(connection, "Subkey-Type: ELG-E")
        Expect.enter(connection, "Subkey-Length: " + keysize)
        Expect.enter(connection, "Name-Real: " + realname)
        Expect.enter(connection, "Name-Comment: " + comment)
        Expect.enter(connection, "Name-Email: " + email)
        Expect.enter(connection, "Expire-Date: " + keyvalid)
        Expect.enter(connection, "%commit")
        Expect.enter(connection, "%echo done")
        Expect.enter(connection, "EOF")
        Expect.expect(connection, "root@")

        Expect.enter(connection, "gpg --gen-key --no-random-seed-file --batch /tmp/gpgkey")
        for _ in xrange(1, 200):
            Expect.enter(connection, ''.join(random.choice(string.ascii_lowercase) for x in range(200)))
            time.sleep(1)
            try:
                Expect.expect(connection, "gpg: done")
                break
            except ExpectFailed:
                continue

    @staticmethod
    def remove_conf_rpm(connection):
        '''
        Remove RHUI configuration rpm from instance (which owns /etc/yum/pluginconf.d/rhui-lb.conf file)
        '''
        Expect.enter(connection, "")
        Expect.expect(connection, "root@")
        Expect.enter(connection, "([ ! -f /etc/yum/pluginconf.d/rhui-lb.conf ] && echo SUCCESS ) || (rpm -e `rpm -qf --queryformat %{NAME} /etc/yum/pluginconf.d/rhui-lb.conf` && echo SUCCESS)")
        Expect.expect(connection, "[^ ]SUCCESS.*root@", 60)

    @staticmethod
    def install_rpm_from_rhua(rhua_connection, connection, rpmpath):
        '''
        Transfer RPM package from RHUA host to the instance and install it
        @param rpmpath: path to RPM package on RHUA node
        '''
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.close()
        rhua_connection.sftp.get(rpmpath, tfile.name)
        connection.sftp.put(tfile.name, tfile.name + ".rpm")
        os.unlink(tfile.name)
        Expect.ping_pong(connection, "rpm -i " + tfile.name + ".rpm" + " && echo SUCCESS", "[^ ]SUCCESS", 60)

    @staticmethod
    def get_ca_password(connection, pwdfile="/etc/rhui/pem/ca.pwd"):
        '''
        Read CA password from file
        @param pwdfile: file with the password (defaults to /etc/rhui/pem/ca.pwd)
        '''
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.close()
        connection.sftp.get(pwdfile, tfile.name)
        with open(tfile.name, 'r') as filed:
            password = filed.read()
        if password[-1:] == '\n':
            password = password[:-1]
        return password

    @staticmethod
    def get_rpm_details(rpmpath):
        '''
        Get (name-version-release, name) pair for local rpm file
        '''
        if rpmpath:
            rpmnvr = os.popen("basename " + rpmpath).read()[:-1]
            rpmname = os.popen("rpm -qp --queryformat '%{NAME}\n' " + rpmpath + " 2>/dev/null").read()[:-1]
            return (rpmnvr, rpmname)
        else:
            return (None, None)

    @staticmethod
    def wildcard(hostname):
        """ Hostname wildcard """
        hostname_particles = hostname.split('.')
        hostname_particles[0] = "*"
        return ".".join(hostname_particles)

    @staticmethod
    def generate_answers(rhuisetup, version="1.0", generate_certs=True, proxy_host=None, proxy_port="3128",
                         proxy_user="rhua", proxy_password=None, capassword=None, answersfile_name="/etc/rhui/answers"):
        ''' Generate answers file ant put it to RHUA node'''
        answersfile = tempfile.NamedTemporaryFile(delete=False)
        answersfile.write("[general]\n")
        answersfile.write("version: " + version + "\n")
        answersfile.write("dest_dir: /etc/rhui/confrpm\n")
        answersfile.write("qpid_ca: /etc/rhui/qpid/ca.crt\n")
        answersfile.write("qpid_client: /etc/rhui/qpid/client.crt\n")
        answersfile.write("qpid_nss_db: /etc/rhui/qpid/nss\n")
        instances = [rhuisetup.Instances["RHUA"][0]]
        instances.extend(rhuisetup.Instances["CDS"])
        cds_number = 1
        if not capassword:
            capassword = Util.get_ca_password(rhuisetup.Instances["RHUA"][0])
        for instance in instances:
            if instance.private_hostname:
                hostname = instance.private_hostname
            else:
                hostname = instance.public_hostname
            if generate_certs:
                Expect.expect_retval(rhuisetup.Instances["RHUA"][0], "openssl genrsa -out /etc/rhui/pem/" + hostname + ".key 2048", timeout=60)
                if instance == rhuisetup.Instances["RHUA"][0]:
                    Expect.expect_retval(rhuisetup.Instances["RHUA"][0], "openssl req -new -key /etc/rhui/pem/" + hostname + ".key -subj \"/C=US/ST=NC/L=Raleigh/CN=" + hostname + "\" -out /etc/rhui/pem/" + hostname + ".csr", timeout=60)
                else:
                    # Create domain wildcard certificates for CDSes
                    # otherwise CDS will not be accessible via public hostname
                    Expect.expect_retval(rhuisetup.Instances["RHUA"][0], "openssl req -new -key /etc/rhui/pem/" + hostname + ".key -subj \"/C=US/ST=NC/L=Raleigh/CN=" + Util.wildcard(hostname) + "\" -out /etc/rhui/pem/" + hostname + ".csr", timeout=60)
                Expect.expect_retval(rhuisetup.Instances["RHUA"][0], "openssl x509 -req -days 365 -CA /etc/rhui/pem/ca.crt -CAkey /etc/rhui/pem/ca.key -passin \"pass:" + capassword + "\" -in /etc/rhui/pem/" + hostname + ".csr -out /etc/rhui/pem/" + hostname + ".crt", timeout=60)
            if instance == rhuisetup.Instances["RHUA"][0]:
                answersfile.write("[rhua]\n")
                if proxy_host:
                    # Doing proxy setup
                    answersfile.write("proxy_server_host: " + proxy_host + "\n")
                    if proxy_port:
                        answersfile.write("proxy_server_port: " + proxy_port + "\n")
                    if proxy_user:
                        answersfile.write("proxy_server_username: " + proxy_user + "\n")
                    if proxy_password:
                        answersfile.write("proxy_server_password: " + proxy_password + "\n")
            else:
                answersfile.write("[cds-" + str(cds_number) + "]\n")
                cds_number += 1
            answersfile.write("hostname: " + hostname + "\n")
            answersfile.write("rpm_name: " + hostname + "\n")
            answersfile.write("ssl_cert: /etc/rhui/pem/" + hostname + ".crt\n")
            answersfile.write("ssl_key: /etc/rhui/pem/" + hostname + ".key\n")
            answersfile.write("ca_cert: /etc/rhui/pem/ca.crt\n")
        answersfile.close()
        rhuisetup.Instances["RHUA"][0].sftp.put(answersfile.name, answersfile_name)
