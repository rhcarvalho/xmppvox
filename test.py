# -*- coding: utf-8 -*-
import unittest
import socket
import sys
from server import recv, recvall, accept, SYSTEM_ENCODING

# Necessário para corrigir bug no unittest.
# A versão da biblioteca presente no Python 2.7
# tem problemas em comparar strings unicode.
if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding(SYSTEM_ENCODING)


class SocketMock(object):
    def __init__(self, recv_size=sys.maxint):
        self.recv_size = recv_size
    
    def recv(self, size):
        return "*" * min(self.recv_size, size)


class TestRecv(unittest.TestCase):
    def test_exact_amount(self):
        sock = SocketMock()
        self.assertEqual(len(recv(sock, 23)), 23)
    
    def test_less_data(self):
        sock = SocketMock(recv_size=2)
        self.assertEqual(len(recv(sock, 23)), 2)
    
    def test_nothing_is_an_error(self):
        sock = SocketMock(recv_size=0)
        self.assertRaises(socket.error, recv, sock, 23)
    
    def test_nothing_is_not_an_error_when_asked_for_nothing(self):
        sock = SocketMock(recv_size=0)
        self.assertEqual(len(recv(sock, 0)), 0)
    
    def test_no_more_than_asked(self):
        sock = SocketMock(recv_size=42)
        self.assertEqual(len(recv(sock, 23)), 23)


class TestRecvAll(unittest.TestCase):
    def test_single_try(self):
        sock = SocketMock()
        self.assertEqual(len(recvall(sock, 23)), 23)
    
    def test_multiple_tries(self):
        sock = SocketMock(recv_size=2)
        self.assertEqual(len(recvall(sock, 23)), 23)
    
    def test_can_ask_for_nothing(self):
        sock = SocketMock(recv_size=2)
        self.assertEqual(len(recvall(sock, 0)), 0)
    
    def test_nothing_is_an_error(self):
        sock = SocketMock(recv_size=0)
        self.assertRaises(socket.error, recvall, sock, 23)
    
    def test_nothing_is_not_an_error_when_asked_for_nothing(self):
        sock = SocketMock(recv_size=0)
        self.assertEqual(len(recvall(sock, 0)), 0)
    
    def test_no_more_than_asked(self):
        sock = SocketMock(recv_size=42)
        self.assertEqual(len(recvall(sock, 23)), 23)


class PapovoxSocketMock(object):
    def __init__(self, addr, nickname):
        self.conn = self
        self.addr = addr
        self.nickname = nickname
        self.__stage = 0
    
    def accept(self):
        return self.conn, self.addr
    
    def sendall(self, data):
        if data.startswith('+OK'):
            self.__stage += 1
        elif self.__stage == 2:
            pass
        else:
            raise socket.error
    
    def recv(self, size):
        if self.__stage == 1:
            return self.nickname + "\r\n"
        raise socket.error

class TestAccept(unittest.TestCase):
    addr = ('127.9.9.9', 9999)
    
    def test_basic(self):
        nickname = u"Olavo".encode(SYSTEM_ENCODING)
        s = PapovoxSocketMock(self.addr, nickname)
        self.assertEqual(accept(s), (s, self.addr, nickname))
    
    def test_nickname_with_accents(self):
        nickname = u"Anônimo".encode(SYSTEM_ENCODING)
        s = PapovoxSocketMock(self.addr, nickname)
        #accept(s)
        self.assertEqual(accept(s), (s, self.addr, nickname))


if __name__ == '__main__':
    unittest.main()