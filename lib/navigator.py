import pxssh
from prompt import Prompt
from command import Command
from screen import Screen
from contextlib import contextmanager

class Navigator(object):
    """Manages a role session"""
    def __init__(self, screen, session):
        self.screen = screen
        self.session = session
    def __repr__(self):
        return "%s(host=%r, user=%r, screen=%r)" % (self.__class__.__name__,
                self.host, self.user, screen)
    def move(self, command):
        if isinstance(command, Command):
            command.send(self.session)
        else:
            self.session.send(str(command))
        self.screen = self.screen.next(command))
    def prompt(self):
        if isinstance (Prompt, self.screen.prompt):
            self.screen.prompt.expect(self.session)
        else:
            # no callbacks required,
            # this justifies the screen switched
            self.expect(self.screen.prompt)
    def navigate(self, command):
        self.move(command)
        self.prompt()
    @contextmanager
    def navigating(self, command)
        self.reset()
        self.move(command)
        yield
        self.prompt()

