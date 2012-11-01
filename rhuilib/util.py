import os
import tempfile
import time

from rhuilib.expect import *


class Util:
    '''
    Utility functions for instances
    '''
    @staticmethod
    def uncolorify(instr):
        res = instr.replace("\x1b", "")
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
        for i in range(1, 200):
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
    def install_rpm_from_master(connection, rpmpath):
        '''
        Transfer RPM package to instance and install it
        @param rpmpath: path to RPM package on Master node
        '''
        Expect.enter(connection, "mkdir -p `dirname " + rpmpath + "`")
        Expect.expect(connection, "root@")
        connection.sftp.put(rpmpath, rpmpath)
        Expect.enter(connection, "yum install " + rpmpath + " && echo 'NO ERRORS'")
        Expect.expect(connection, "Is this ok \[y/N\]:", 30)
        Expect.enter(connection, "y")
        # Check the result to address https://bugzilla.redhat.com/show_bug.cgi?id=617014
        Expect.expect(connection, "NO ERRORS.*root@", 60)

    @staticmethod
    def get_ca_password(connection, pwdfile="/etc/rhui/pem/ca.pwd"):
        '''
        Read CA password from file
        @param pwdfile: file with the password (defaults to /etc/rhui/pem/ca.pwd)
        '''
        tf = tempfile.NamedTemporaryFile(delete=False)
        tf.close()
        connection.sftp.get("/etc/rhui/pem/ca.pwd", tf.name)
        fd = open(tf.name, 'r')
        password = fd.read()
        fd.close()
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
