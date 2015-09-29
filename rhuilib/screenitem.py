"""
Screen item module
"""

import lineparser
import rhuimanager

class NoSuchItem(ValueError):
    """
    to be risen in case the item can't be located
    """

class ScreenItem(object):
    """
    something that has a line parser
    and is able to locate itself within the lines
    """
    parser = lineparser.Parser(mapping = []) # to be overriden in subclasses

    def __init__(self):
        self.parser = lineparser.Parser(self.mapping)

    def locate(self, lines):
        """
        locate self in the lines while parsing those
        raises NoSuchItem
        returns linenr of the first line the item starts on
        """
        index = 0
        for index, other in self.iter_parse(lines):
            if self == other:
                break
        else:
            raise NoSuchItem("can't locate self in lines given")
        return index

    def selected(self, lines):
        """
        a default implementation of a screen item selection handling
        return True/False, on-screen-index
        """
        index = self.locate(lines)
        # usually, the "selection"--pattern header will preceed the line
        # on which this item was found; subclasses may override
        return rhuimanager.RHUIManager.selected_line(lines[index - 1])

    @classmethod
    def from_parsed_item_pairs(cls, item_pairs):
        """
        a default implementation of the parser--output constructor
        """
        obj = cls()
        for pair in item_pairs:
            setattr(obj, pair[0], pair[1][0]) # second item is a tuple here (re.match groups)
        return obj

    @classmethod
    def parse(cls, lines):
        """
        parse the list of lines returning list of cls instances
        """
        return list(cls.iter_parse(lines))

    @classmethod
    def iter_parse(cls, lines):
        """
        parse the list of lines yielding cls instance a time
        lines as shown in list of cds on the rhui screen
        """
        for linenr, pairs in cls.parser.parse(lines):
            # map the pairs onto cls
            yield linenr, cls.from_parsed_item_pairs(pairs)

