from twisted.python import log

class PrematureEOFError(RuntimeError):
    """EOF received while still some handlers stacked"""

class Keeper(object):
    """ Twisted reactor--pexpect adapter with stacked session handlers"""
    handlers = []
    err_back = None
    call_back = None
    def __init__(self, session, handlers=[], err_back=None, call_back=None):
        self.session = session
        self.err_back = err_back
        self.call_back = call_back
        for handler in handlers:
            self.push(handler)
        self.engage()

    def __repr__(self):
        return "Keeper(%r, handlers=%r, err_back=%r, call_back=%r)" % (self.session, self.handlers, self.err_back, call_back)
    def push(self, handler):
        log.msg("pushing %r" % (handler), logLevel=log.logging.DEBUG)
        self.handlers.append(handler)
        handler.keeper = self
    def pop(self):
        return self.handlers.pop()
    def doRead(self):
        handler = self.pop()
        try:
            log.msg("got file event", logLevel=log.logging.DEBUG)
            index = self.session.expect(handler.expressions)
            handler.call_back(index)
            log.msg("before=%r, after=%r" % (self.session.before, self.session.after), logLevel = log.logging.DEBUG)
            self.engage()
        except Exception as e:
            # in case of an error, be it either generic or handler-uncought
            # pexpect.EOF/pexpec.TIMEOUT just bail out
            self.connectionLost(e)
    def logPrefix(self):
        return repr(self)
    def fileno(self):
        return self.session.fileno()
    def connectionLost(self, reason):
            from twisted.python.failure import Failure
            from twisted.internet import reactor, error
            import pexpect
            self.session.close()
            reactor.removeReader(self)
            if  isinstance(reason, pexpect.EOF) or reason.type is error.ConnectionDone:
                # clean close; figure out any handlers left in stack
                if len(self.handlers):
                    # still some handlers left
                    raise PrematureEOFError("%r: got EOF but still some handlers left" % self )
                log.msg("got EOF", logLevel=log.logging.DEBUG)
                if self.call_back:
                    self.call_back()
            else:
                # connection error; handle the session/socket no more
                log.msg("Got %s; bailing out" % (reason), logLevel=log.logging.ERROR)
                if self.err_back:
                    self.err_back(reason)
    def engage(self):
        log.msg("enganging", logLevel=log.logging.DEBUG)
        from twisted.internet import reactor
        reactor.addReader(self)




if __name__ == '__main__':
    from twisted.internet import reactor
    import pexpect, sys
    log.startLogging(sys.stderr, setStdout=False)
    class Handler(object):
        expressions = ['.*']
        keeper = None
        def __init__(self, expressions=['.*']):
            self.expressions = expressions
        def call_back(self, index):
            log.msg("matched: %r" % self.expressions[index])
        def logPrefix(self):
            return repr(self)
        def __repr__(self):
            return 'Handler(%r)' % self.expressions
    h = Handler()

    def err_back(reason):
        log.msg("err_back: %r" % reason)
        reactor.stop()
    def call_back():
        log.msg("call_back: stopping")
        reactor.stop()
    k = Keeper(pexpect.spawn('/bin/bash -c "echo Ahoj"'), [h], err_back=err_back,
            call_back=call_back)
    reactor.run()
