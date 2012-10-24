from cds_manager import CdsManager

class QuitTwiceError(RuntimeError):
	pass

class RhuiManager(object):
    def __init__(self, session=None, screen=None):
        self._quit = False
        session.sendline("rhui-manager")
        session.expect("=> ")
        self.screen = screen
        self.cds = CdsManager(session=session, screen=screen)
    def quit(self):
        if not self._quit:
            self.session.sendline("q")
            self._quit = True
        else:
            raise QuitTwiceError("Can't quit twice")
