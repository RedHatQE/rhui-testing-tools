from rhuilib.expect import *
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
        Expect.expect(connection, "Display name for the custom repository.*:")
        Expect.enter(connection, displayname)
        Expect.expect(connection, "Path at which the repository will be served.*:")
        Expect.enter(connection, path)
        Expect.expect(connection, "Enter value.*:")
        Expect.enter(connection, checksum_alg)
        Expect.expect(connection, "Should the repository require an entitlement certificate to access\? \(y/n\)")
        Expect.enter(connection, entitlement)
        if entitlement == "y":
            Expect.expect(connection, "Path that should be used when granting an entitlement for this repository.*:")
            Expect.enter(connection, entitlement_path)
        Expect.expect(connection, "packages are signed by a GPG key\? \(y/n\)")
        if redhat_gpg or custom_gpg:
            Expect.enter(connection, "y")
            Expect.expect(connection, "Will the repository be used to host any Red Hat GPG signed content\? \(y/n\)")
            Expect.enter(connection, redhat_gpg)
            Expect.expect(connection, "Will the repository be used to host any custom GPG signed content\? \(y/n\)")
            if custom_gpg:
                Expect.enter(connection, "y")
                Expect.expect(connection, "Enter the absolute path to the public key of the GPG keypair:")
                Expect.enter(connection, custom_gpg)
            else:
                Expect.enter(connection, "n")
        else:
            Expect.enter(connection, "n")
        RHUIManager.proceed(connection)
        Expect.expect(connection, "Successfully created repository.*rhui \(repo\) =>")
        Expect.enter(connection, "q")

    @staticmethod
    def add_rh_repo(connection, reponame):
        '''
        add a new Red Hat content repository
        '''
        RHUIManager.screen(connection, "repo")
        Expect.enter(connection, "a")
        #not finished

    @staticmethod
    def delete_custom_repo(connection, repolist):
        '''
        delete a repository from the RHUI
        '''
        RHUIManager.screen(connection, "repo")
        Expect.enter(connection, "d")
        RHUIManager.select(connection, repolist)
        RHUIManager.proceed(connection)
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
        RHUIManager.proceed(connection)
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
        Expect.expect(connection, "Packages:.*rhui \(repo\) =>")
        Expect.enter(connection, "q")
