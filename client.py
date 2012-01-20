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
XMPPVOX - módulo cliente

Este módulo implementa um cliente do protocolo XMPP, usando a biblioteca
SleekXMPP, que permite estabelecer comunicação com servidores diversos, como
Google Talk, Facebook chat e Jabber.
"""

import sys
import getpass
from optparse import OptionParser

import sleekxmpp

import logging
log = logging.getLogger(__name__)


# Python versions before 3.0 do not use UTF-8 encoding
# by default. To ensure that Unicode is handled properly
# throughout SleekXMPP, we will set the default encoding
# ourselves to UTF-8.
if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding('utf8')
else:
    raw_input = input


class BotXMPP(sleekxmpp.ClientXMPP):
    u"""Um robô simples para processar mensagens recebidas via XMPP.

    Sempre que uma mensagem do tipo 'normal' ou 'chat' for recebida, uma função
    é chamada e a mensagem é passada como argumento.
    É possível fornecer sua própria função para tratar mensagens.
    """
    # Accept and create bidirectional subscription requests:
    auto_authorize = True
    auto_subscribe = True

    def __init__(self, jid, password):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)

        # The session_start event will be triggered when
        # the bot establishes its connection with the server
        # and the XML streams are ready for use. We want to
        # listen for this event so that we we can initialize
        # our roster.
        self.add_event_handler("session_start", self.start)

        # The message event is triggered whenever a message
        # stanza is received. Be aware that that includes
        # MUC messages and error messages.
        self.add_event_handler("message", self.message)

        # Outros eventos interessantes
        self.add_event_handler('got_online', self.got_online)
        self.add_event_handler('got_offline', self.got_offline)
        self.add_event_handler('changed_status', self.changed_status)

        # Eventos de integração com Papovox
        self.add_event_handler('papovox_connected', self.papovox_connected)
        self.add_event_handler('papovox_disconnected', self.papovox_disconnected)

        self.nickname = u""
        self.message_handler = None

        # Com quem estou conversando
        self.talking_to = None

        # Registra alguns plugins do SleekXMPP
        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin('xep_0004') # Data Forms
        self.register_plugin('xep_0060') # PubSub
        self.register_plugin('xep_0199') # XMPP Ping

    def start(self, event):
        """
        Process the session_start event.

        Typical actions for the session_start event are
        requesting the roster and broadcasting an initial
        presence stanza.

        Arguments:
            event -- An empty dictionary. The session_start
                     event does not provide any additional
                     data.
        """
        self.get_roster()

    def papovox_connected(self, event):
        self.nickname = event.get('nick')
        self.message_handler = event.get('message_handler')
        # Envia presença em broadcast. Neste momento o usuário aparece como
        # online para seus contatos.
        self.send_presence(pnick=self.nickname)

    def papovox_disconnected(self, event):
        self.disconnect()

    def message(self, msg):
        """
        Process incoming message stanzas. Be aware that this also
        includes MUC messages and error messages. It is usually
        a good idea to check the messages's type before processing
        or sending replies.

        Arguments:
            msg -- The received message stanza. See the documentation
                   for stanza objects and the Message stanza to see
                   how it may be used.
        """
        # Só processa mensagens depois que 'message_handler' for definido.
        # Ignora mensagens que não sejam 'chat' ou 'normal', por exemplo
        # mensagens de erro.
        if callable(self.message_handler) and msg['type'] in ('chat', 'normal'):
            self.message_handler(msg)
            self.talking_to = msg['from']

    def got_online(self, presence):
        log.debug(u"Entrou: %s" % presence['from'])

    def got_offline(self, presence):
        log.debug(u"Saiu: %s" % presence['from'])

    def changed_status(self, presence):
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
            log.debug(u"Novo apelido: %s (%s)" % (nick, jid))
            # Guarda o nome localmente, mas não salva no servidor XMPP.
            # Se fosse desejável salvar, usar método self.update_roster.
            self.client_roster[jid]['name'] = nick

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


if __name__ == '__main__':
    # Setup the command line arguments.
    optp = OptionParser()

    # Output verbosity options.
    optp.add_option('-q', '--quiet', help='set logging to ERROR',
                    action='store_const', dest='loglevel',
                    const=logging.ERROR, default=logging.INFO)
    optp.add_option('-d', '--debug', help='set logging to DEBUG',
                    action='store_const', dest='loglevel',
                    const=logging.DEBUG, default=logging.INFO)
    optp.add_option('-v', '--verbose', help='set logging to COMM',
                    action='store_const', dest='loglevel',
                    const=5, default=logging.INFO)

    # JID and password options.
    optp.add_option("-j", "--jid", dest="jid",
                    help="JID to use")
    optp.add_option("-p", "--password", dest="password",
                    help="password to use")

    opts, args = optp.parse_args()

    # Setup logging.
    logging.basicConfig(level=opts.loglevel,
                        format='%(levelname)-8s %(message)s')

    if opts.jid is None:
        opts.jid = raw_input("Username: ")
    if opts.password is None:
        opts.password = getpass.getpass("Password: ")

    # Setup the GenericBot and register plugins. Note that while plugins may
    # have interdependencies, the order in which you register them does
    # not matter.
    xmpp = GenericBot(opts.jid, opts.password)
    xmpp.register_plugin('xep_0030') # Service Discovery
    xmpp.register_plugin('xep_0004') # Data Forms
    xmpp.register_plugin('xep_0060') # PubSub
    xmpp.register_plugin('xep_0199') # XMPP Ping

    # If you are working with an OpenFire server, you may need
    # to adjust the SSL version used:
    # xmpp.ssl_version = ssl.PROTOCOL_SSLv3

    # If you want to verify the SSL certificates offered by a server:
    # xmpp.ca_certs = "path/to/ca/cert"

    # Connect to the XMPP server and start processing XMPP stanzas.
    if xmpp.connect():
        # If you do not have the dnspython library installed, you will need
        # to manually specify the name of the server if it does not match
        # the one in the JID. For example, to use Google Talk you would
        # need to use:
        #
        # if xmpp.connect(('talk.google.com', 5222)):
        #     ...
        xmpp.process(block=True)
        print("Done")
    else:
        print("Unable to connect.")
