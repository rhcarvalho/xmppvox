#!/usr/bin/env python
# -*- coding: utf-8 -*-
import socket
import struct
import time
from functools import partial
from itertools import count
from cStringIO import StringIO

import getpass
import logging
from echo_client import GenericBot

#---------------- Constantes --------------------------------------------------#

# Todas as strings passadas para o Papovox devem ser codificadas usando a
# codificação padrão do Windows.
SYSTEM_ENCODING = 'cp1252'

PORTA_PAPOVOX = 1963
#PORTA_URGENTE = 1964
#PORTA_NOMES = 1956

DADOTECLADO = 1   # texto da mensagem (sem tab, nem lf nem cr ao final)

TAMANHO_DO_BUFFER = 4096 # Ver C:\winvox\Fontes\tradutor\DVINET.PAS

REMETENTE_DESCONHECIDO = u"remetente desconhecido"

#------------------------------------------------------------------------------#

def accept(sock):
    ur"""Aceita uma conexão via socket com o Papovox.
    
    Retorna socket e endereço de rede do Papovox e o nome do usuário conectado.
    
    Ver 'C:\winvox\Fontes\PAPOVOX\PPLIGA.PAS' e
    'C:\winvox\Fontes\SITIOVOX\SVPROC.PAS'.
    """
    conn, addr = sock.accept()
    sendline(conn, u"+OK - %s:%s conectado" % addr)
    nickname = recv(conn, TAMANHO_DO_BUFFER)
    sendline(conn, u"+OK")
    
    # Espera Papovox estar pronto para receber mensagens.
    #
    # A espera é necessária pois se enviar mensagens logo em seguida o Papovox
    # as ignora, provavelmente relacionado a alguma temporização ou espera na
    # leitura de algum buffer ou estado da variável global 'conversando'.
    # O SítioVox aguarda 100ms (arquivo SVPROC.PAS).
    time.sleep(0.1)
    
    print u"Aceitei conexão de %s:%s" % addr
    print u"Apelido: %s" % (nickname,)
    return conn, addr, nickname


# Funções de envio de dados para o Papovox ------------------------------------#

def sendline(sock, line):
    u"""Codifica e envia texto via socket pelo protocolo do Papovox.
    
    Uma quebra de linha é adicionada automaticamente ao fim da mensagem.
    
    Nota: esta função *não* deve ser usada para enviar mensagens. Use apenas
    para transmitir dados brutos de comunicação.
    """
    print "==>> %s ==>>" % (line,)
    line = line.encode(SYSTEM_ENCODING)
    sock.sendall("%s\r\n" % (line,))

def sendmessage(sock, msg):
    u"""Codifica e envia uma mensagem via socket pelo protocolo do Papovox."""
    print "[[[[ %s ]]]]" % (msg,)
    msg = msg.encode(SYSTEM_ENCODING)
    sock.sendall("%s%s" % (struct.pack('<BH', DADOTECLADO, len(msg)),
                           msg))

def send_chat_message(sock, sender, body):
    u"""Formata e envia uma mensagem de bate-papo via socket.
    
    Use esta função para enviar uma mensagem para o Papovox sintetizar.
    """
    sendmessage(sock, u"%(sender)s disse: %(body)s" % locals())


# Funções de recebimento de dados do Papovox ----------------------------------#

def recv(sock, size):
    u"""Recebe dados via socket.
    
    Use esta função para receber do socket `size' bytes ou menos.
    Levanta uma exceção caso nenhum byte seja recebido.
    
    Nota: em geral, use esta função ao invés do método 'sock.recv'.
    Veja também a função 'recvall'.
    """
    data = sock.recv(size)
    if not data and size:
        raise socket.error(u"Nenhum dado recebido do socket, conexão perdida.")
    return data

def recvall(sock, size):
    u"""Recebe dados exaustivamente via socket.
    
    Use esta função para receber do socket exatamente `size' bytes.
    Levanta uma exceção caso nenhum byte seja recebido.
    
    Nota: em geral, use esta função ou 'recv' ao invés do método 'sock.recv'.
    """
    data = StringIO()
    while data.tell() < size:
        data.write(recv(sock, size - data.tell()))
    data_str = data.getvalue()
    data.close()
    return data_str

#------------------------------------------------------------------------------#

def main():
    # Setup logging.
    logging.basicConfig(level=logging.INFO,
                        format='%(levelname)-8s %(message)s')

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
