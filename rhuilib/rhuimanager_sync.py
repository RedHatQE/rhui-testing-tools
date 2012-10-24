import re

from rhuilib.expect import *
from rhuilib.rhuimanager import *


class RHUIManagerSync:
    '''
    Represents -= Synchronization Status =- RHUI screen
    '''
    @staticmethod
    def sync_cds(connection, cdslist):
        '''
        sync an individual CDS immediately
        '''
        RHUIManager.screen(connection, "sync")
        Expect.enter(connection, "sc")
        RHUIManager.select(connection, cdslist)
        RHUIManager.proceed(connection)
        RHUIManager.quit(connection)

    @staticmethod
    def sync_cluster(connection, clusterlist):
        '''
        sync a CDS cluster immediately
        '''
        RHUIManager.screen(connection, "sync")
        Expect.enter(connection, "sl")
        RHUIManager.select(connection, clusterlist)
        RHUIManager.proceed(connection)
        RHUIManager.quit(connection)

    @staticmethod
    def get_cds_status(connection, cdsname):
        '''
        display CDS sync summary
        '''
        RHUIManager.screen(connection, "sync")
        Expect.enter(connection, "dc")
        res_list = Expect.match(connection, re.compile(".*" + cdsname.replace(".", "\.") + "[\.\s]*\[([^\n]*)\].*" + cdsname.replace(".", "\.") + "\s*\r\n[\s0-9\-:]+([^\n]*)\r\n", re.DOTALL), [1, 2])
        connection.channel.close()
        connection.channel = connection.cli.invoke_shell()
        ret_list = []
        for val in res_list:
            val = val.replace("\x1b", "")
            val = val.replace("[92m", "")
            val = val.replace("[0m", "")
            val = val.replace(" ", "")
            ret_list.append(val)
        return ret_list

    @staticmethod
    def sync_repo(connection, repolist):
        '''
        sync an individual repository immediately
        '''
        RHUIManager.screen(connection, "sync")
        Expect.enter(connection, "sr")
        Expect.expect(connection,"Select one or more repositories.*for more commands:", 60)
        Expect.enter(connection, "l")
        RHUIManager.select(connection, repolist)
        RHUIManager.proceed_with_check(connection, "The following repositories will be scheduled for synchronization:", repolist)
        RHUIManager.quit(connection)
