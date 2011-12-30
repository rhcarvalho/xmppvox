import unittest
import socket
import sys
from papovox_server import recv, recvall


class SocketMock(object):
    def __init__(self, recv_size=sys.maxint):
        self.recv_size = recv_size
    
    def recv(self, size):
        return "*" * min(self.recv_size, size)


class TestRecv(unittest.TestCase):
    def test_recv_exact_amount(self):
        sock = SocketMock()
        self.assertEqual(len(recv(sock, 23)), 23)
    
    def test_recv_less_data(self):
        sock = SocketMock(recv_size=2)
        self.assertEqual(len(recv(sock, 23)), 2)
    
    def test_recv_nothing_is_an_error(self):
        sock = SocketMock(recv_size=0)
        self.assertRaises(socket.error, recv, sock, 23)
    
    def test_recv_nothing_is_not_an_error_when_asked_for_nothing(self):
        sock = SocketMock()
        self.assertEqual(len(recv(sock, 0)), 0)


class TestRecvAll(unittest.TestCase):
    def test_recvall_single_try(self):
        sock = SocketMock()
        self.assertEqual(len(recvall(sock, 23)), 23)
    
    def test_recvall_multiple_tries(self):
        sock = SocketMock(recv_size=2)
        self.assertEqual(len(recvall(sock, 23)), 23)
    
    def test_recvall_can_ask_for_nothing(self):
        sock = SocketMock(recv_size=2)
        self.assertEqual(len(recvall(sock, 0)), 0)


if __name__ == '__main__':
    unittest.main()