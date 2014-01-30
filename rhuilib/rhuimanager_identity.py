""" RHUIManager Identity functions """

from patchwork.expect import Expect
from rhuilib.rhuimanager import RHUIManager
from rhuilib.util import Util


class RHUIManagerIdentity(object):
    '''
    Represents -= Identity Certificate Management =- RHUI screen
    '''
    @staticmethod
    def generate_new(connection, days="", cert_pw=None):
        '''
        generate a new identity certificate
        '''
        RHUIManager.screen(connection, "identity")
        Expect.enter(connection, "g")
        Expect.expect(connection, "Proceed\? \[y/n\]")
        Expect.enter(connection, "y")
        Expect.expect(connection, "regenerated using rhui-manager.*:")
        Expect.enter(connection, days)
        Expect.expect(connection, "Enter pass phrase for.*:")
        if cert_pw:
            Expect.enter(connection, cert_pw)
        else:
            Expect.enter(connection, Util.get_ca_password(connection))
        RHUIManager.quit(connection, "Successfully regenerated RHUI Identity certificate", 30)
