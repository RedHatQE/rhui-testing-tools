from patchwork.expect import *
from rhuilib.rhuimanager import *


class RHUIManagerUsers:
    '''
    Represents -= User Manager =- RHUI screen
    '''
    @staticmethod
    def change_password(connection, username, password):
        '''
        change a user's password
        '''
        RHUIManager.screen(connection, "users")
        Expect.enter(connection, "p")
        Expect.expect(connection, "Username:")
        Expect.enter(connection, username)
        Expect.expect(connection, "New Password:")
        Expect.enter(connection, password)
        Expect.expect(connection, "Re-enter Password:")
        Expect.enter(connection, password)
        RHUIManager.quit(connection, "Password successfully updated")
