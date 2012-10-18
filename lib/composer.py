
import yaml

from yaml.error import MarkedYAMLError
from yaml.events import *
from yaml.nodes import *

from yaml.composer import ComposerError

class Composer (yaml.composer.Composer):
    def compose_node(self, parent, index):
        if self.check_event(AliasEvent):
            event = self.get_event()
            anchor = event.anchor
            if anchor not in self.anchors:
                self.anchors[anchor] = ScalarNode(u'tag:yaml.org,2002:str', '__None__', None, None, None)
            return self.anchors[anchor]
        event = self.peek_event()
        try:
            anchor = event.anchor
            if anchor is not None:
                if anchor in self.anchors:
                    self.anchors[anchor] = event
                    print "OooOops %r " % event
        except AttributeError:
            anchor = None
        self.descend_resolver(parent, index)
        if self.check_event(ScalarEvent):
            node = self.compose_scalar_node(anchor)
        elif self.check_event(SequenceStartEvent):
            node = self.compose_sequence_node(anchor)
        elif self.check_event(MappingStartEvent):
            node = self.compose_mapping_node(anchor)
        self.ascend_resolver()
        return node
