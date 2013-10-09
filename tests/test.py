# -*- coding: utf-8 -*-

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

# Coloca código-fonte do XMPPVOX no path.
import os.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'xmppvox'))

from server import PapovoxLikeServer, SYSTEM_ENCODING
from client import BotXMPP
import commands


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
    def setUp(self):
        self.s = PapovoxLikeServer()

    def test_exact_amount(self):
        self.s.socket = SocketMock()
        self.assertEqual(len(self.s.recv(23)), 23)

    def test_less_data(self):
        self.s.socket = SocketMock(recv_size=2)
        self.assertEqual(len(self.s.recv(23)), 2)

    def test_nothing_is_an_error(self):
        self.s.socket = SocketMock(recv_size=0)
        self.assertRaises(socket.error, self.s.recv, 23)

    def test_nothing_is_not_an_error_when_asked_for_nothing(self):
        self.s.socket = SocketMock(recv_size=0)
        self.assertEqual(len(self.s.recv(0)), 0)

    def test_no_more_than_asked(self):
        self.s.socket = SocketMock(recv_size=42)
        self.assertEqual(len(self.s.recv(23)), 23)


class TestRecvAll(unittest.TestCase):
    def setUp(self):
        self.s = PapovoxLikeServer()

    def test_single_try(self):
        self.s.socket = SocketMock()
        self.assertEqual(len(self.s.recvall(23)), 23)

    def test_multiple_tries(self):
        self.s.socket = SocketMock(recv_size=2)
        self.assertEqual(len(self.s.recvall(23)), 23)

    def test_can_ask_for_nothing(self):
        self.s.socket = SocketMock(recv_size=2)
        self.assertEqual(len(self.s.recvall(0)), 0)

    def test_nothing_is_an_error(self):
        self.s.socket = SocketMock(recv_size=0)
        self.assertRaises(socket.error, self.s.recvall, 23)

    def test_nothing_is_not_an_error_when_asked_for_nothing(self):
        self.s.socket = SocketMock(recv_size=0)
        self.assertEqual(len(self.s.recvall(0)), 0)

    def test_no_more_than_asked(self):
        self.s.socket = SocketMock(recv_size=42)
        self.assertEqual(len(self.s.recvall(23)), 23)


class PapovoxSocketMock(object):
    def __init__(self, addr, nickname):
        # Socket servidor
        if addr:
            self.client_socket = PapovoxSocketMock(None, nickname)
            self.addr = addr
        # Socket cliente
        else:
            self.nickname = nickname
            self.__stage = 0

    # Socket servidor
    def accept(self):
        return self.client_socket, self.addr

    # Socket cliente
    def sendall(self, data):
        if data.startswith('+OK'):
            self.__stage += 1
        elif self.__stage == 2:
            pass
        else:
            raise socket.error

    # Socket cliente
    def recv(self, size):
        if self.__stage == 1:
            return self.nickname + "\r\n"
        raise socket.error


class TestAccept(unittest.TestCase):
    addr = ('127.9.9.9', 9999)

    def setUp(self):
        self.s = PapovoxLikeServer()

    def test_basic(self):
        nickname = u"Olavo".encode(SYSTEM_ENCODING)
        self.s.server_socket = PapovoxSocketMock(self.addr, nickname)
        client_socket = self.s.server_socket.client_socket
        self.s._accept()
        self.assertEqual((self.s.socket, self.s.addr, self.s.nickname),
                         (client_socket, self.addr, nickname))

    def test_nickname_with_accents(self):
        nickname = u"Anônimo".encode(SYSTEM_ENCODING)
        self.s.server_socket = PapovoxSocketMock(self.addr, nickname)
        client_socket = self.s.server_socket.client_socket
        self.s._accept()
        self.assertEqual((self.s.socket, self.s.addr, self.s.nickname),
                         (client_socket, self.addr, nickname))


class TestCaseXMPP(unittest.TestCase):
    u"""Classe para casos de teste que envolvam interação com o cliente XMPP."""
    def setUp(self):
        # Caixa de saída de mensagens Papovox
        self.outbox = []
        # Caixa de entrada de mensagens XMPP
        self.inbox = []
        class FakePapovoxServer(PapovoxLikeServer):
            nickname = u"Test"
            @staticmethod
            def sendmessage(msg):
                self.outbox.append(msg)
            @staticmethod
            def send_chat_message(sender, body):
                self.inbox.append(body)
        papovox = FakePapovoxServer()
        self.xmpp = BotXMPP('', '', papovox)


class TestClient(TestCaseXMPP):
    def test_receive_message(self):
        m = self.xmpp.make_message(mto='nobody', mtype='chat', mbody='testing')
        self.assertEqual(self.inbox, [], u"Caixa de entrada começa vazia")
        # Recebe uma mensagem XMPP
        self.xmpp.message(m)
        self.assertEqual(self.inbox, [m['body']], u"Mensagem recebida")

    def test_send_first_incoming_message_help(self):
        m = self.xmpp.make_message(mfrom='tester',
                                   mto='nobody', mtype='chat', mbody='testing')
        self.assertEqual(len(self.outbox), 0, u"Caixa de saída começa vazia")
        # Recebe uma mensagem XMPP
        self.xmpp.message(m)
        self.assertEqual(len(self.outbox), 1, u"Envia ajuda sobre comando /r")
        self.xmpp.message(m)
        self.assertEqual(len(self.outbox), 1, u"Envia ajuda apenas uma vez")


class TestServerClientInteraction(TestCaseXMPP):
    def test_show_no_online_contacts(self):
        self.assertEqual(len(self.outbox), 0, u"Caixa de saída começa vazia")
        self.xmpp.papovox.show_online_contacts(self.xmpp)
        self.assertEqual(len(self.outbox), 1, u"Aviso não há contatos online")


class TestCommands(unittest.TestCase):
    def setUp(self):
        # Caixa de mensagens de sistema
        self.sysbox = []
        class FakeSocket(object):
            @staticmethod
            def sendall(data):
                self.sysbox.append(data)
        self.s = PapovoxLikeServer()
        self.s.socket = FakeSocket()

    def test_unknown(self):
        self.assertEqual(len(self.sysbox), 0, u"vazio")
        commands.process_command(None, '/bogus command', self.s)
        self.assertEqual(len(self.sysbox), 1, u"Aviso comando desconhecido")

    def test_ajuda(self):
        self.assertEqual(len(self.sysbox), 0, u"vazio")
        commands.ajuda(papovox=self.s)
        self.assertEqual(len(self.sysbox), 4, u"Ajuda enviada em 4 partes")


if __name__ == '__main__':
    unittest.main()
