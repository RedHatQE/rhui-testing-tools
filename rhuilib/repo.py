""" Repo container """

class Repo(object):
    """A Repo attributes container"""
    def __init__(self,
        name=None,
        package_count=None
        ):
        self.name = name
        self.package_count = package_count

    def __repr__(self):
        return "Repo(" +\
            "name = %r" % self.name +\
            ", package_count = %r)" % self.package_count

    def __eq__(self, other):
        ret = True
        ret &= self.name == other.name
        ret &= self.package_count == other.package_count
        return ret

    def __str__(self):
        return str(self.name)

    def __cmp__(self, other):
        if self == other:
            return 0
        return cmp(repr(self), repr(other))


class PulpRepo(Repo):
    """a Repo as the Pulp keeps track of it"""
    def __init__(self,
            repoid=None,
            name=None,
            package_count=None,
            url=None
            ):
        Repo.__init__(self,
                name=name,
                package_count=package_count
                )
        self.id = repoid
        self.url = url

    def __eq__(self, other):
        ret = Repo.__eq__(self, other)
        if isinstance(other, PulpRepo):
            ret &= self.id == other.id
            ret &= self.url == other.url
        return ret

    def __repr__(self):
        return "Pulp" + Repo.__repr__(self).strip(')') +\
                ", id = %r" % self.id +\
                ", url = %r)" % self.url
