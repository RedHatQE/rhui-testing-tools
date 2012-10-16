from zope.interface import Interface


class IConfiguredObject(Interface):
    """I provide the attribute_names attribute; the first item of which is
    name
    """


class ConfiguredObjectParser(object):
    """reads object attributes from a ini-like config made up of just one kind
    of sections. The name attribute is always assumed.
    """
    def __init__(self, object_type):
        """object_type: type to instantiate for each section read. The instance
        is assumed to have a attribute_names attribute. The very
        first attribute is considered the section name"""
        from ConfigParser import ConfigParser
        #if not IConfiguredObject.implementedBy(object_type):
        #   raise TypeError("Seems %r doesn't implement the interface IConfiguredObject" % object_type)
        self.object_type = object_type
        self.config = ConfigParser(allow_no_value=True)

    def add(self, other):
        section_name = str(getattr(other, other.attribute_names[0]))
        if not self.config.has_section(section_name):
            self.config.add_section(section_name)
        for attribute_name in other.attribute_names[1:]:
            self.config.set(section_name, attribute_name, getattr(other, attribute_name))

    @property
    def objects(self):
        from ConfigParser import NoOptionError
        for section_name in self.config.sections():
            obj = self.object_type()
            setattr(obj, obj.attribute_names[0], section_name)
            for attribute_name in obj.attribute_names[1:]:
                try:
                    setattr(obj, attribute_name, self.config.get(section_name, attribute_name))
                except NoOptionError:
                    setattr(obj, attribute_name, None)
            yield obj

    @objects.setter
    def objects(self, other):
        for obj in other:
            self.add(obj)

    def remove(self, other):
        return self.config.remove_section(other.attribute_names[0])

    def read(self, config_path):
        self.config.read(config_path)

    def readfp(self, config_fp):
        self.config.readfp(config_fp)

    def write(self, file_object):
        self.config.write(file_object)

class ConfigMash(object):
    path='./conf'
    def __init__(self, types=[]):
        self.map = {}
        self.types = types
        for t in types:
            cop = ConfiguredObjectParser(t)
            self.map[t.__name__] = {}
            cop.read("%s/%ss.cfg" % (self.path, t.__name__))
            for obj in cop.objects:
                self.add(obj)
    def __repr__(self):
        return "ConfigMash(types=%r).map=%r" % (self.map.keys(), self.map)
    def add(self, obj):
        self.map[type(obj).__name__][obj.name] = obj
        try:
            for t in self.types:
                others = self.map[t.__name__]
                for other in others.values():
                    if hasattr(other, type(obj).__name__):
                        if getattr(other, type(obj).__name__) == obj.name:
                            setattr(other, type(obj).__name__, obj)
        except KeyError:
            pass
    def all(self, type_object):
        return self.map[type_object.__name__].values()


if __name__ == '__main__':
    from host import Host
    from role import Role
    cfg = ConfigMash([Role, Host])
    print cfg.map['Role']['rhua']
    print cfg.all(Role)
