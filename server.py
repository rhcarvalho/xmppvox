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
XMPPVOX - módulo servidor

Este módulo implementa um servidor compatível com o protocolo usado pelo Papovox
e Sítiovox.
"""

import socket
import struct
import textwrap
import time
from cStringIO import StringIO

import logging
log = logging.getLogger(__name__)


# Constantes ------------------------------------------------------------------#

# Todas as strings passadas para o Papovox devem ser codificadas usando a
# codificação padrão do Windows.
SYSTEM_ENCODING = 'cp1252'

PORTA_PAPOVOX = 1963
#PORTA_URGENTE = 1964
#PORTA_NOMES = 1956

DADOTECLADO = 1   # texto da mensagem (sem tab, nem lf nem cr ao final)

TAMANHO_DO_BUFFER = 4096 # Ver C:\winvox\Fontes\tradutor\DVINET.PAS

TAMANHO_MAXIMO_MSG = 255

#------------------------------------------------------------------------------#

def accept(sock):
    ur"""Aceita uma conexão via socket com o Papovox.

    Retorna socket e endereço de rede do Papovox e o nome do usuário conectado.

    Ver 'C:\winvox\Fontes\PAPOVOX\PPLIGA.PAS' e
    'C:\winvox\Fontes\SITIOVOX\SVPROC.PAS'.
    """
    log.info(u"Aguardando Papovox conectar...")
    conn, addr = sock.accept()
    sendline(conn, u"+OK - %s:%s conectado" % addr)
    nickname = recvline(conn, TAMANHO_DO_BUFFER)
    sendline(conn, u"+OK")

    # Espera Papovox estar pronto para receber mensagens.
    #
    # A espera é necessária pois se enviar mensagens logo em seguida o Papovox
    # as ignora, provavelmente relacionado a alguma temporização ou espera na
    # leitura de algum buffer ou estado da variável global 'conversando'.
    # O SítioVox aguarda 100ms (arquivo SVPROC.PAS).
    time.sleep(0.1)

    log.info(u"Conectado ao Papovox em %s:%s", *addr)
    log.info(u"Apelido: %s", nickname)

    # Envia mensagem de boas-vindas
    sendmessage(conn, u"Olá %s, bem-vindo ao XMPPVOX!" % nickname)
    sendmessage(conn, u"Digite /ajuda para obter ajuda.")

    return conn, addr, nickname


# Funções de envio de dados para o Papovox ------------------------------------#

def sendline(sock, line):
    u"""Codifica e envia texto via socket pelo protocolo do Papovox.

    Uma quebra de linha é adicionada automaticamente ao fim da mensagem.

    Nota: esta função *não* deve ser usada para enviar mensagens. Use apenas
    para transmitir dados brutos de comunicação.
    """
    log.debug(u"[sendline] %s", line)
    line = line.encode(SYSTEM_ENCODING)
    sock.sendall("%s\r\n" % (line,))

def sendmessage(sock, msg):
    u"""Codifica e envia uma mensagem via socket pelo protocolo do Papovox."""
    log.debug(u"[sendmessage] %s", msg)
    msg = msg.encode(SYSTEM_ENCODING)

    # Apesar de teoricamente o protocolo do Papovox suportar mensagens com até
    # 65535 (2^16 - 1) caracteres, na prática apenas os 255 primeiros são
    # exibidos, e os restantes acabam ignorados.
    # Portanto, é necessário quebrar mensagens grandes em várias menores.
    chunks = textwrap.wrap(
        text=msg,
        width=TAMANHO_MAXIMO_MSG,
        expand_tabs=False,
        replace_whitespace=False,
        drop_whitespace=False,
    )

    def sendmsg(msg):
        sock.sendall("%s%s" % (struct.pack('<BH', DADOTECLADO, len(msg)), msg))
    # Envia uma ou mais mensagens pelo socket
    map(sendmsg, chunks)

def send_chat_message(sock, sender, body, _state={}):
    u"""Formata e envia uma mensagem de bate-papo via socket.

    Use esta função para enviar uma mensagem para o Papovox sintetizar.
    """
    # Tempo máximo entre duas mensagens para considerar que fazem parte da mesma
    # conversa, em segundos.
    TIMEOUT = 90

    # Recupera estado.
    last_sender = _state.get('last_sender')
    last_timestamp = _state.get('last_timestamp', 0) # em segundos

    timestamp = time.time()
    timed_out = (time.time() - last_timestamp) > TIMEOUT

    if sender == last_sender and not timed_out:
        msg = u"%(body)s"
    else:
        msg = u"%(sender)s disse: %(body)s"
    sendmessage(sock, msg % locals())

    # Guarda estado para ser usado na próxima execução.
    _state['last_sender'] = sender
    _state['last_timestamp'] = timestamp


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

def recvline(sock, size):
    u"""Recebe uma linha via socket.

    A string é retornada em unicode e não contém \r nem \n.
    """
    # Assume que apenas uma linha está disponível no socket.
    data = recv(sock, size).rstrip('\r\n')
    data = data.decode(SYSTEM_ENCODING)
    if any(c in data for c in '\r\n'):
        log.warning("[recvline] recebeu mais que uma linha!")
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

def recvmessage(sock):
    u"""Recebe uma mensagem via socket pelo protocolo do Papovox.

    A mensagem é retornada em unicode.
    Se uma exceção não for levantada, esta função sempre retorna uma mensagem.
    """
    # Tenta receber mensagem até obter sucesso.
    while True:
        datatype, datalen = struct.unpack('<BH', recvall(sock, 3))

        # Recusa dados do Papovox que não sejam do tipo DADOTECLADO
        if datatype != DADOTECLADO:
            log.warning(u"Recebi tipo de dados desconhecido: (%d)" % datatype)
            continue

        # Ignora mensagens vazias
        if datalen == 0:
            log.debug(u"Mensagem vazia ignorada")
            continue

        # Recebe dados/mensagem do Papovox
        data = recvall(sock, datalen)
        data = data.decode(SYSTEM_ENCODING)
        return data
