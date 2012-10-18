from manager import Manager
from screen import ScreenLeaf

class CdsInfoScreen(ScreenLeaf):
    yaml_tag=u'!CdsInfoScreen'
    def __init__(self, parent):
        ScreenLeaf.__init__(self, parent=parent, name="cds_info")
        from prompt import Prompt
        self.prompt = Prompt(actions=
    def _menu_item_callback(self):


class RhuiManager(Manager):
    screens_config = './conf/Screens-nested.yaml'
    def __init__(self, rhua):
        import yaml
        with open(self.screens_config) as fd:
            Manager.__init__(self, rhua.host.name, rhua.host.user, yaml.load(fd))
        self.rhua = rhua
    def __repr__(self):
        return "RhuiManager(%r)" % self.rhua
    def list_cdses(self):
        """does nothing, just dumps the cds list screen contents"""
        self.navigate('^')
        self.navigate('c')
        self.navigate('l')
    def info_cds(self, cds):
        self.navigate('^')
        self.navigate('c')
        self.navigate('i')
#        self.session.expect(
