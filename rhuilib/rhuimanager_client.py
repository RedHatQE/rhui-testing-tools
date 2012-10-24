from rhuilib.expect import *
from rhuilib.util import *
from rhuilib.rhuimanager import *


class RHUIManagerClient:
    '''
    Represents -= Client Entitlement Management =- RHUI screen
    '''
    @staticmethod
    def generate_ent_cert(connection, clustername, repolist, certname, dirname, validity_days="", cert_pw=None):
        '''
        generate an entitlement certificate
        '''
        RHUIManager.screen(connection, "client")
        Expect.enter(connection, "e")
        RHUIManager.select_one(connection, clustername)
        RHUIManager.select(connection, repolist)
        Expect.expect(connection, "Name of the certificate.*contained with it:")
        Expect.enter(connection, certname)
        Expect.expect(connection, "Local directory in which to save the generated certificate.*:")
        Expect.enter(connection, dirname)
        Expect.expect(connection, "Number of days the certificate should be valid.*:")
        Expect.enter(connection, validity_days)
        RHUIManager.proceed_with_check(connection, "Repositories to be included in the entitlement certificate:", repolist, ["Custom Entitlements", "Red Hat Repositories"])
        Expect.expect(connection, "Enter pass phrase for.*:")
        if cert_pw:
            Expect.enter(connection, cert_pw)
        else:
            Expect.enter(connection, Util.getCaPassword(connection))
        RHUIManager.quit(connection)

    @staticmethod
    def create_conf_rpm(connection, clustername, primary_cds, dirname, certpath, certkey, rpmname, rpmversion=""):
        '''
        create a client configuration RPM from an entitlement certificate
        '''
        RHUIManager.screen(connection, "client")
        Expect.enter(connection, "c")
        Expect.expect(connection, "Full path to local directory.*:")
        Expect.enter(connection, dirname)
        Expect.expect(connection, "Name of the RPM:")
        Expect.enter(connection, rpmname)
        Expect.expect(connection, "Version of the configuration RPM.*:")
        Expect.enter(connection, rpmversion)
        Expect.expect(connection, "Full path to the entitlement certificate.*:")
        Expect.enter(connection, certpath)
        Expect.expect(connection, "Full path to the private key for the above entitlement certificate:")
        Expect.enter(connection, certkey)
        RHUIManager.select_one(connection, clustername)
        RHUIManager.select_one(connection, primary_cds)
        RHUIManager.quit(connection)
