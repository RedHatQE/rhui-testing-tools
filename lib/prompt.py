import yaml
from yaml import YAMLObject

class Prompt(YAMLObject):
    actions=[]
    yaml_tag = u'!Prompt'
    def __init__(self, actions=[]):
        self.actions = actions
    def __repr__(self):
        return "Prompt(.actions=%r)" % self.actions
    def add_pattern_callback(self, pattern, callback):
        self.actions.append((pattern, callback))
    def expect(self, session):
        index = session.expect([pattern for pattern, callback in self.actions])
        # fire the callback
        self.actions[index][1]()
