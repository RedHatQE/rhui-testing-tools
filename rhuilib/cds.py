
class Cds(object):
    """A CDS attributes container"""
    def __init__(self,
            name = None,
            hostname = None,
            description = None,
            cluster = None,
            repos = []):
        self.name = name
        self.hostname = hostname
        self.description = description
        self.cluster = cluster
        self.repos = repos
    def __repr__(self):
        return "Cds(" + \
                "name = %r, " % self.name + \
                "hostname = %r, " % self.hostname + \
                "description = %r, " % self.description + \
                "cluster = %r, " % self.cluster + \
                "repos = %r)" % self.repos
    def __eq__(self, other):
        ret = True
        ret &= self.name == other.name
        ret &= self.hostname == other.hostname
        ret &= self.description == other.description
        ret &= self.cluster == other.cluster
        ret &= self.repos == other.repos
        return ret
    def __cmp__(self , other):
        """for comparison of sorted lists to work as expected"""
        if self == other:
            return 0
        # hack that in other cases
        return cmp(repr(self), repr(other))


class RhuiCds(Cds):
    """A Cds the way RHUI tracks it"""
    def __init__(self,
            name = None,
            hostname = None,
            client_hostname = None,
            description = 'RHUI CDS',
            cluster = None,
            repos = []):
        # by default RHUI assigns all names to hostnames; simulating the same
        if client_hostname is None:
            client_hostname = hostname
        if name is None:
            name = hostname
        Cds.__init__(self,name,hostname,description,cluster,repos)
        self.client_hostname = client_hostname
        def __eq__(self, other):
            ret = Cds.__eq__(self, other)
            if isinstance(other, RhuiCds):
                ret &= self.client_hostname == other.client_hostname
            return ret
        def __repr__(self):
            return "Rhui" + Cds.__repr__(self).strip(')') + \
                    ", client_hostname = %r)" % self.client_hostname

class PulpCds(Cds):
    """A Cds the way Pulp tracks it"""
    def __init__(self,
            name = None,
            hostname = None,
            description = None,
            cluster = None,
            repos = [],
            sync_schedule = None,
            last_sync = None,
            last_heartbeat = None):
        Cds.__init__(self, name, hostname, description, cluster, repos)
        self.sync_schedule = sync_schedule
        self.last_sync = last_sync
        self.last_heartbeat = last_heartbeat
    def __eq__(self, other):
        ret = Cds.__eq__(self, other)
        if isinstance(other, PulpCds):
            ret &= self.sync_schedule == other.sync_schedule
            ret &= self.last_sync == other.last_sync
            ret &= self.last_heartbeat == other.last_heartbeat
        return ret
    def __repr__(self):
        return "Pulp" + Cds.__repr__(self).strip(")") + \
                ", sync_schedule = %r, " % self.sync_schedule + \
                "last_sync = %r, " % self.last_sync + \
                "last_heartbeat = %r)" % self.last_heartbeat

