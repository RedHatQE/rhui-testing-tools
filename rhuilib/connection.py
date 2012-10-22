import paramiko


class Connection():
    def __init__(self, hostname, username="root", key_filename=None):
        self.hostname = hostname
        self.username = username
        self.key_filename = key_filename
        self.cli = paramiko.SSHClient()
        self.cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.cli.connect(hostname=hostname, username=username, key_filename=key_filename)
        self.channel = self.cli.invoke_shell()
        self.sftp = self.cli.open_sftp()
        self.channel.setblocking(0)
