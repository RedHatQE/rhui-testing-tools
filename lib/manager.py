import pxssh
from prompt import Prompt
from command import Command
from screen import Screen

class Manager(object):
    """Manages a role session"""
    def __init__(self, host, user, screen, logfile=None, timeout=30):
        self.user = user
        self.host = host
        self.screens = [screen]
        self.session = pxssh.pxssh(logfile=logfile, timeout=timeout)
        self.session.login(self.host, self.user)
        self.session.prompt()
    def __repr__(self):
        return "Manager(host=%r, user=%r, screen=%r)" % (self.host, self.user,
                screen)
    def navigate(self, command=None):
        self.push(self.screen.next(command))
        if isinstance(command, Command):
            command.send(self.session)
        else:
            self.session.send(str(command))
        if isinstance (Prompt, screen.prompt):
            self.screen.prompt.expect(self.session)
        else:
            # no callbacks required,
            # this justifies the screen switched
            self.expect(self.screen.prompt)
        self.pop()
    def push(self, screen):
        self.screens.append(screen)
    def pop(self):
        self.screens.pop()
    @property
    def screen(self):
        """last screen"""
        return self.screens[-1]

