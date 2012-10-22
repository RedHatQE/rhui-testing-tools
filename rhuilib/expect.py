import re
import time
import logging
import socket


class ExpectFailed(Exception):
    pass


class Expect():
    @staticmethod
    def expect_list(connection, regexp_list, timeout=5):
        result = ""
        count = 0
        while count < timeout:
            try:
                recv_part = connection.channel.recv(16384)
                logging.debug("RCV: " + recv_part)
                result += recv_part
            except socket.timeout:
                pass

            for (regexp, retvalue) in regexp_list:
                if re.match(regexp, result):
                    return retvalue
            time.sleep(1)
            count += 1
        raise ExpectFailed()

    @staticmethod
    def expect(connection, strexp, timeout=5):
        return Expect.expect_list(connection, [(re.compile(".*" + strexp + ".*", re.DOTALL), True)], timeout)

    @staticmethod
    def match(connection, regexp, grouplist=[1], timeout=5):
        result = ""
        count = 0
        while count < timeout:
            try:
                recv_part = connection.channel.recv(16384)
                logging.debug("RCV: " + recv_part)
                result += recv_part
            except socket.timeout:
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
        return connection.channel.send(command + "\n")
