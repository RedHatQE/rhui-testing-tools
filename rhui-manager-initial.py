import rhuilib
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

rs = rhuilib.RHUIsetup()
rs.setupFromRolesfile()
rs.RHUA.enter("rhui-manager")
rs.RHUA.expect("Full path to the new signing CA certificate:")
rs.RHUA.enter("/etc/rhui/pem/ca.crt")
rs.RHUA.expect("Full path to the new signing CA certificate private key:")
rs.RHUA.enter("/etc/rhui/pem/ca.key")
rs.RHUA.expect("regenerated using rhui-manager.*:")
rs.RHUA.enter("")
rs.RHUA.expect("Enter pass phrase for.*:")
rs.RHUA.enter(rs.RHUA.getCaPassword())
rs.RHUA.expect("RHUI Username:")
rs.RHUA.enter("admin")
rs.RHUA.expect("RHUI Password:")
rs.RHUA.enter("admin")
rs.RHUA.expect("rhui \(home\) =>")
rs.RHUA.enter("q")
