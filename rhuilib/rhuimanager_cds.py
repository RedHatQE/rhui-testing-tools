import re

from rhuilib.expect import *
from rhuilib.rhuimanager import *


class RHUIManagerCds:
    '''
    Represents -= Content Delivery Server (CDS) Management =- RHUI screen
    '''
    @staticmethod
    def _add_cds_part1(connection, clustername, cdsname, hostname="", displayname=""):
        '''
        service function for add_cds
        '''
        Expect.enter(connection, "a")
        Expect.expect(connection, "Hostname of the CDS to register:")
        Expect.enter(connection, cdsname)
        Expect.expect(connection, "Client hostname \(hostname clients will use to connect to the CDS\).*:")
        Expect.enter(connection, hostname)
        Expect.expect(connection, "Display name for the CDS.*:")
        Expect.enter(connection, displayname)

    @staticmethod
    def add_cds(connection, clustername, cdsname, hostname="", displayname=""):
        '''
        register (add) a new CDS instance
        '''
        RHUIManager.screen(connection, "cds")
        RHUIManagerCds._add_cds_part1(connection, clustername, cdsname, hostname, displayname)
        state = Expect.expect_list(connection, [(re.compile(".*Enter a CDS cluster name:.*", re.DOTALL), 1), (re.compile(".*Select a CDS cluster or enter a new one:.*", re.DOTALL), 2)])
        if state == 1:
            Expect.enter(connection, clustername)
        else:
            Expect.enter(connection, 'b')
            RHUIManagerCds._add_cds_part1(connection, clustername, cdsname, hostname, displayname)
            try:
                select = Expect.match(connection, re.compile(".*\s+([0-9]+)\s*-\s*" + clustername + "\s*\r\n.*to abort:.*", re.DOTALL))
                Expect.enter(connection, select[0])
            except ExpectFailed:
                Expect.enter(connection, "1")
                Expect.expect(connection, "Enter a CDS cluster name:")
                Expect.enter(connection, clustername)
        # We need to compare the output before proceeding
        checklist = ["Hostname: " + cdsname]
        if hostname != "":
            checklist.append("Client Hostname: " + hostname)
        else:
            checklist.append("Client Hostname: " + cdsname)
        if displayname != "":
            checklist.append("Name: " + displayname)
        else:
            checklist.append("Name: " + cdsname)
        checklist.append("Cluster: " + clustername)
        RHUIManager.proceed_with_check(connection, "The following CDS instance will be registered:", checklist)
        Expect.expect(connection, "Successfully registered.*rhui \(cds\) =>.*")
        Expect.enter(connection, "q")

    @staticmethod
    def delete_cds(connection, clustername, cdslist):
        '''
        unregister (delete) a CDS instance from the RHUI
        '''
        RHUIManager.screen(connection, "cds")
        Expect.enter(connection, "d")
        RHUIManager.select_one(connection, clustername)
        RHUIManager.select(connection, cdslist)
        RHUIManager.proceed_with_check(connection, "The following CDS instances from the %s cluster will be unregistered:"
                % clustername, cdslist)
        RHUIManager.quit(connection)

    @staticmethod
    def associate_repo_cds(connection, clustername, repolist):
        '''
        associate a repository with a CDS cluster
        '''
        RHUIManager.screen(connection, "cds")
        Expect.enter(connection, "s")
        RHUIManager.select_one(connection, clustername)
        RHUIManager.select(connection, repolist)
        RHUIManager.proceed_with_check(connection, "The following repositories will be associated with the " + clustername + " cluster:", repolist, ["Red Hat Repositories", "Custom Repositories"])
        RHUIManager.quit(connection)

    @staticmethod
    def unassociate_repo_cds(connection, clustername, repolist):
        '''
        unassociate a repository with a CDS cluster
        '''
        RHUIManager.screen(connection, "cds")
        Expect.enter(connection, "u")
        RHUIManager.select_one(connection, clustername)
        RHUIManager.select(connection, repolist)
        RHUIManager.proceed_with_check(connection, "The following repositories will be unassociated from the " + clustername + " cluster:", repolist, ["Red Hat Repositories", "Custom Repositories"])
        RHUIManager.quit(connection)

    @staticmethod
    def list(connection):
        '''
        return the list currently managed CDSes and clusters as it is provided
        by the cds list command
        '''
        RHUIManager.screen(connection, "cds")
        Expect.enter(connection, "l")
        pattern = re.compile('l(\r\n)+(.*)rhui\s* \(cds\)\s* =>',
                re.DOTALL)
        return Expect.match(connection, pattern, grouplist=[2])[0]
