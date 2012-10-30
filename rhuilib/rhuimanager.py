import re
from rhuilib.expect import *
from rhuilib.util import *


class RHUIManager:
    '''
    Basic functions to manage rhui-manager.
    '''
    @staticmethod
    def select(connection, value_list):
        '''
        Select list of values (multiple choice)
        '''
        for value in value_list:
            match = Expect.match(connection, re.compile(".*-\s+([0-9]+)\s*:[^\n]*\s+" + value + "\s*\n.*for more commands:.*", re.DOTALL))
            Expect.enter(connection, match[0])
            match = Expect.match(connection, re.compile(".*x\s+([0-9]+)\s*:[^\n]*\s+" + value + "\s*\n.*for more commands:.*", re.DOTALL))
            Expect.enter(connection, "l")
        Expect.enter(connection, "c")

    @staticmethod
    def select_one(connection, value):
        '''
        Select one value (single choice)
        '''
        match = Expect.match(connection, re.compile(".*([0-9]+)\s+-\s+" + value + "\s*\n.*to abort:.*", re.DOTALL))
        Expect.enter(connection, match[0])

    @staticmethod
    def quit(connection, prefix="", timeout=5):
        '''
        Quit from rhui-manager
        
        Use @param prefix to specify something to expect before exiting
        Use @param timeout to specify the timeout
        '''
        Expect.expect(connection, prefix + ".*rhui \(.*\) =>", timeout)
        Expect.enter(connection, "q")

    @staticmethod
    def proceed_without_check(connection):
        '''
        Proceed without check (avoid this function when possible!)
        '''
        Expect.expect(connection, "Proceed\? \(y/n\)")
        Expect.enter(connection, "y")

    @staticmethod
    def proceed_with_check(connection, caption, value_list, skip_list=[]):
        '''
        Proceed with prior checking the list of values

        Use @param skip_list to skip meaningless 2nd-level headers
        '''
        selected = Expect.match(connection, re.compile(".*" + caption + "\r\n(.*)\r\nProceed\? \(y/n\).*", re.DOTALL))[0].split("\r\n")
        selected_clean = []
        for val in selected:
            val = val.strip()
            val = val.replace("\t"," ")
            val = ' '.join(val.split())
            val = val.replace("(","\(")
            val = val.replace(")","\)")
            if val != "" and not val in skip_list:
                selected_clean.append(val)
        if sorted(selected_clean) != sorted(value_list):
            logging.debug("Selected: " + str(selected_clean))
            logging.debug("Expected: " + str(value_list))
            raise ExpectFailed()
        Expect.enter(connection, "y")


    @staticmethod
    def screen(connection, screen_name):
        '''
        Open specified rhui-manager screen
        '''
        Expect.enter(connection, "rhui-manager")
        Expect.expect(connection, "rhui \(home\) =>")
        if screen_name in ["repo", "cds", "sync", "identity", "users"]:
            key = screen_name[:1]
        elif screen_name == "client":
            key = "e"
        elif screen_name == "entitlements":
            key = "n"
        Expect.enter(connection, key)
        Expect.expect(connection, "rhui \(" + screen_name + "\) =>")

    @staticmethod
    def initial_run(connection, crt="/etc/rhui/pem/ca.crt", key="/etc/rhui/pem/ca.key", cert_pw=None, days="", username="admin", password="admin"):
        '''
        Do rhui-manager initial run
        '''
        Expect.enter(connection, "rhui-manager")
        state = Expect.expect_list(connection, [(re.compile(".*Full path to the new signing CA certificate:.*", re.DOTALL), 1), (re.compile(".*rhui \(home\) =>.*", re.DOTALL), 2)])
        if state == 1:
            # Need to answer sone first-run questions
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
