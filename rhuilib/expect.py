import re
import time
import logging
import socket


class ExpectFailed(Exception):
    '''
    Exception to represent expectation error
    '''
    pass


class Expect():
    '''
    Class to do expect-ike stuff over paramiko connection
    '''
    @staticmethod
    def expect_list(connection, regexp_list, timeout=5):
        '''
        Expect a list of expressions

        @param connection: paramiko connection
        @param regexp_list: list of tuples (regexp, return value)
        @param timeout: timeout (default to 5)
        '''
        result = ""
        count = 0
        while count < timeout:
            try:
                recv_part = connection.channel.recv(16384)
                logging.debug("RCV: " + recv_part)
                result += recv_part
            except socket.timeout:
                # socket.timeout here means 'no more data'
                pass

            for (regexp, retvalue) in regexp_list:
                # search for the first matching regexp and return desired value
                if re.match(regexp, result):
                    return retvalue
            time.sleep(1)
            count += 1
        raise ExpectFailed()

    @staticmethod
    def expect(connection, strexp, timeout=5):
        '''
        Expect one expression

        @param connection: paramiko connection
        @param strexp: string to convert to expression (.*string.*)
        @param timeout: timeout (default to 5)
        '''
        return Expect.expect_list(connection, [(re.compile(".*" + strexp + ".*", re.DOTALL), True)], timeout)

    @staticmethod
    def match(connection, regexp, grouplist=[1], timeout=5):
        '''
        Match against an expression

        @param connection: paramiko connection
        @param regexp: compiled regular expression
        @param grouplist: list of groups to return (defaults to [1])
        @param timeout: timeout (default to 5)

        '''
        result = ""
        count = 0
        while count < timeout:
            try:
                recv_part = connection.channel.recv(16384)
                logging.debug("RCV: " + recv_part)
                result += recv_part
            except socket.timeout:
                # socket.timeout here means 'no more data'
                pass

            match = regexp.match(result)
            if match:
                ret_list = []
                for group in grouplist:
                    logging.debug("matched: " + match.group(group))
                    ret_list.append(match.group(group))
                return ret_list
            time.sleep(1)
            count += 1
        raise ExpectFailed()

    @staticmethod
    def enter(connection, command):
        '''
        Enter a command to the channel (with '\n' appended)
        '''
        return connection.channel.send(command + "\n")
