import re
from rhuilib.expect import Expect, ExpectFailed


class PulpAdmin(object):
    """pulp-admin handler"""

    @staticmethod
    def command(connection, arg, username="admin", password="admin"):
        Expect.enter(connection, "pulp-admin -u " + username + " -p " + password + " " + arg)

    @staticmethod
    def cds_list(connection, username="admin", password="admin"):
        """returns the output of pulp-admin cds list; header stripped off"""
        PulpAdmin.command(connection, "cds list", username, password)
        # eats prompt!
        pattern = re.compile(".*cds list\r\n\+-+\+\r\n\s*CDS Instances\s*\r\n\+-+\+(\r\n)+(.*)\[.*@.*\][\$#]", re.DOTALL)
        ret = Expect.match(connection, pattern, grouplist=[2])[0]
        # reset prompt

        reslist = ret.split("\r\n")
        i = 0
        cdslist = []
        cds = {}
        while i < len(reslist):
            line = reslist[i]
            if line[0:5] == 'Name ':
            # New cds found
                if cds != {}:
                    # Appending previous cds
                    cdslist.append(cds)
                cds['Name'] = line.split('\t')[1].strip()
            elif line[0:9] == 'Hostname ':
                cds['Hostname'] = line.split('\t')[1].strip()
            elif line[0:8] == 'Cluster ':
                cds['Cluster'] = line.split('\t')[1].strip()
            elif line[0:6] == 'Repos ':
                cds['Repos'] = line.split('\t')[1].strip()
            elif line.strip() == "Status:":
                # The real status is in the next line
                cds['Status'] = reslist[i + 1].split('\t')[1].strip()
            i += 1

        if cds != {}:
            # Appending last cds
            cdslist.append(cds)

        Expect.enter(connection, "")
        return cdslist
