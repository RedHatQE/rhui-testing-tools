from zope.interface import implements
from config import IConfiguredObject


class Role(object):
    implements(IConfiguredObject)
    attribute_names = ['name', 'host']
    name = None
    host = None

    def __init__(self, name=None, host=None):
        self.name = name
        self.host = host

    def __repr__(self):
        return "Role(name=%r, host=%r)" % (self.name, self.host)


class RolesConfigParser(object):
    config_path = "./conf/roles.cfg"

    def __init__(self):
        from config import ConfiguredObjectParser as COP
        self.aCop = COP(Role)
        from host import HostsConfigParser
        self.hosts_config = HostsConfigParser()
        self._sync_hosts()
        self.aCop.read(self.config_path)

    def _sync_hosts(self):
        self._hosts_map = {}
        for host in self.hosts_config.hosts:
            self._hosts_map[host.name] = host

    @property
    def roles(self):
        self._sync_hosts()
        for role in self.aCop.objects:
            # try converting the host name to a real host config object
            role.host = self._hosts_map[role.host]
            yield role

    @roles.setter
    def roles(self, other):
        for obj in other:
            host = obj.host
            self.hosts_config.add(host)
            obj.host = host.name
            self.aCop.add(obj)
            obj.host = host
        self._sync_hosts()

    def __del__(self):
        with open(self.config_path, 'wb') as roles_file:
            self.aCop.write(roles_file)
        del(self.hosts_config)


if __name__ == "__main__":
    rcp = RolesConfigParser()
    for role in rcp.roles:
        print role
