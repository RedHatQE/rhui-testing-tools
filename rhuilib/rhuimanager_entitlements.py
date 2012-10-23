from rhuilib.expect import *
from rhuilib.rhuimanager import *


class RHUIManagerEntitlements:
    @staticmethod
    def upload_content_cert(connection, certpath):
        Expect.enter(connection, "mkdir -p `dirname " + certpath + "`")
        Expect.expect(connection, "root@")
        connection.sftp.put(certpath, certpath)
        RHUIManager.screen(connection, "entitlements")
        Expect.enter(connection, "u")
        Expect.expect(connection, "Full path to the new content certificate:")
        Expect.enter(connection, certpath)
        RHUIManager.proceed(connection)
        Expect.expect(connection, "Red Hat Entitlements.*Valid.*rhui \(entitlements\) =>")
        Expect.enter(connection, "q")
