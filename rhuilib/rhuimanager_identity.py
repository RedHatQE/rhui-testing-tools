from rhuilib.expect import *
from rhuilib.rhuimanager import *


class RHUIManagerIdentity:
    @staticmethod
    def generate_new(connection, days="", cert_pw=None):
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
            Expect.enter(connection, Util.getCaPassword(connection))
        Expect.expect(connection, "Successfully regenerated RHUI Identity certificate.*rhui \(identity\) =>")
        Expect.enter(connection, "q")
