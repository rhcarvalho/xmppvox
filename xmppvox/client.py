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
XMPPVOX - módulo cliente

Este módulo implementa um cliente do protocolo XMPP, usando a biblioteca
SleekXMPP, que permite estabelecer comunicação com servidores diversos, como
Google Talk, Facebook chat e Jabber.
"""

import sys
from threading import Timer

import sleekxmpp

from xmppvox import commands
from xmppvox.strings import get_string as S
from xmppvox.version import __version__

import logging
log = logging.getLogger(__name__)


# Python versions before 3.0 do not use UTF-8 encoding
# by default. To ensure that Unicode is handled properly
# throughout SleekXMPP, we will set the default encoding
# ourselves to UTF-8.
if sys.version_info < (3, 0):
    from sleekxmpp.util.misc_ops import setdefaultencoding
    setdefaultencoding('utf8')
else:
    raw_input = input


class BotXMPP(sleekxmpp.ClientXMPP):
    u"""Um robô simples para processar mensagens recebidas via XMPP.

    Sempre que uma mensagem do tipo 'normal' ou 'chat' for recebida, uma função
    é chamada e a mensagem é passada como argumento.
    É possível fornecer sua própria função para tratar mensagens.
    """
    # Aceita e cria requisições de inscrição bidirecional:
    auto_authorize = True
    auto_subscribe = True

    def __init__(self, jid, password, papovox):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)

        # Disable IPv6 to avoid connectivity problems
        self.use_ipv6 = False

        # Referência para o servidor compatível com o Papovox
        self.papovox = papovox
        self.nickname = papovox.nickname

        # Eventos do SleekXMPP que serão tratados
        self.add_event_handler("connected", self.handle_connected)
        self.add_event_handler("disconnected", self.handle_disconnected)
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("message", self.message)
        self.add_event_handler('got_online', self.got_online)
        self.add_event_handler('got_offline', self.got_offline)
        self.add_event_handler('changed_status', self.changed_status)
        self.add_event_handler('no_auth', self.no_auth)
        self.add_event_handler('socket_error', self.socket_error)

        # Com quem estou conversando
        self.talking_to = None
        # Último que me mandou mensagem
        self.last_sender = None

        # Registra alguns plugins do SleekXMPP
        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin('xep_0004') # Data Forms
        self.register_plugin('xep_0060') # PubSub
        self.register_plugin('xep_0199') # XMPP Ping

    def connect(self, *args, **kwargs):
        log.info(u"Conectando-se ao servidor %s...", self.boundjid.host)
        return sleekxmpp.ClientXMPP.connect(self, *args, **kwargs)

    def handle_connected(self, event):
        log.info(u"Conectado ao servidor %s.", self.boundjid.host)

    def handle_disconnected(self, event):
        log.info(u"Desconectado do servidor %s.", self.boundjid.host)

    def start(self, event):
        u"""Processa evento de início de sessão.

        Quando uma conexão é estabelecida, a lista de contatos é solicitada,
        a presença inicial enviada para rede XMPP e uma mensagem de boas-vindas
        é enviada ao Papovox.
        """
        self.get_roster()
        log.debug(u"Enviando presença inicial...")
        self.send_presence(pnick=self.nickname)
        # Envia mensagem de boas-vindas
        self.papovox.sendmessage(S.WELCOME.format(nick=self.nickname,
                                                  version=__version__))
        # Exibe lista de contatos online alguns segundos após eu ficar
        # online. É necessário esperar um tempo para receber presenças dos
        # contatos.
        Timer(5, self.papovox.show_online_contacts, (self,)).start()

    def message(self, msg):
        u"""Processa mensagens recebidas.

        As mensagens podem ser também de bate-papo multi-usuário (MUC)
        ou mensagens de erro.
        """
        # Ignora mensagens que não sejam 'chat' ou 'normal', por exemplo
        # mensagens de erro.
        if msg['type'] in ('chat', 'normal'):
            # Recebe mensagem da rede XMPP e envia para o Papovox.
            sender = self.get_chatty_name(msg['from'])
            body = msg['body']
            self.papovox.send_chat_message(sender, body)

            # Ensina o comando /responder na primeira vez que alguém me mandar
            # mensagem, se eu ainda não estiver falando com este alguém.
            if self.talking_to:
                talking_to_bare = self.get_bare_jid(self.talking_to)
            else:
                talking_to_bare = None
            from_bare = self.get_bare_jid(msg['from'])
            if self.last_sender is None and talking_to_bare != from_bare:
                sendmessage = self.papovox.sendmessage
                name = self.get_chatty_name(msg['from'])
                sendmessage(S.FIRST_INCOME_MSG_HELP.format(name=name))
            # Lembra da última pessoa que falou comigo. Útil para usar comando
            # /responder.
            self.last_sender = msg['from']

    def got_online(self, presence):
        u"""Registra que um contato apareceu online."""
        log.debug(u"Entrou: %s", presence['from'])

    def got_offline(self, presence):
        u"""Registra que um contato ficou offline."""
        log.debug(u"Saiu: %s", presence['from'])

    def changed_status(self, presence):
        u"""Processa evento de presenças de contatos.

        Quando um contato envia uma nova presença, seu estado pode ter mudado
        de diferentes formas. Ele pode exibir uma nova mensagem de status,
        mudar para disponível/ocupado/ausente/etc, etc.

        Caso ele mude de apelido, este apelido será usado na interface do
        XMPPVOX.
        """
        # A presença pode ou não incluir um elemento 'nick'.
        # Em ambos os casos o comando abaixo executa corretamente, retornando
        # None caso 'nick' não esteja presente.
        nick = presence['nick'].get_nick()
        jid = presence['from'].bare

        # Se o contato está no meu roster e ainda não tem um nome, vamos usar
        # temporariamente o nick como nome.
        # Este é o caso quando dois usuários do XMPPVOX falam entre si, pois o
        # XMPPVOX envia o apelido do usuário quando ele se conecta à rede XMPP.
        if jid in self.client_roster and not self.client_roster[jid]['name'] and nick:
            log.debug(u"Novo apelido: %s (%s)", nick, jid)
            # Guarda o nome localmente, mas não salva no servidor XMPP.
            # Se fosse desejável salvar, usar método self.update_roster.
            self.client_roster[jid]['name'] = nick

    def no_auth(self, stanza):
        log.error(u"Falha na autenticação: usuário ou senha incorretos.")
        # Avisa ao Papovox que a autenticação falhou.
        self.papovox.signal_error(S.ERROR_NO_AUTH)

    def socket_error(self, error):
        host = self.boundjid.host
        log.error(u"Não foi possível conectar ao servidor '%s'.\n"
                  u"Verifique sua conexão com a Internet.", host)
        # Avisa ao Papovox que houve erro de conexão.
        self.papovox.signal_error(S.ERROR_SOCKET_ERROR.format(host=host))
        # Interrompe atividades deste cliente XMPP.
        self.stop.set()

    def get_chatty_name(self, jid_obj_or_string):
        u"""Retorna nome de usuário para ser usado numa conversa."""
        bare_jid = self.get_bare_jid(jid_obj_or_string)
        roster = self.client_roster
        # Tenta usar um nome amigável se possível.
        if bare_jid in roster and roster[bare_jid]['name']:
            name = roster[bare_jid]['name']
        # Senão usa o nome de usuário do JID. Por exemplo, fulano quando JID
        # for fulano@gmail.com.
        elif jid_obj_or_string:
            try:
                # sleekxmpp.roster.jid.JID
                name = jid_obj_or_string.user
            except AttributeError:
                # string
                name = jid_obj_or_string.split('@', 1)[0]
        # Este caso não deveria ocorrer normalmente.
        else:
            name = u"desconhecido"
        return name

    @staticmethod
    def get_bare_jid(jid_obj_or_string):
        u"""Retorna o JID sem o resource."""
        try:
            # Se for uma instância de sleekxmpp.roster.jid.JID, chama seu método:
            bare_jid = jid_obj_or_string.bare
        except AttributeError:
            # Ou, se for uma string, remove resource (tudo depois da /, inclusive):
            bare_jid = jid_obj_or_string.split('/', 1)[0]
        return bare_jid

    def validate_jid(self):
        u"""Causa uma exceção 'InvalidJID' se o JID for inválido para o XMPPVOX."""
        jid = self.boundjid.full
        if not commands.jid_regexp.match(jid):
            raise sleekxmpp.InvalidJID('JID failed validation.')
