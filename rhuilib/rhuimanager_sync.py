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
        RHUIManager.proceed_with_check(connection, "The following CDS instances will be scheduled for synchronization:", cdslist)
        RHUIManager.quit(connection)

    @staticmethod
    def sync_cluster(connection, clusterlist):
        '''
        sync a CDS cluster immediately
        '''
        RHUIManager.screen(connection, "sync")
        Expect.enter(connection, "sl")
        RHUIManager.select(connection, clusterlist)
        RHUIManager.proceed_with_check(connection, "The following CDS clusters will be scheduled for synchronization:", clusterlist)
        RHUIManager.quit(connection)

    @staticmethod
    def get_cds_status(connection, cdsname):
        '''
        display CDS sync summary
        '''
        RHUIManager.screen(connection, "sync")
        Expect.enter(connection, "dc")
        res_list = Expect.match(connection, re.compile(".*\n" + cdsname.replace(".", "\.") + "[\.\s]*\[([^\n]*)\].*" + cdsname.replace(".", "\.") + "\s*\r\n([^\n]*)\r\n", re.DOTALL), [1, 2], 60)
        connection.cli.exec_command("killall -s SIGINT rhui-manager")
        ret_list = []
        for val in [res_list[0]] + res_list[1].split("             "):
            val = Util.uncolorify(val.strip())
            ret_list.append(val)
        RHUIManager.quit(connection)
        return ret_list

    @staticmethod
    def sync_repo(connection, repolist):
        '''
        sync an individual repository immediately
        '''
        RHUIManager.screen(connection, "sync")
        Expect.enter(connection, "sr")
        Expect.expect(connection, "Select one or more repositories.*for more commands:", 60)
        Expect.enter(connection, "l")
        RHUIManager.select(connection, repolist)
        RHUIManager.proceed_with_check(connection, "The following repositories will be scheduled for synchronization:", repolist)
        RHUIManager.quit(connection)

    @staticmethod
    def get_repo_status(connection, reponame):
        '''
        display repo sync summary
        '''
        RHUIManager.screen(connection, "sync")
        Expect.enter(connection, "dr")
        reponame_quoted = reponame.replace(".", "\.")
        res = Expect.match(connection, re.compile(".*" + reponame_quoted + "\s*\r\n([^\n]*)\r\n.*", re.DOTALL), [1], 60)[0]
        connection.cli.exec_command("killall -s SIGINT rhui-manager")
        res = Util.uncolorify(res)
        ret_list = res.split("             ")
        for i in range(len(ret_list)):
            ret_list[i] = ret_list[i].strip()
        RHUIManager.quit(connection)
        return ret_list
