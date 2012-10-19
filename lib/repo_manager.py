from rhui_navigator import MenuItemNotFoundError, multi_selection_prompt, confirm_prompt,
     RhuiNavigator

class RepoManager(RhuiNavigator):
    def reset(self):
        RhuiNavigator.reset(self)
        self.navigate('r')
    def info(self, repos):
        with self.navigating('i'):
            self.select_multimenu_items(repos)

