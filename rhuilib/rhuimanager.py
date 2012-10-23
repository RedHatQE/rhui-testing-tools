import re
from rhuilib.expect import *
from rhuilib.util import *


class RHUIManager:
    @staticmethod
    def select(connection, value_list):
        for value in value_list:
            match = Expect.match(connection, re.compile(".*-\s+([0-9]+)\s+:.*\s+" + value + "\s*\n.*for more commands:.*", re.DOTALL))
            Expect.enter(connection, match[0])
            match = Expect.match(connection, re.compile(".*x\s+([0-9]+)\s+:.*\s+" + value + "\s*\n.*for more commands:.*", re.DOTALL))
            Expect.enter(connection, "l")
        Expect.enter(connection, "c")

    @staticmethod
    def select_one(connection, value):
        match = Expect.match(connection, re.compile(".*([0-9]+)\s+-\s+" + value + "\s*\n.*to abort:.*", re.DOTALL))
        Expect.enter(connection, match[0])

    @staticmethod
    def quit(connection):
        Expect.expect(connection, "rhui \(.*\) =>")
        Expect.enter(connection, "q")

    @staticmethod
    def proceed(connection):
        Expect.expect(connection, "Proceed\? \(y/n\)")
        Expect.enter(connection, "y")

    @staticmethod
    def screen(connection, screen_name):
        Expect.enter(connection, "rhui-manager")
        Expect.expect(connection, "rhui \(home\) =>")
        if screen_name in ["repo", "cds", "sync", "identity", "users"]:
            key = screen_name[:1]
        elif screen_name == "client":
            key = "e"
        Expect.enter(connection, key)
        Expect.expect(connection, "rhui \(" + screen_name + "\) =>")

    @staticmethod
    def initial_run(connection, crt="/etc/rhui/pem/ca.crt", key="/etc/rhui/pem/ca.key", cert_pw=None, days="", username="admin", password="admin"):
        Expect.enter(connection, "rhui-manager")
        state = Expect.expect_list(connection, [(re.compile(".*Full path to the new signing CA certificate:.*", re.DOTALL), 1), (re.compile(".*rhui \(home\) =>.*", re.DOTALL), 2)])
        if state == 1:
            Expect.enter(connection, crt)
            Expect.expect(connection, "Full path to the new signing CA certificate private key:")
            Expect.enter(connection, key)
            Expect.expect(connection, "regenerated using rhui-manager.*:")
            Expect.enter(connection, days)
            Expect.expect(connection, "Enter pass phrase for.*:")
            if cert_pw:
                Expect.enter(connection, cert_pw)
            else:
                Expect.enter(connection, Util.getCaPassword(connection))
            Expect.expect(connection, "RHUI Username:")
            Expect.enter(connection, username)
            Expect.expect(connection, "RHUI Password:")
            Expect.enter(connection, password)
            Expect.expect(connection, "rhui \(home\) =>")
        else:
            # initial step was already performed by someone
            Expect.enter(connection, "q")
