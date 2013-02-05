import re

from patchwork.expect import *
from rhuilib.rhuimanager import *


class RHUIManagerRepo:
    '''
    Represents -= Repository Management =- RHUI screen
    '''
    @staticmethod
    def add_custom_repo(connection, reponame, displayname="", path="", checksum_alg="1", entitlement="y", entitlement_path="", redhat_gpg="y", custom_gpg=None):
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
            checklist.append("Path: " + path)
        else:
            checklist.append("Path: " + reponame)
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
                educated_guess, replace_count = re.subn("(i386|x86_64)","$basearch", path)
                if replace_count > 1:
                    # bug 815975
                    educated_guess = path
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
        Expect.expect(connection, "Import Repositories:.*to abort:", 120)
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
        Expect.expect(connection, "Import Repositories:.*to abort:", 120)
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
        Expect.expect(connection, "Import Repositories:.*to abort:", 120)
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
        RHUIManager.quit(connection, "Packages:")
