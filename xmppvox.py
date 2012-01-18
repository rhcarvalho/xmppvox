#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
            bare_jid = msg['from'].bare
            roster = xmpp.client_roster
            
            # Tenta usar um nome amigável se possível
            if bare_jid in roster and roster[bare_jid]['name']:
                sender = roster[bare_jid]['name']
            # Senão usa o nome de usuário do JID. Por exemplo, fulano quando JID
            # for fulano@gmail.com
            elif msg['from'].user:
                sender = msg['from'].user
            # Este caso não deveria ocorrer, pois toda mensagem que chega
            # deveria ter um remetente.
            else:
                sender = REMETENTE_DESCONHECIDO
            body = msg['body']
            send_chat_message(conn, sender, body)
        
        xmpp.event('papovox_connected',
                   {'nick': nickname, 'message_handler': message_handler})
        
        try:
            # Processa mensagens do Papovox para a rede XMPP
            for i in count(1):
                data = recvmessage(conn)
                
                # Tenta executar algum comando contido na mensagem
                if process_command(conn, xmpp, data):
                    # Caso algum comando seja executado, sai do loop e passa
                    # para a próxima mensagem.
                    continue
                
                # Envia mensagem XMPP para o último remetente
                if xmpp.last_sender_jid is not None:
                    mto = xmpp.last_sender_jid
                    xmpp.send_message(mto=mto,
                                      mbody=data,
                                      mtype='chat')
                    send_chat_message(conn, u"eu", data)
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
