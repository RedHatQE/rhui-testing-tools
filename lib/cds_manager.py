from rhui_navigator import MenuItemNotFoundError, multi_selection_prompt, confirm_prompt, RhuiNavigator

class CdsManager(RhuiNavigator):
    def reset(self):
        if self.screen.name != 'cds':
            RhuiNavigator.reset(self)
            self.navigate('c')
    def info(self, cluster, cds):
        with self.navigating('i'):
            self.select_multimenu_items([cluster])
            self.select_multimenu_items(cds)
        return self.session.beforematch
    def add(self, cluster, display_name, client_name, host_name):
        with self.navigating('a'):
            self.expect("Hostname of the CDS to register:\r\n")
            self.sendline(host_name)
            self.expect("Client hostname.*:\r\n")
            self.sendline(client_name)
            self.sendline("Display name.*:\r\n")
            self.sendline(display_name)
            self.select_cluster(cluster)
    def delete(self, cluster, cdses, force=False):
        """Use force only if you know the CDSes will fail to remove ;)"""
        with self.navigating('d'):
            self.select_menu_item(cluster)
            self.select_multimenu_items(cdses)
            if force:
                self.proceed(question="Forcibly remove these CDS instances\?")
    def move(self, cluster, cdses):
        with self.navigating('m'):
            self.select_multimenu_items(cdses)
            self.select_cluster(cluster)
    def _associate_switch(self, cluster, repos, switch='s'):
        with self.navigating(switch):
            self.select_cluster(cluster, OK=False)
            self.select_multimenu_items(repolist)
            self.proceed()
    def associate(self, cluster, repos):
        self._associate_switch(cluster, repos, switch='s')
    def unassociate(self, cluster, repos):
        self._associate_switch(cluster, repos, switch='u')
