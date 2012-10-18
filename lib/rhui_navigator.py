from navigator import Navigator
from screen import ScreenLeaf
from command import Command
from prompt import Prompt
from contextlib import contextmanager
import re
import pexpect

multi_selection_prompt = "Enter value (\d*) to toggle selection, 'c' to confirm selections, or '?' for more commands: "
confirm_prompt = ".*confirm: "

class MenuItemNotFoundError(RuntimeError)
    """In cases expect didn't find the requested menu item"""

class RhuiNavigator(Navigator):
    def __init__(self, host, user, screens= './conf/Screens-nested.yaml'):
        import yaml
        with open(self.screens_config) as fd:
            Navigator.__init__(self, host,  user, yaml.load(fd))
        self.rhua = host
        self.user = user
    def get_menu_item(self, items):
        self.expect(["^.*([\d])*: *%s" % (item, multi_selection_prompt), pexpect.TIMEOUT])
        if self.session.match is None:
            raise MenuItemNotFoundError("menu item: %s not offered" % item)
        return self.session.match.groups()[1]
    def select_multimenu_items(self, items):
        """MIND the ORDER of ITEMS"""
        for item in items:
            menu_item = self.get_menu_item(item)
            self.expect(multi_selection_prompt)
            self.sendline(menu_item)
        self.expect(multi_selection_prompt)
        self.sendline("c")
    def select_menu_item(self, item):
        menu_item = self.get_menu_item(item)
        self.sendline(menu_item)
        self.expect(confirm_prompt)
        self.sendline("c")
    def reset(self):
        self.navigate('^')
    def self(quit):
        self.reset()
        self.sendline('q')
