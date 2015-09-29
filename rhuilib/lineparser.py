"""
generic list parser
"""

class Parser(object):

    def __init__(self, mapping=[]):
        self.mapping = mapping
        self.pairs = []
        self.index = 0
        self.linenr = 0

    def parse(self, lines=[]):
        """
        parse the list of lines yielding mapping pairs a time
        lines as shown in list of items on some rhui screen
        mapping is a list of tuples:
            [
                (<your_key>, re.pattern()),
                ...
            ]
        such as:
            [
                ('host_name', re.compile("^  Hostname:\s*(.*)$")),
                ('user_name', re.compile("^  SSH Username:\s*(.*)$")),
                ('ssh_key_path', re.compile("^  SSH Private Key:\s*(.*)$"))
            ]
        if applied on a list of lines gives a generator of items as follows:
            ...
            (line_nr, [
                ('host_name', ('cds01.example.com',)),
                ('user_name', ('ec2-user',)),
                ('ssh_key_path', ('/root/.ssh/id_rsa_rhua',)),
            ])
            ...
        where line_nr is the line number on which the item starts
        """
        self.linenr = 0
        self.index = 0
        self.pairs = []
        for line in lines:
            self.linenr += 1
            name, pattern = self.mapping[self.index]
            match = pattern.match(line)

            if match is None:
                if self.index == 0:
                    # lines not matching while "outside" an item are OK
                    continue
                else:
                    # but lines that don't match while processing an item are input error
                    raise ValueError("%s doesn't match %s at line #%s" (pattern, line, self.linenr))

            # add matching name--value pair and shift mapping index
            self.pairs.append((name, match.groups()))
            self.index = (self.index + 1) % len(self.mapping)

            if self.index == 0:
                # new item starts next iteration
                yield self.linenr - len(self.mapping), self.pairs
                pairs = []

        def copy(self, prefix=[], suffix=[]):
            return type(self)(mapping=prefix + self.mapping + suffix)
