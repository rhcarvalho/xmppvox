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

from client import GenericBot
from server import *
from commands import process_commands

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

xmpp = GenericBot(opts.jid, opts.password)
xmpp.register_plugin('xep_0030') # Service Discovery
xmpp.register_plugin('xep_0004') # Data Forms
xmpp.register_plugin('xep_0060') # PubSub
xmpp.register_plugin('xep_0199') # XMPP Ping

if xmpp.connect():
    log.info(u"Conectado ao servidor XMPP")
    # Run XMPP client in another thread
    xmpp.process(block=False)

HOST = ''                 # Symbolic name meaning all available interfaces
PORT = PORTA_PAPOVOX      # Arbitrary non-privileged port
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Reuse open port
#s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
s.listen(1)
while True:
    log.info(u"XMPPVOX servindo na porta %s" % PORT)
    
    # Conecta ao Papovox -----------------------------------------------#
    try:
        conn, addr, nickname = accept(s)
    except socket.error:
        log.error(u"Erro: Não foi possível conectar ao Papovox.")
        xmpp.disconnect()
        sys.exit(1)
    #----------------------------------------------------------------------#
    
    def recv_new_msg(msg):
        sender = msg['from'].user or REMETENTE_DESCONHECIDO
        body = msg['body']
        send_chat_message(conn, sender, body)
    
    xmpp.func_receive_msg = recv_new_msg
    
    try:
        # Processa mensagens do Papovox para a rede XMPP
        for i in count(1):
            data = recvmessage(conn)
            
            # Tenta executar algum comando contido na mensagem
            if process_commands(conn, xmpp, data):
                # Caso algum comando seja executado, sai do loop e passa para
                # a próxima mensagem.
                continue
            
            # Envia mensagem XMPP para o último remetente
            if xmpp.last_sender is not None:
                xmpp.send_message(mto=xmpp.last_sender,
                                  mbody=data,
                                  mtype='chat')
                send_chat_message(conn, u"eu", data)
            mto = xmpp.last_sender or u"ninguém"
            log.debug(u"#%(i)03d. Eu disse para %(mto)s: %(data)s", locals())
    except socket.error, e:
        log.info(e)
    finally:
        log.info(u"Conexão com o Papovox encerrada.")
