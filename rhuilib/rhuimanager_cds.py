""" RHUIManager CDS functions """

import re

from patchwork.expect import Expect, ExpectFailed
from rhuilib.rhuimanager import RHUIManager
from rhuilib.cds import RhuiCds


class RHUIManagerCds(object):
    '''
    Represents -= Content Delivery Server (CDS) Management =- RHUI screen
    '''
    @staticmethod
    def _add_cds_part1(connection, cdsname, hostname="", displayname=""):
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
    def _select_cluster(connection, clustername, create_new=True):
        '''
        select cluster
        '''
        try:
            select = Expect.match(connection, re.compile(".*\s+([0-9]+)\s*-\s*" + clustername + "\s*\r\n.*to abort:.*", re.DOTALL))
            Expect.enter(connection, select[0])
        except ExpectFailed as err:
            if not create_new:
                raise err
            Expect.enter(connection, "1")
            Expect.expect(connection, "Enter a[^\n]*CDS cluster name:")
            Expect.enter(connection, clustername)

    @staticmethod
    def add_cds(connection, clustername, cdsname, hostname="", displayname=""):
        '''
        register (add) a new CDS instance
        '''
        RHUIManager.screen(connection, "cds")
        RHUIManagerCds._add_cds_part1(connection, cdsname, hostname, displayname)
        state = Expect.expect_list(connection, [(re.compile(".*Enter a CDS cluster name:.*", re.DOTALL), 1),
                                                (re.compile(".*Select a CDS cluster or enter a new one:.*", re.DOTALL), 2)])
        if state == 1:
            Expect.enter(connection, clustername)
        else:
            Expect.enter(connection, 'b')
            Expect.expect(connection, "rhui \(cds\) =>")
            RHUIManagerCds._add_cds_part1(connection, cdsname, hostname, displayname)
            RHUIManagerCds._select_cluster(connection, clustername)
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
        RHUIManager.quit(connection, "Successfully registered")

    @staticmethod
    def delete_cds(connection, clustername, cdslist, force=False):
        '''
        unregister (delete) a CDS instance from the RHUI
        '''
        RHUIManager.screen(connection, "cds")
        Expect.enter(connection, "d")
        RHUIManager.select_one(connection, clustername)
        RHUIManager.select(connection, cdslist)
        RHUIManager.proceed_with_check(connection, "The following CDS instances from the %s cluster will be unregistered:"
                % clustername, cdslist)
        if force:
            Expect.expect(connection, "Forcibly remove these CDS instances", 60)
            Expect.enter(connection, "y")
        RHUIManager.quit(connection, timeout=30)

    @staticmethod
    def associate_repo_cds(connection, clustername, repolist):
        '''
        associate a repository with a CDS cluster
        '''
        RHUIManager.screen(connection, "cds")
        Expect.enter(connection, "s")
        RHUIManager.select_one(connection, clustername)
        RHUIManager.select(connection, repolist)
        RHUIManager.proceed_with_check(connection, "The following repositories will be associated with the " + clustername + " cluster:",
                                       repolist, ["Red Hat Repositories", "Custom Repositories"])
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
        RHUIManager.proceed_with_check(connection, "The following repositories will be unassociated from the " + clustername + " cluster:",
                                       repolist, ["Red Hat Repositories", "Custom Repositories"])
        RHUIManager.quit(connection)

    @staticmethod
    def list(connection):
        '''
        return the list currently managed CDSes and clusters as it is provided
        by the cds list command
        '''
        RHUIManager.screen(connection, "cds")
        Expect.enter(connection, "l")
        # eating prompt!!
        pattern = re.compile('l(\r\n)+(.*)rhui\s* \(cds\)\s* =>',
                re.DOTALL)
        ret = Expect.match(connection, pattern, grouplist=[2])[0]
        # custom quitting; have eaten the prompt
        Expect.enter(connection, 'q')
        return ret

    @staticmethod
    def info(connection, clusterlist):
        '''
        display detailed information on a CDS clusters

        @param clusterlist - list of clusters to examine
        @returns a list of Cds instances
        '''
        RHUIManager.screen(connection, "cds")
        Expect.enter(connection, "i")
        RHUIManager.select(connection, clusterlist)
        pattern = re.compile('.*-= RHUI CDS Clusters =-(.*)rhui\s* \(cds\)\s* =>',
                re.DOTALL)
        ret = Expect.match(connection, pattern, grouplist=[1])[0]
        reslist = ret.split("\r\n")
        i = 0
        clusterlist = []
        cluster = {}
        while i < len(reslist):
            line = reslist[i]
            # Readling lines and searching for clusters
            if line.strip() != '':
                if line[:2] == '  ' and not line[2:3] in [' ', '-']:
                    # We've found a new cluster!
                    if cluster != {}:
                        clusterlist.append(cluster)
                        cluster = {}
                    cluster['Name'] = line[2:]
                    i += 2
                    while reslist[i][:4] == '    ' or reslist[i] == '':
                        if reslist[i] == '':
                            i += 1
                            continue
                        line = reslist[i].strip()
                        if line == "CDS Instances":
                            # Figuring out cds instances
                            instances = []
                            i += 2
                            while reslist[i].strip() != "":
                                # New cds
                                cds = reslist[i].strip()
                                hostname = reslist[i + 1].strip().split(':')[1].strip()
                                client = reslist[i + 2].strip().split(':')[1].strip()
                                instances.append(RhuiCds(name=reslist[i].strip(), hostname=hostname, client_hostname=client,
                                    description='RHUI CDS',
                                    cluster=cluster['Name']))
                                i += 3
                            cluster['Instances'] = sorted(instances)
                        elif line == "Repositories":
                            # Figuring out repositories
                            repositories = []
                            i += 2
                            while reslist[i].strip() != "":
                                # New repo
                                repo = reslist[i].strip()
                                i += 1
                                if repo == '(None)':
                                    # no repos, continue with next (empty)
                                    # line
                                    continue
                                repositories.append(repo)
                            cluster['Repositories'] = repositories
                            # update all cluster CDSes with appropriate repo
                            # records
                            for cds in cluster['Instances']:
                                cds.repos = repositories
                            break
                        else:
                            i += 1
            i += 1

        if cluster != {}:
            clusterlist.append(cluster)
        cdses = []
        for cluster in clusterlist:
            cdses.extend(cluster['Instances'])
        Expect.enter(connection, 'q')
        return cdses

    @staticmethod
    def move_cds(connection, cdslist, clustername):
        '''
        move the CDSes to clustername
        '''
        RHUIManager.screen(connection, "cds")
        Expect.enter(connection, "m")
        RHUIManager.select(connection, cdslist)
        RHUIManagerCds._select_cluster(connection, clustername)
        RHUIManager.proceed_with_check(connection,
                "The following Content Delivery Servers will be moved to the %s cluster:\r\n.*-+" % clustername,
                cdslist)
        RHUIManager.quit(connection, "successfully moved CDS")
