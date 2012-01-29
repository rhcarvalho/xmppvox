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

import sys

from optparse import OptionParser
import getpass

import client
import server
import commands
import strings

import logging
log = logging.getLogger(__name__)


def main():
    u"""Executa o cliente XMPP e o servidor compatível com Papovox.

    Esta função é o ponto de partida da execução do XMPPVOX."""
    # Configuração.
    opts, args = parse_command_line()
    configure_logging(opts)
    strings.get_string.show_code = opts.show_code

    # Instancia servidor e aguarda conexão do Papovox.
    papovox = server.PapovoxLikeServer(opts.port)
    if papovox.connect():
        jid, password = get_jid_and_password(opts)

        # Inicia cliente XMPP.
        xmpp = client.BotXMPP(jid, password, papovox)
        #xmpp = client.BotXMPP(jid, password, papovox, sasl_mech="X-GOOGLE-TOKEN")

        log.info(u"Tentando conectar ao servidor %s...", xmpp.boundjid.host)
        if xmpp.connect():
            log.info(u"Conectado ao servidor %s", xmpp.boundjid.host)

            xmpp.event('papovox_connected',
                       {'nick': papovox.nickname,
                        'message_handler': papovox.new_message_handler(xmpp)})  # FIXME direct=True

            # Executa cliente XMPP em outra thread.
            xmpp.process(block=False)

            # Bloqueia processando mensagens do Papovox.
            # Sem o bloqueio, a thread principal termina e o executável
            # gerado pelo PyInstaller termina prematuramente.
            papovox.process(xmpp)

            xmpp.event('papovox_disconnected')
    else:
        log.error(u"Erro: Não foi possível conectar ao Papovox.")
    log.info(u"Fim do XMPPVOX")


def parse_command_line():
    u"""Processa opções de linha de comando passadas para o XMPPVOX."""
    optp = OptionParser()
    # Configuração de verbosidade.
    optp.add_option('-d', '--debug',
                    help=u"exibe mais detalhes sobre a execução",
                    action='store_const', dest='loglevel',
                    const=logging.DEBUG, default=logging.INFO)
    # Configuração de strings.
    optp.add_option('-c', '--codificar',
                    help=u"mostra mensagens codificadas para o Papovox",
                    action='store_true', dest='show_code', default=False)
    # JID e senha
    optp.add_option("-j", "--jid", dest="jid",
                    help="identificador do usuário")
    optp.add_option("-s", "--senha", dest="password",
                    help="senha")
    optp.add_option("-p", "--porta", type="int", dest="port",
                    help="porta de escuta")
    return optp.parse_args()

def configure_logging(opts):
    # Configura logging.
    logging.basicConfig(level=opts.loglevel,
                        format='%(levelname)-8s %(asctime)s %(message)s',
                        datefmt='%H:%M')
    # Não mostrar mensagens de DEBUG do SleekXMPP.
    if opts.loglevel == logging.DEBUG:
        logging.getLogger('sleekxmpp').setLevel(logging.INFO)
    else:
        logging.getLogger('sleekxmpp').setLevel(logging.WARNING)

def get_jid_and_password(opts):
    jid = opts.jid or raw_input("Conta (ex.: fulano@gmail.com): ")
    password = opts.password or getpass.getpass("Senha para %r: " % jid)
    if commands.email_regexp.match(jid) is None:
        log.error(u"Usuário inválido '%s'.\n"
                  u"Exemplos: paulo@gmail.com, marcio@chat.facebook.com, "
                  u"regina@jabber.org", jid)
        sys.exit(1)
    return jid, password


main()
