from zope.interface import implements
from config import IConfiguredObject


class Host(object):
    implements(IConfiguredObject)
    attribute_names = ['name', 'key', 'user']
    name = None
    key = None
    user = None

    def __init__(self, name=None, key=None, user=None):
        self.name = name
        self.key = key
        self.user = user

    def __repr__(self):
        return "Host(name=%r, key=%r, user=%r)" % (self.name, self.key, self.user)


class HostsConfigParser(object):
    config_path = "./conf/hosts.cfg"

    def __init__(self):
        from config import ConfiguredObjectParser as COP
        self.aCop = COP(Host)
        self.aCop.read(self.config_path)

    @property
    def hosts(self):
        return self.aCop.objects

    @hosts.setter
    def hosts(self, other):
        self.aCop.objects = other

    def __del__(self):
        with open(self.config_path, 'wb') as hosts_file:
            self.aCop.write(hosts_file)


if __name__ == '__main__':
    hcp = HostsConfigParser()
    for host in hcp.hosts:
        print host
