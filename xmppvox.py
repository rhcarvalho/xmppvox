#!/usr/bin/env python
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
XMPPVOX - módulo principal

Este módulo é responsável pela coordenação entre os demais módulos.
"""

import socket
import struct
import sys
from itertools import count

from optparse import OptionParser
import getpass

from client import BotXMPP
from server import *
from commands import process_command

import logging
log = logging.getLogger(__name__)


# Setup the command line arguments.
optp = OptionParser()

# Output verbosity options.
optp.add_option('-q', '--quiet', help='set logging to ERROR',
                action='store_const', dest='loglevel',
                const=logging.ERROR, default=logging.INFO)
optp.add_option('-d', '--debug', help='set logging to DEBUG',
                action='store_const', dest='loglevel',
                const=logging.DEBUG, default=logging.INFO)

# JID and password options.
optp.add_option("-j", "--jid", dest="jid",
                help="JID to use")
optp.add_option("-p", "--password", dest="password",
                help="password to use")

opts, args = optp.parse_args()

# Configura logging.
logging.basicConfig(level=opts.loglevel,
                    format='%(levelname)-8s %(asctime)s %(message)s',
                    datefmt='%H:%M')
# Não mostrar mensagens de DEBUG do SleekXMPP.
logging.getLogger('sleekxmpp').setLevel(max(logging.INFO, opts.loglevel))

if opts.jid is None:
    opts.jid = raw_input("Conta (ex.: fulano@gmail.com): ")
if opts.password is None:
    opts.password = getpass.getpass("Senha para %r: " % opts.jid)

xmpp = BotXMPP(opts.jid, opts.password)

if xmpp.connect():
    log.info(u"Conectado ao servidor XMPP")
    # Run XMPP client in another thread
    xmpp.process(block=False)

HOST = '127.0.0.1'        # Escuta apenas conexões locais
PORT = PORTA_PAPOVOX      # Arbitrary non-privileged port
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Reuse open port
#s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
s.listen(1)
try:
    while True:
        log.info(u"XMPPVOX servindo na porta %s" % PORT)

        # Conecta ao Papovox --------------------------------------------------#
        try:
            conn, addr, nickname = accept(s)
        except socket.error:
            log.error(u"Erro: Não foi possível conectar ao Papovox.")
            raise
        #----------------------------------------------------------------------#

        def message_handler(msg):
            u"""Recebe uma mensagem da rede XMPP e envia para o Papovox."""
            sender = xmpp.get_chatty_name(msg['from'])
            body = msg['body']
            send_chat_message(conn, sender, body)

        xmpp.event('papovox_connected',
                   {'nick': nickname, 'message_handler': message_handler})

        try:
            # Processa mensagens do Papovox para a rede XMPP.
            for i in count(1):
                data = recvmessage(conn)

                # Tenta executar algum comando contido na mensagem.
                if process_command(conn, xmpp, data):
                    # Caso algum comando seja executado, sai do loop e passa
                    # para a próxima mensagem.
                    continue

                # Envia mensagem XMPP para quem está conversando comigo.
                if xmpp.talking_to is not None:
                    mto = xmpp.talking_to
                    xmpp.send_message(mto=mto,
                                      mbody=data,
                                      mtype='chat')
                    send_chat_message(conn, u"eu", data)

                    # Avisa se o contato estiver offline.
                    bare_jid = xmpp.get_bare_jid(mto)
                    roster = xmpp.client_roster
                    if bare_jid in roster and not roster[bare_jid].resources:
                        warning = (u"* %s está indisponível agora. "
                                   u"Talvez a mensagem não tenha sido recebida.")
                        sendmessage(conn, warning % xmpp.get_chatty_name(mto))
                else:
                    mto = u"ninguém"
                    sendmessage(conn, u"Não estou em nenhuma conversa.")
                log.debug(u"#%(i)03d. Eu disse para %(mto)s: %(data)s", locals())
        except socket.error, e:
            log.info(e.message)
        finally:
            log.info(u"Conexão com o Papovox encerrada.")
            break
except socket.error:
    sys.exit(1)
finally:
    xmpp.event('papovox_disconnected')
    log.info(u"Fim do XMPPVOX.")
