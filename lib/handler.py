class Handler(object):
    expressions = ".*"
    def call_back(self, index):
        print index
    def __repr__(self):
        return "Handler(%r)" % self.expressions
