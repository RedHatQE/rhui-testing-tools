import yaml
from yaml import YAMLObject

class Command(YAMLObject):
    yaml_tag = u'!Command'
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return "Command(%r)" % self.value
    def send(self, session):
        session.send(str(self.value))
    def __hash__(self):
        return hash(repr(self))
    def __str__(self):
        return str(self.value)

class ControlCommand(Command):
    yaml_tag = u'!ControlCommand'
    def send(self, session):
        session.sendcontrol(str(self.value)[0])

