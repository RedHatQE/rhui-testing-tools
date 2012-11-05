import re
from rhuilib.expect import Expect, ExpectFailed

class Cds(object):
    """A CDS attributes container"""
    def __init__(self,
            name = None,
            hostname = None,
            description = None,
            cluster = None,
            sync = None,
            repos = [],
            last_sync = None,
            last_heartbeat = None):
        self.name = name
        self.hostname = hostname
        self.description = description
        self.cluster = cluster
        self.sync = sync
        self.repos = repos
        self.last_sync = last_sync
        self.last_heartbeat = last_heartbeat
    def __repr__(self):
        return "Cds(" + \
                "name = %r, " % self.name + \
                "hostname = %r, " % self.hostname + \
                "description = %r, " % self.description + \
                "cluster = %r, " % self.cluster + \
                "sync_schedule = %r, " % self.sync + \
                "repos = %r, " % self.repos + \
                "last_sync = %r, " % self.last_sync + \
                "last_heartbeat = %r)" % self.last_heartbeat
    def __eq__(self, other):
        """ doesn't take care about sync_schedule, last_sync and last_heartbeat"""
        ret = True
        ret &= self.name == other.name
        ret &= self.hostname == other.hostname
        ret &= self.description == other.description
        ret &= self.cluster == other.cluster
        ret &= self.repos == other.repos
        return ret


class PulpAdmin(object):
    """pulp-admin handler"""

    @staticmethod
    def command(connection, arg, username="admin", password="admin"):
        Expect.enter(connection, "pulp-admin -u " + username + " -p " + password + " " + arg)

    @staticmethod
    def cds_list(connection, username="admin", password="admin"):
        """returns the output of pulp-admin cds list; header stripped off"""
        PulpAdmin.command(connection, "cds list", username, password)
        # eats prompt!
        pattern = re.compile(".*cds list\r\n\+-+\+\r\n\s*CDS Instances\s*\r\n\+-+\+(\r\n)+(.*)\[.*@.*\][\$#]", re.DOTALL)
        ret = Expect.match(connection, pattern, grouplist=[2])[0]
        # reset prompt
        Expect.enter(connection, "")
        lines = ret.split("\r\n")
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
                cds = Cds()
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

__all__ = [PulpAdmin, Cds]
