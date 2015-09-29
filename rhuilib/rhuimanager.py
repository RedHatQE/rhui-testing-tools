import re
import logging

from stitches.expect import Expect, ExpectFailed
from rhuilib.util import Util

SELECT_PATTERN = re.compile('^  (x|-)  (\d+) :')
PROCEED_PATTERN = re.compile('.*Proceed\? \(y/n\).*', re.DOTALL)
CONFIRM_PATTERN_STRING = "Enter value \([\d]+-[\d]+\) to toggle selection, 'c' to confirm selections, or '\?' for more commands: "

class NotSelectLine(ValueError):
    """
    to be risen when the line isn't actually a selection line
    """

class RHUIManager(object):
    '''
    Basic functions to manage rhui-manager.
    '''

    @staticmethod
    def selected_line(line):
        """
        return True/False, item list index
        """
        match = SELECT_PATTERN.match(line)
        if match is None:
            raise NotSelectLine(line)
        return match.groups()[0] == 'x', int(match.groups()[1])

    @staticmethod
    def list_lines(connection, prompt='', enter_l=True):
        '''
        list items on screen returning a list of lines seen
        eats prompt!!!
        '''
        if enter_l:
            Expect.enter(connection, "l")
        match = Expect.match(connection, re.compile("(.*)" + prompt, re.DOTALL))
        return match[0].split('\r\n')

    @staticmethod
    def select_items(connection, *items):
        '''
        Select list of items (multiple choice)
        '''
        for item in items:
            index = 0
            selected = False
            lines = RHUIManager.list_lines(connection, prompt=CONFIRM_PATTERN_STRING, enter_l=False)
            selected, index = item.selected(lines)
            if not selected:
                # insert the on-screen index nr to trigger item selection
                Expect.enter(connection, str(index))
                lines = RHUIManager.list_lines(connection, prompt=CONFIRM_PATTERN_STRING, enter_l=False)
                selected, index = item.selected(lines)
                assert selected, 'item #%s %s not selected' % (index, item)
        # confirm selection
        Expect.enter(connection, "c")

    @staticmethod
    def select_one(connection, item):
        '''
        Select one item (single choice)
        '''
        match = Expect.match(connection, re.compile(".*([0-9]+)\s+-\s+" + value + "\s*\n.*to abort:.*", re.DOTALL))
        Expect.enter(connection, match[0])

    @staticmethod
    def quit(connection, prefix="", timeout=10):
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
            val = val.replace("\t", " ")
            val = ' '.join(val.split())
            val = val.replace("(", "\(")
            val = val.replace(")", "\)")
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
        elif screen_name == "haproxy":
            key = "l"
        Expect.enter(connection, key)
        Expect.expect(connection, "rhui \(" + screen_name + "\) =>")

    @staticmethod
    def initial_run(connection, crt="/etc/rhui/pem/ca.crt", key="/etc/rhui/pem/ca.key", cert_pw=None, days="", username="admin", password="admin"):
        '''
        Do rhui-manager initial run
        '''
        Expect.enter(connection, "rhui-manager")
        state = Expect.expect_list(connection, [(re.compile(".*Full path to the new signing CA certificate:.*", re.DOTALL), 1),
                                                (re.compile(".*RHUI Username:.*", re.DOTALL),2),
                                                (re.compile(".*rhui \(home\) =>.*", re.DOTALL), 3)])
        if state in [1, 2]:
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
                    Expect.enter(connection, Util.get_ca_password(connection))
                Expect.expect(connection, "RHUI Username:")
            Expect.enter(connection, username)
            Expect.expect(connection, "RHUI Password:")
            Expect.enter(connection, password)
            Expect.expect(connection, "rhui \(home\) =>")
        else:
            # initial step was already performed by someone
            pass
        Expect.enter(connection, "q")

    @staticmethod
    def remove_rh_certs(connection):
        '''
        Remove all RH certificates from RHUI
        '''
        Expect.enter(connection, "find /etc/pki/rhui/redhat/ -name '*.pem' -delete")
        Expect.expect(connection, "root@")
