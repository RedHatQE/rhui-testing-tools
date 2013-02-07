from patchwork.expect import *
from rhuilib.rhuimanager import *


class RHUIManagerEntitlements:
    '''
    Represents -= Entitlements Manager =- RHUI screen
    '''
    @staticmethod
    def upload_content_cert(connection, certpath):
        '''
        upload a new or updated Red Hat content certificate
        '''
        if certpath[:1] == '/':
            Expect.enter(connection, "mkdir -p `dirname " + certpath + "` && echo SUCCESS")
            Expect.expect(connection, "[^ ]SUCCESS")
        connection.sftp.put(certpath, certpath)
        RHUIManager.screen(connection, "entitlements")
        Expect.enter(connection, "u")
        Expect.expect(connection, "Full path to the new content certificate:")
        Expect.enter(connection, certpath)
        RHUIManager.proceed_with_check(connection, "The RHUI will be updated with the following certificate:", [certpath])
        RHUIManager.quit(connection, "Red Hat Entitlements.*Valid.*------------------")
