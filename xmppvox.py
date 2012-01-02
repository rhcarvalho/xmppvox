#!/usr/bin/env python
# -*- coding: utf-8 -*-
u"""
XMPPVOX - módulo principal

Este módulo é responsável pela coordenação entre os demais módulos.
"""

import socket
import struct
from functools import partial
from itertools import count

import getpass
import logging

from client import GenericBot
from server import *


def main():
    # Configura logging.
    logging.basicConfig(level=logging.INFO,
                        format='%(levelname)-8s %(asctime)s %(message)s',
                        datefmt='%H:%M:%S')

    jid = raw_input("Conta (ex.: fulano@gmail.com): ")
    password = getpass.getpass("Senha para %r: " % jid)
    xmpp = GenericBot(jid, password)
    xmpp.register_plugin('xep_0030') # Service Discovery
    xmpp.register_plugin('xep_0004') # Data Forms
    xmpp.register_plugin('xep_0060') # PubSub
    xmpp.register_plugin('xep_0199') # XMPP Ping
    
    if xmpp.connect():
        print "<<XMPP conectado>>"
        xmpp.process(threaded=True)

    HOST = ''                 # Symbolic name meaning all available interfaces
    PORT = PORTA_PAPOVOX      # Arbitrary non-privileged port
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Reuse open port
    #s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(1)
    while True:
        print u"XMPPVOX servindo na porta %s" % PORT
        
        # Conecta ao Papovox -----------------------------------------------#
        try:
            conn, addr, nickname = accept(s)
        except socket.error:
            print u"Erro: Não foi possível conectar ao Papovox."
        #----------------------------------------------------------------------#
        
        # Funções úteis usando a conexão atual
        _sendline, _sendmessage, _recvall = map(partial,
                                                (sendline, sendmessage, recvall),
                                                (conn, conn, conn))
        
        def recv_new_msg(msg):
            sender = msg['from'].user or REMETENTE_DESCONHECIDO
            body = msg['body']
            send_chat_message(conn, sender, body)
        
        xmpp.func_receive_msg = recv_new_msg
        
        try:
            # Envia mensagem de boas-vindas
            _sendmessage(u"Olá companheiro, bem-vindo ao Gugou Tolk Vox!")
            
            # Processa mensagens do Papovox para a rede XMPP
            for i in count(1):
                datatype, datalen = struct.unpack('<BH', _recvall(3))
                
                # Recusa dados do Papovox que não sejam do tipo DADOTECLADO
                if datatype != DADOTECLADO:
                    print u"<<== Recebi tipo de dados desconhecido: (%d) <<==" % datatype
                    continue
                
                # Recebe dados/mensagem do Papovox
                data = _recvall(datalen)
                data = data.decode(SYSTEM_ENCODING)
                
                # Envia mensagem XMPP para o último remetente
                if xmpp.last_sender is not None:
                    xmpp.send_message(mto=xmpp.last_sender,
                                      mbody=data,
                                      mtype='chat')
                    send_chat_message(conn, u"eu", data)
                print u"#%03d. %s ** para %s" % (i, data,
                                                 xmpp.last_sender or u"ninguém")
        except socket.error, e:
            print u"Erro: %s" % (e,)
        finally:
            print u"Conexão encerrada."


if __name__ == '__main__':
    main()
