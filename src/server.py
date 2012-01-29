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
import sys
from cStringIO import StringIO

import commands
from strings import get_string as S

import logging
log = logging.getLogger(__name__)


# Constantes ------------------------------------------------------------------#

# Todas as strings passadas para o Papovox devem ser codificadas usando a
# codificação padrão do DOSVOX, ISO-8859-1, também conhecida como Latin-1.
SYSTEM_ENCODING = 'ISO-8859-1'

#------------------------------------------------------------------------------#


class PapovoxLikeServer(object):
    u"""Um servidor compatível com o Papovox."""

    HOST = '127.0.0.1'        # Escuta apenas conexões locais
    PORTA_PAPOVOX = 1963
    #PORTA_URGENTE = 1964
    #PORTA_NOMES = 1956
    DADOTECLADO = 1           # texto da mensagem (sem tab, nem lf nem cr ao final)
    TAMANHO_DO_BUFFER = 4096  # Ver C:\winvox\Fontes\tradutor\DVINET.PAS
    TAMANHO_MAXIMO_MSG = 255

    def __init__(self, port=None):
        u"""Cria servidor compatível com o Papovox."""
        # Socket do servidor
        self.server_socket = None
        # Porta do servidor
        self.port = port or self.PORTA_PAPOVOX

        # Socket do cliente
        self.socket = None
        # Endereço do cliente
        self.addr = None

        # Apelido
        self.nickname = u""

    def connect(self):
        u"""Conecta ao Papovox via socket.

        Retorna booleano indicando se a conexão foi bem-sucedida.
        Bloqueia aguardando Papovox conectar.
        Define atributos:
            self.server_socket
            self.socket
            self.addr
            self.nickname
        """
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Reutilizar porta já aberta
            #self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.HOST, self.port))
            self.server_socket.listen(1)

            log.debug(u"XMPPVOX servindo na porta %s" % self.port)

            # Conecta ao Papovox ----------------------------------------------#
            try:
                self._accept()
            except socket.error:
                return False
            #------------------------------------------------------------------#
            return True
        except socket.error, e:
            log.error(e.message or u" ".join(map(unicode, e.args)))
            sys.exit(1)

    def _accept(self):
        ur"""Aceita uma conexão via socket com o Papovox.

        Ver 'C:\winvox\Fontes\PAPOVOX\PPLIGA.PAS' e
        'C:\winvox\Fontes\SITIOVOX\SVPROC.PAS'.
        """
        log.info(u"Aguardando Papovox conectar...")
        self.socket, self.addr = self.server_socket.accept()
        self.sendline(u"+OK - %s:%s conectado" % self.addr)
        self.nickname = self.recvline(self.TAMANHO_DO_BUFFER)
        self.sendline(u"+OK")

        # Espera Papovox estar pronto para receber mensagens.
        #
        # A espera é necessária pois se enviar mensagens logo em seguida o Papovox
        # as ignora, provavelmente relacionado a alguma temporização ou espera na
        # leitura de algum buffer ou estado da variável global 'conversando'.
        # O SítioVox aguarda 100ms (arquivo SVPROC.PAS).
        time.sleep(0.1)

        log.info(u"Conectado ao Papovox")
        log.info(u"Apelido: %s", self.nickname)

    def disconnect(self):
        u"""Desliga a conexão com o Papovox."""
        log.debug(u"Encerrando conexão com o Papovox...")
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
        self.server_socket.shutdown(socket.SHUT_RDWR)
        self.server_socket.close()

    # Funções de integração com o cliente XMPP --------------------------------#

    def process(self, xmpp):
        u"""Processa mensagens do Papovox para a rede XMPP.

        Mensagens podem conter comandos para o XMPPVOX.
        Nota: esta função só termina caso ocorra algum erro ou a conexão com o
              Papovox seja perdida.
        """
        try:
            while True:
                data = self.recvmessage()
                # Tenta executar algum comando contido na mensagem.
                if commands.process_command(xmpp, data, self):
                    # Caso algum comando seja executado, sai do loop e passa
                    # para a próxima mensagem.
                    continue
                else:
                    # Caso contrário, envia a mensagem para a rede XMPP.
                    self.send_xmpp_message(xmpp, data)
        except socket.error, e:
            log.debug(e.message)
        finally:
            log.info(u"Conexão com o Papovox encerrada")

    def show_online_contacts(self, xmpp):
        u"""Envia para o Papovox informação sobre contatos disponíveis."""
        online_contacts_count = len(commands.enumerate_online_roster(xmpp))
        if online_contacts_count == 0:
            online_contacts_count = "nenhum"
            contacts = u"contato disponível"
        elif online_contacts_count == 1:
            contacts = u"contato disponível"
        else:
            contacts = u"contatos disponíveis"
        self.sendmessage(S.ONLINE_CONTACTS_INFO.format(amount=online_contacts_count,
                                                       contacts=contacts))

    def send_xmpp_message(self, xmpp, mbody):
        u"""Envia mensagem XMPP para quem está conversando comigo."""
        if xmpp.talking_to is not None:
            mto = xmpp.talking_to
            # Envia mensagem XMPP.
            xmpp.send_message(mto=mto, mbody=mbody, mtype='chat')
            # Repete a mensagem que estou enviando para ser falada pelo Papovox.
            self.send_chat_message(u"eu", mbody)

            # Avisa se o contato estiver offline.
            bare_jid = xmpp.get_bare_jid(mto)
            roster = xmpp.client_roster
            if bare_jid in roster and not roster[bare_jid].resources:
                name = xmpp.get_chatty_name(mto)
                self.sendmessage(S.WARN_MSG_TO_OFFLINE_USER.format(name=name))
        else:
            mto = u"ninguém"
            self.sendmessage(S.WARN_MSG_TO_NOBODY)
        log.debug(u"[send_xmpp_message] para %(mto)s: %(mbody)s", locals())

    # Funções de envio de dados para o Papovox --------------------------------#

    def sendline(self, line):
        u"""Codifica e envia texto via socket pelo protocolo do Papovox.

        Uma quebra de linha é adicionada automaticamente ao fim da mensagem.

        Nota: esta função *não* deve ser usada para enviar mensagens. Use apenas
        para transmitir dados brutos de comunicação.
        """
        log.debug(u"[sendline] %s", line)
        line = line.encode(SYSTEM_ENCODING, 'replace')
        self.socket.sendall("%s\r\n" % (line,))

    def sendmessage(self, msg):
        u"""Codifica e envia uma mensagem via socket pelo protocolo do Papovox."""
        log.debug(u"[sendmessage] %s", msg)
        msg = msg.encode(SYSTEM_ENCODING, 'replace')

        # Apesar de teoricamente o protocolo do Papovox suportar mensagens com até
        # 65535 (2^16 - 1) caracteres, na prática apenas os 255 primeiros são
        # exibidos, e os restantes acabam ignorados.
        # Portanto, é necessário quebrar mensagens grandes em várias menores.
        chunks = textwrap.wrap(
            text=msg,
            width=self.TAMANHO_MAXIMO_MSG,
            expand_tabs=False,
            replace_whitespace=False,
            drop_whitespace=False,
        )

        def sendmsg(msg):
            self.socket.sendall("%s%s" % (struct.pack('<BH', self.DADOTECLADO, len(msg)), msg))
        # Envia uma ou mais mensagens pelo socket
        map(sendmsg, chunks)

    def send_chat_message(self, sender, body, _state={}):
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
            msg = S.MSG
        else:
            msg = S.MSG_FROM
        self.sendmessage(msg.format(**locals()))

        # Guarda estado para ser usado na próxima execução.
        _state['last_sender'] = sender
        _state['last_timestamp'] = timestamp

    def signal_error(self, msg):
        u"""Sinaliza erro para o Papovox e termina a conexão."""
        # Avisa Papovox sobre o erro.
        self.sendmessage(msg)
        # Encerra conexão com o Papovox.
        self.disconnect()

    # Funções de recebimento de dados do Papovox ------------------------------#

    def recv(self, size):
        u"""Recebe dados via socket.

        Use esta função para receber do socket `size' bytes ou menos.
        Levanta uma exceção caso nenhum byte seja recebido.

        Nota: em geral, use esta função ao invés do método 'socket.recv'.
        Veja também a função 'recvall'.
        """
        data = self.socket.recv(size)
        if not data and size:
            raise socket.error(u"Nenhum dado recebido do socket, conexão perdida.")
        return data

    def recvline(self, size):
        u"""Recebe uma linha via socket.

        A string é retornada em unicode e não contém \r nem \n.
        """
        # Assume que apenas uma linha está disponível no socket.
        data = self.recv(size).rstrip('\r\n')
        data = data.decode(SYSTEM_ENCODING)
        if any(c in data for c in '\r\n'):
            log.warning("[recvline] recebeu mais que uma linha!")
        return data

    def recvall(self, size):
        u"""Recebe dados exaustivamente via socket.

        Use esta função para receber do socket exatamente `size' bytes.
        Levanta uma exceção caso nenhum byte seja recebido.

        Nota: em geral, use esta função ou 'recv' ao invés do método 'socket.recv'.
        """
        data = StringIO()
        while data.tell() < size:
            data.write(self.recv(size - data.tell()))
        data_str = data.getvalue()
        data.close()
        return data_str

    def recvmessage(self):
        u"""Recebe uma mensagem via socket pelo protocolo do Papovox.

        A mensagem é retornada em unicode.
        Se uma exceção não for levantada, esta função sempre retorna uma mensagem.
        """
        # Tenta receber mensagem até obter sucesso.
        while True:
            datatype, datalen = struct.unpack('<BH', self.recvall(3))

            # Recusa dados do Papovox que não sejam do tipo DADOTECLADO
            if datatype != self.DADOTECLADO:
                log.warning(u"Recebi tipo de dados desconhecido: (%d)" % datatype)
                continue

            # Ignora mensagens vazias
            if datalen == 0:
                log.debug(u"Mensagem vazia ignorada")
                continue

            # Recebe dados/mensagem do Papovox
            data = self.recvall(datalen)
            data = data.decode(SYSTEM_ENCODING)
            return data

# FIXME Remover referências hard-coded para comandos e o prefixo de comando.
