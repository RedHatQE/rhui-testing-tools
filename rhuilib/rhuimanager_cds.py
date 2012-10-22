from rhuilib.expect import *
from rhuilib.rhuimanager import *


class RHUIManagerCds:
    @staticmethod
    def add_cds(connection, clustername, cdsname, hostname="", displayname=""):
        RHUIManager.screen(connection, "cds")
        Expect.enter(connection, "a")
        Expect.expect(connection, "Hostname of the CDS to register:")
        Expect.enter(connection, cdsname)
        Expect.expect(connection, "Client hostname \(hostname clients will use to connect to the CDS\).*:")
        Expect.enter(connection, hostname)
        Expect.expect(connection, "Display name for the CDS.*:")
        Expect.enter(connection, displayname)
        Expect.expect(connection, "Enter a CDS cluster name:")
        Expect.enter(connection, clustername)
        RHUIManager.proceed(connection)
        RHUIManager.quit(connection)

    @staticmethod
    def delete_cds(connection, clustername, cdslist):
        RHUIManager.screen(connection, "cds")
        Expect.enter(connection, "d")
        RHUIManager.select_one(connection, clustername)
        RHUIManager.select(connection, cdslist)
        RHUIManager.proceed(connection)
        RHUIManager.quit(connection)

    @staticmethod
    def associate_repo_cds(connection, clustername, repolist):
        RHUIManager.screen(connection, "cds")
        Expect.enter(connection, "s")
        RHUIManager.select_one(connection, clustername)
        RHUIManager.select(connection, repolist)
        RHUIManager.proceed(connection)
        RHUIManager.quit(connection)
