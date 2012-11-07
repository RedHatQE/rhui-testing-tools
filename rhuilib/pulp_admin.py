import re
from rhuilib.expect import Expect, ExpectFailed
from cds import PulpCds
from repo import PulpRepo

class PulpAdmin(object):
    """pulp-admin handler"""

    @staticmethod
    def command_output(connection, command, pattern_tuple, username="admin",
            password="admin"):
        """return output of a command based on pattern_tuple provided. Output
        is split to lines"""
        Expect.enter(connection, "pulp-admin -u %s -p %s %s" % \
                (username, password, command))
        # eats prompt!
        pattern, group_index = pattern_tuple
        ret = Expect.match(connection, pattern, grouplist=[group_index])[0]
        # reset prompt
        Expect.enter(connection, "")
        return ret.split('\r\n')
    @staticmethod
    def output_list_pattern(command, header):
        """
        command and header of the list are incorporated;
        returns a tuple (pattern, group_id); group_id points to the group
        command output will be stored in after a match
        """
        return (re.compile(".*" + command + "\r\n\+-+\+\r\n\s*"+ header +\
                "\s*\r\n\+-+\+(\r\n)+(.*)\[.*@.*\][\$#]", re.DOTALL), 2)
    @staticmethod
    def output_info_pattern(command):
        """
        command is incorporated;
        returns a tuple (pattern, group_id); group_id points to the group
        command output will be stored in after a match
        """
        return (re.compile(".*" + command +\
            "(\r\n)+(.*)(\r\n)+\[.*@.*\][\$#]", re.DOTALL), 2)
    @staticmethod
    def cds_list(connection, username="admin", password="admin"):
        """returns the output of pulp-admin cds list; header stripped off"""
        command = "cds list"
        header = "CDS Instances"
        pattern_tuple = PulpAdmin.output_list_pattern(command, header)
        lines = PulpAdmin.command_output(connection, command, pattern_tuple,
                username, password)
        return PulpAdmin._cds_lines_parser(lines)
    @staticmethod
    def cds_info(connection, cds_id, username="admin", password="admin"):
        """returns PulpCds object based on output of pulp-admin cds info
        command
        """
        command = "cds info --id %s" % cds_id
        pattern_tuple = PulpAdmin.output_info_pattern(command)
        lines = PulpAdmin.command_output(connection, command, pattern_tuple,
                username, password)
        return PulpAdmin._cds_lines_parser(lines)[0]
    @staticmethod
    def _cds_lines_parser(lines):
        """returns a list of PulpCds instances"""
        cdses = []
        cds = None
        for line in lines:
            words = line.split()
            if words == []:
                # skip empty lines
                continue
            # handle attributes
            if words[0] == 'Name':
                # the Name attribute means a start of a new cds record
                # push current cds instance and create a fresh one
                cds = PulpCds()
                cdses.append(cds)
                cds.name = words[1]
            if words[0] == 'Hostname':
                cds.hostname = words[1]
            if words[0] == 'Description':
                cds.description = " ".join(words[1:])
            if words[0] == 'Cluster':
                cds.cluster = words[1]
            if words[0] == 'Sync':
                if words[1] == 'Schedule':
                    cds.sync_schedule = " ".join(words[1:])
            if words[0] == 'Repos':
                if not words[1] == 'None':
                    cds.repos = words[1:]
            if words[0] == 'Last':
                if words[1] == 'Sync':
                    cds.last_sync = " ".join(words[2:])
                if words[1] == 'Heartbeat':
                    cds.last_heartbeat = " ".join(words[2:])
        return cdses
    @staticmethod
    def repo_list(connection, username="admin", password="admin"):
        """
        return the output of pulp-admin repo list parsed into PulpRepo
        objects
        """
        command = "repo list"
        header = "List of Available Reoisitories"
        pattern_tuple = PulpAdmin.output_list_pattern(command, header)
        lines = PulpAdmin.command_output(connection, command, pattern_tuple,
                username, password)
        return PulpAdmin._repo_lines_parser(lines)
    @staticmethod
    def repo_info(connection, repo_id, username="admin", password="admin"):
        """
        return the output of the repo id command parsed into PulpRepo object
        """
        command = "repo info --id %s" % repo_id
        pattern_tuple = PulpAdmin.output_info_pattern(command)
        lines = PulpAdmin.command(connection, command, pattern_tuple,
                username, password)
        return PulpAdmin._repo_lines_parser(lines)[0]
    @staticmethod
    def _repo_lines_parser(lines):
        """ returns a list of PulpRepo objects """
        repos = []
        repo = None
        for line in lines:
            words = line.split()
            if words[0] == 'Id':
                # Id means a start of a new repo record
                # push current repo and create a fresh one
                repo = PulpRepo(id = words[1])
                repos.append(repo)
            if words[0] == 'Name':
                repo.name = words[1]
            if words[0] == 'Repo':
                if words[1] == 'URL':
                    repo.url = "".join(words[2:])
            if words[0] == 'Packages':
                repo.package_count = int(word[1])
        return repos


__all__ = ['PulpAdmin']
