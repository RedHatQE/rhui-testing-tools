from rhui_navigator import MenuItemNotFoundError, multi_selection_prompt, confirm_prompt,
     RhuiNavigator

class CdsManager(RhuiNavigator):
    def reset(self):
        RhuiNavigator.reset(self)
        self.navigate('c')
    def list_cdses(self):
        """does nothing, just dumps the cds list screen contents"""
        self.reset()
        self.navigate('l')
        return self.session.beforematch
    def info_cds(self, cluster, cds):
        self.reset()
        with self.navigating('i'):
            self.select_multimenu_items([cluster])
            self.select_multimenu_items(cds)
        return self.session.beforematch
    def add_cds(self, cluster, display_name, client_name, host_name):
        self.reset()
        with self.navigating('r'):
            self.expect("Hostname of the CDS to register:\n")
            self.sendline(host_name)
            self.expect("Client hostname.*:\n")
            self.sendline(client_name)
            self.sendline("Display name.*:\n")
            self.sendline(display_name)
            try:
                menu_item = self.get_menu_item(cluster)
                self.sendline(menuitem)
            except MenuItemNotFoundError:
                self.sendline("0")
                self.expect('Enter a CDS cluster name:\n')
                self.sendline(cluster)
            finally:
                self.expect(confirm_prompt)
                self.sendline(c)
    def del_cdses(self, cluster, cdses):
        self.reset()
        with self.navigating('d'):
            self.select_menu_item(cluster)
            self.select_multimenu_items(cdses)
