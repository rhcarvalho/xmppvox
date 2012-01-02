#!/usr/bin/env python
# -*- coding: utf-8 -*-
u"""
XMPPVOX - módulo servidor

Este módulo implementa um servidor compatível com o protocolo usado pelo Papovox
e Sítiovox.
"""

import socket
import struct
import time
from cStringIO import StringIO


# Constantes ------------------------------------------------------------------#

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


if __name__ == '__main__':
    print "Execute 'python xmppvox.py'"
