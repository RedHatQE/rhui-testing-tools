import paramiko


class Connection():
    '''
    Stateful object to represent paramiko connection to the host
    '''
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

    def exec_command(self, command, bufsize=-1):
        '''
        execute a command in the connection
        @param command:  a string command to execute
        @param bufsize:  paramiko bufsize option
        @return (stdin, stdout, stderr)
        '''
        return self.cli.exec_command(command, bufsize)
