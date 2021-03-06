""" RHUIManager Repo functions """

import re

from stitches.expect import Expect, ExpectFailed
from rhuilib.rhuimanager import RHUIManager


class RHUIManagerRepo(object):
    '''
    Represents -= Repository Management =- RHUI screen
    '''
    @staticmethod
    def add_custom_repo(connection, reponame, displayname="", path="", checksum_alg="2", entitlement="y", entitlement_path="", redhat_gpg="y", custom_gpg=None):
        '''
        create a new custom repository
        '''
        RHUIManager.screen(connection, "repo")
        Expect.enter(connection, "c")
        Expect.expect(connection, "Unique ID for the custom repository.*:")
        Expect.enter(connection, reponame)
        checklist = ["ID: " + reponame]
        Expect.expect(connection, "Display name for the custom repository.*:")
        Expect.enter(connection, displayname)
        if displayname != "":
            checklist.append("Name: " + displayname)
        else:
            checklist.append("Name: " + reponame)
        Expect.expect(connection, "Path at which the repository will be served.*:")
        Expect.enter(connection, path)
        if path != "":
            path_real = path
        else:
            path_real = reponame
        checklist.append("Path: " + path_real)
        Expect.expect(connection, "Enter value.*:")
        Expect.enter(connection, checksum_alg)
        Expect.expect(connection, "Should the repository require an entitlement certificate to access\? \(y/n\)")
        Expect.enter(connection, entitlement)
        if entitlement == "y":
            Expect.expect(connection, "Path that should be used when granting an entitlement for this repository.*:")
            Expect.enter(connection, entitlement_path)
            if entitlement_path != "":
                checklist.append("Entitlement: " + entitlement_path)
            else:
                educated_guess, replace_count = re.subn("(i386|x86_64)", "$basearch", path_real)
                if replace_count > 1:
                    # bug 815975
                    educated_guess = path_real
                checklist.append("Entitlement: " + educated_guess)
        Expect.expect(connection, "packages are signed by a GPG key\? \(y/n\)")
        if redhat_gpg == "y" or custom_gpg:
            Expect.enter(connection, "y")
            checklist.append("GPG Check Yes")
            Expect.expect(connection, "Will the repository be used to host any Red Hat GPG signed content\? \(y/n\)")
            Expect.enter(connection, redhat_gpg)
            if redhat_gpg == "y":
                checklist.append("Red Hat GPG Key: Yes")
            else:
                checklist.append("Red Hat GPG Key: No")
            Expect.expect(connection, "Will the repository be used to host any custom GPG signed content\? \(y/n\)")
            if custom_gpg:
                Expect.enter(connection, "y")
                Expect.expect(connection, "Enter the absolute path to the public key of the GPG keypair:")
                Expect.enter(connection, custom_gpg)
                Expect.expect(connection, "Would you like to enter another public key\? \(y/n\)")
                Expect.enter(connection, "n")
                checklist.append("Custom GPG Keys: '" + custom_gpg + "'")
            else:
                Expect.enter(connection, "n")
                checklist.append("Custom GPG Keys: \(None\)")
        else:
            Expect.enter(connection, "n")
            checklist.append("GPG Check No")
            checklist.append("Red Hat GPG Key: No")

        RHUIManager.proceed_with_check(connection, "The following repository will be created:", checklist)
        RHUIManager.quit(connection, "Successfully created repository")

    @staticmethod
    def add_rh_repo_all(connection):
        '''
        add a new Red Hat content repository (All in Certificate)
        '''
        RHUIManager.screen(connection, "repo")
        Expect.enter(connection, "a")
        Expect.expect(connection, "Import Repositories:.*to abort:", 180)
        Expect.enter(connection, "1")
        RHUIManager.proceed_without_check(connection)
        RHUIManager.quit(connection, "Content will not be downloaded", 45)

    @staticmethod
    def add_rh_repo_by_product(connection, productlist):
        '''
        add a new Red Hat content repository (By Product)
        '''
        RHUIManager.screen(connection, "repo")
        Expect.enter(connection, "a")
        Expect.expect(connection, "Import Repositories:.*to abort:", 180)
        Expect.enter(connection, "2")
        RHUIManager.select(connection, productlist)
        RHUIManager.proceed_with_check(connection, "The following products will be deployed:", productlist)
        RHUIManager.quit(connection, "Content will not be downloaded", 45)

    @staticmethod
    def add_rh_repo_by_repo(connection, repolist):
        '''
        add a new Red Hat content repository (By Repository)
        '''
        RHUIManager.screen(connection, "repo")
        Expect.enter(connection, "a")
        Expect.expect(connection, "Import Repositories:.*to abort:", 180)
        Expect.enter(connection, "3")
        RHUIManager.select(connection, repolist)
        repocheck = list(repolist)
        for repo in repolist:
            #adding repo titles to check list
            repotitle = re.sub(" \\\\\([^\(]*\\\\\)$", "", repo)
            if not repotitle in repocheck:
                repocheck.append(repotitle)
        RHUIManager.proceed_with_check(connection, "The following product repositories will be deployed:", repocheck)
        RHUIManager.quit(connection, "Content will not be downloaded", 45)

    @staticmethod
    def delete_repo(connection, repolist):
        '''
        delete a repository from the RHUI
        '''
        RHUIManager.screen(connection, "repo")
        Expect.enter(connection, "d")
        RHUIManager.select(connection, repolist)
        RHUIManager.proceed_with_check(connection, "The following repositories will be deleted:", repolist, ["Red Hat Repositories", "Custom Repositories"])
        RHUIManager.quit(connection)

    @staticmethod
    def upload_content(connection, repolist, path):
        '''
        upload content to a custom repository
        '''
        RHUIManager.screen(connection, "repo")
        Expect.enter(connection, "u")
        RHUIManager.select(connection, repolist)
        Expect.expect(connection, "will be uploaded:")
        Expect.enter(connection, path)
        RHUIManager.proceed_without_check(connection)
        RHUIManager.quit(connection)

    @staticmethod
    def check_for_package(connection, reponame, package):
        '''
        list packages in a repository
        '''
        RHUIManager.screen(connection, "repo")
        Expect.enter(connection, "p")
        RHUIManager.select_one(connection, reponame)
        Expect.expect(connection, "\(blank line for no filter\):")
        Expect.enter(connection, package)

        pattern = re.compile('.*only\.\r\n(.*)\r\n-+\r\nrhui\s* \(repo\)\s* =>',
                             re.DOTALL)
        ret = Expect.match(connection, pattern, grouplist=[1])[0]
        reslist = map(lambda x: x.strip(), ret.split("\r\n"))
        print reslist
        packagelist = []
        for line in reslist:
            if line == '':
                continue
            if line == 'Packages:':
                continue
            if line == 'No packages found that match the given filter.':
                continue
            if line == 'No packages in the repository.':
                continue
            packagelist.append(line)

        Expect.enter(connection, 'q')
        return packagelist

    @staticmethod
    def list(connection):
        '''
        list repositories
        '''
        RHUIManager.screen(connection, "repo")
        Expect.enter(connection, "l")
        # eating prompt!!
        pattern = re.compile('l\r\n(.*)\r\n-+\r\nrhui\s* \(repo\)\s* =>',
                re.DOTALL)
        ret = Expect.match(connection, pattern, grouplist=[1])[0]
        print ret
        reslist = map(lambda x: x.strip(), ret.split("\r\n"))
        print reslist
        repolist = []
        for line in reslist:
            # Readling lines and searching for repos
            if line == '':
                continue
            if "Custom Repositories" in line:
                continue
            if "Red Hat Repositories" in line:
                continue
            if "No repositories are currently managed by the RHUI" in line:
                continue
            repolist.append(line)

        Expect.enter(connection, 'q')
        return repolist

    @staticmethod
    def info(connection, repolist):
        '''
        detailed information about repositories

        Method returns list of items from rhui-manager info screen. Some of them are variable and these are replaced by "rh_repo" constant.
        '''
        RHUIManager.screen(connection, "repo")
        Expect.enter(connection, "i")
        RHUIManager.select(connection, repolist)

        try:
            pattern = re.compile('.*for more commands: \r\n\r\nName:\s(.*)\r\n-+\r\nrhui\s* \(repo\)\s* =>',
                                 re.DOTALL)
            ret = Expect.match(connection, pattern, grouplist=[1])[0]
            print ret
            res = map(lambda x: x.strip(), ret.split("\r\n"))
            reslist = ["Name:"]
            for line in res:
                reslist.extend(map(lambda y: y.strip(), re.split("\s{3}", line)))
            print reslist
            repoinfo = []
            rh_repo = 0
            rh_repo_info = 0
            for line in reslist:
                # Readling lines
                if line == '':
                    continue
                if rh_repo_info == 1:
                    line = "rh_repo"
                    rh_repo_info = 0
                if line == "Red Hat":
                    rh_repo = 1
                if "Relative Path:" in line:
                    if rh_repo == 1:
                        rh_repo_info = 1
                if "Package Count:" in line:
                    if rh_repo == 1:
                        rh_repo_info = 1
                if "Last Sync:" in line:
                    if rh_repo == 1:
                        rh_repo_info = 1
                if "Next Sync:" in line:
                    if rh_repo == 1:
                        rh_repo_info = 1
                repoinfo.append(line)
            print repoinfo

        except:
            repoinfo = []

        Expect.enter(connection, 'q')
        return repoinfo
