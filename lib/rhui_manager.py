import yaml
from yaml import YAMLObject
class NextScreenError(Exception):
    """Next state not found exception"""

class Screen(YAMLObject):
    yaml_tag = u'!Screen'
    screen_map = None
    prompt = None
    name = None
    def __init__(self, name=None, screen_map=None, prompt=None):
        self.name = name
        if screen_map is not None:
            self.screen_map = screen_map
        else:
            self.screen_map = {}
        self.prompt = prompt
    def next(self, command):
        try:
            return self.screen_map[command]
        except KeyError:
            raise NextScreenError("No next screen found for command: %r" %
                    command)
    def __repr__(self):
        return "Screen(name=%r, screen_map=%r, prompt=%r)" % (self.name,
                self.screen_map, self.prompt)



if __name__ == '__main__':
    home_screen = Screen(name='home', prompt='.*rhui (home) => ')
    cds_screen = Screen(name='cds', prompt='.*rhui (cds) => ')
    repo_screen = Screen(name='repo', prompt='.*rhui (repo) => ')
    sync_screen = Screen(name='sync', prompt='.*rhui (sync) => ')
    ent_screen = Screen(name='ent', prompt='.*rhui (ent) => ')
    rhn_screen = Screen(name='rhn', prompt='.*rhui (rhn) => ')
    usr_screen = Screen(name='usr', prompt='.*rhui (usr) => ')
    id_screen = Screen(name='id', prompt='.*rhui (id) => ')
    home_screen.add_screen(repo_screen, 'r')
    home_screen.add_screen(cds_screen, 'c')
    home_screen.add_screen(sync_screen, 's')
    home_screen.add_screen(ent_screen, 'e')
    home_screen.add_screen(rhn_screen, 'n')
    home_screen.add_screen(usr_screen, 'u')
    home_screen.add_screen(id_screen, 'i')
    print home_screen
    print home_screen.next('i')
