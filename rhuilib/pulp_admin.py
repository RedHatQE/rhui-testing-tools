
import re
from rhuilib.expect import Expect, ExpectFailed

class PulpAdmin(object):
    """pulp-admin handler"""
    def __init__(self, connection, username="admin", password="admin"):
        self.connection = connection
        self.username = username
        self.password = password
    def command(self, *args):
        return "pulp-admin -u %s -p %s " % (self.username, self.password) + \
            " ".join([str(x) for x in args])
    def cds_list(self):
        """returns the output of pulp-admin cds list; header stripped off"""
        cmd = self.command("cds", "list")
        Expect.enter(self.connection, cmd)
        # eats prompt!
        pattern = re.compile(".*%s\r\n" % cmd +
                "\+-+\+\r\n\s*CDS Instances\s*\r\n\+-+\+(\r\n)+(.*)\[.*@.*\][\$#]",
                re.DOTALL)
        ret = Expect.match(self.connection, pattern, grouplist=[2])[0]
        # reset prompt
        Expect.enter(self.connection, "")
        return ret
