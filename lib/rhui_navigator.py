from navigator import Navigator
from screen import ScreenLeaf
from command import Command
from prompt import Prompt
from contextlib import contextmanager
import re
import pexpect

multi_selection_prompt = "Enter value (\d*) to toggle selection, 'c' to confirm selections, or '?' for more commands: "
confirm_prompt = ".*confirm: "
proceed_prompt = ".*\(y/n\)"
class MenuItemNotFoundError(RuntimeError)
    """In cases expect didn't find the requested menu item"""

class RhuiNavigator(Navigator):
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
    def proceed(self, question=""):
        self.expect(question + proceed_prompt)
        self.sendline('y')
    def reset(self):
        self.navigate('^')
    def self(quit):
        self.reset()
        self.sendline('q')
    def select_cluster(self, cluster, OK=True):
        try:
            menu_item = self.get_menu_item(cluster)
            self.sendline(menuitem)
        except MenuItemNotFoundError as err:
            if not OK:
                raise err
            self.sendline("0")
            self.expect('Enter a CDS cluster name:\n')
            self.sendline(cluster)
        finally:
            self.expect(confirm_prompt)
            self.sendline(c)

