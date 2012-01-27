﻿# -*- coding: utf-8 -*-

#    XMPPVOX: XMPP client for DOSVOX.
#    Copyright (C) 2012  Rodolfo Henrique Carvalho
#
#    This file is part of XMPPVOX.
#
#    XMPPVOX is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

u"""
XMPPVOX - módulo de testes

Este módulo implementa testes automatizados para o XMPPVOX.
"""

import unittest
import socket
import sys

from server import recv, recvall, accept, SYSTEM_ENCODING
from client import BotXMPP


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


class TestClient(unittest.TestCase):
    def setUp(self):
        # Caixa de saída de mensagens Papovox
        self.outbox = []
        # Caixa de entrada de mensagens XMPP
        self.inbox = []

        class FakeServer(object):
            _SOCK = None
            @staticmethod
            def sendmessage(sock, msg):
                self.outbox.append(msg)
        server = FakeServer()

        def message_handler(msg):
            self.inbox.append(msg)

        self.xmpp = BotXMPP('', '', server)
        self.xmpp.message_handler = message_handler

    def test_receive_message(self):
        m = self.xmpp.make_message(mto='nobody', mtype='chat', mbody='testing')
        self.assertEqual(self.inbox, [], u"Caixa de entrada começa vazia")
        # Recebe uma mensagem XMPP
        self.xmpp.message(m)
        self.assertEqual(self.inbox, [m], u"Mensagem recebida")

    def test_send_first_incoming_message_help(self):
        m = self.xmpp.make_message(mfrom='tester',
                                   mto='nobody', mtype='chat', mbody='testing')
        self.assertEqual(len(self.outbox), 0, u"Caixa de saída começa vazia")
        # Recebe uma mensagem XMPP
        self.xmpp.message(m)
        self.assertEqual(len(self.outbox), 1, u"Envia ajuda sobre comando /r")
        self.xmpp.message(m)
        self.assertEqual(len(self.outbox), 1, u"Envia ajuda apenas uma vez")


if __name__ == '__main__':
    unittest.main()