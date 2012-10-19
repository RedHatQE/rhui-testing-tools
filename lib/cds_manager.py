from rhui_navigator import MenuItemNotFoundError, multi_selection_prompt, confirm_prompt,
     RhuiNavigator

class CdsManager(RhuiNavigator):
    def reset(self):
        RhuiNavigator.reset(self)
        self.navigate('c')
    def list(self):
        """does nothing, just dumps the cds list screen contents"""
        self.reset()
        self.navigate('l')
        return self.session.beforematch
    def info(self, cluster, cds):
        self.reset()
        with self.navigating('i'):
            self.select_multimenu_items([cluster])
            self.select_multimenu_items(cds)
        return self.session.beforematch
    def add(self, cluster, display_name, client_name, host_name):
        self.reset()
        with self.navigating('r'):
            self.expect("Hostname of the CDS to register:\n")
            self.sendline(host_name)
            self.expect("Client hostname.*:\n")
            self.sendline(client_name)
            self.sendline("Display name.*:\n")
            self.sendline(display_name)
            self.select_cluster(cluster)
    def del(self, cluster, cdses, force=False):
        """Use force only if you know the CDSes will fail to remove ;)"""
        self.reset()
        with self.navigating('d'):
            self.select_menu_item(cluster)
            self.select_multimenu_items(cdses)
            if force:
                self.proceed(question="Forcibly remove these CDS instances\?")
    def move(self, cluster, cdses):
        self.reset()
        with self.navigating('m'):
            self.select_multimenu_items(cdses)
            self.select_cluster(cluster)
    def associate(self, cluster, repo):
        self.reset()
        with self.navigating('s'):
            self.select_cluster(cluster, OK=False)
