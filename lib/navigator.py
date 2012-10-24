import pxssh
from prompt import Prompt
from command import Command
from screen import Screen
from contextlib import contextmanager

class Navigator(object):
    """Manages a role session"""
    def __init__(self, screen=None, session=None):
        self.screen = screen
        self.session = session
        self.reset()
    def __repr__(self):
        return "%s(host=%r, user=%r, screen=%r)" % (self.__class__.__name__,
                self.host, self.user, screen)
    def step(self, command):
        if isinstance(command, Command):
            command.send(self.session)
        else:
            self.sendline(str(command))
        self.screen = self.screen.next(command)
    def prompt(self):
        if isinstance (self.screen.prompt, Prompt):
            self.screen.prompt.expect(self.session)
        else:
            # no callbacks required,
            # this justifies the screen switched
            self.expect(self.screen.prompt)
    def navigate(self, command):
        self.step(command)
        self.prompt()
    @contextmanager
    def navigating(self, command):
        self.reset()
        self.step(command)
        yield
        self.prompt()
    def sendline(self, *args, **kvargs):
        return self.session.sendline(*args, **kvargs)
    def expect(self, *args, **kvargs):
        return self.session.expect(*args, **kvargs)
    def send(self, *args, **kvargs):
        return self.session.send(*args, **kvargs)
    def reset(self):
        pass

