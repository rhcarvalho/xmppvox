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

from optparse import OptionParser
import getpass

import client
import tracker
import server
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
    papovox = server.PapovoxLikeServer(opts.host, opts.port)

    if papovox.connect():
        jid, password = get_jid_and_password(opts)

        # Inicia cliente XMPP.
        xmpp = client.BotXMPP(jid, password, papovox)
        # Para especificar o mecanismo de autenticação:
        #xmpp = client.BotXMPP(jid, password, papovox, sasl_mech="X-GOOGLE-TOKEN")

        # Valida JID e tenta conectar ao servidor XMPP.
        if xmpp.validate_jid():
            # Cria sessão no tracker.
            session_id = tracker.new_session(jid)

            if xmpp.connect():
                # Executa cliente XMPP em outra thread.
                xmpp.process(block=False)

                # Bloqueia processando mensagens do Papovox.
                # Sem o bloqueio, a thread principal termina e o executável
                # gerado pelo PyInstaller termina prematuramente.
                papovox.process(xmpp)

                # Interrompe cliente XMPP quando Papovox desconectar.
                xmpp.disconnect()

            # Encerra sessão no tracker.
            tracker.close_session(session_id)
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
                    help=u"envia strings codificadas",
                    action='store_true', dest='show_code', default=False)
    # JID e senha
    optp.add_option("-j", "--jid", dest="jid",
                    help="identificador do usuário")
    optp.add_option("-s", "--senha", dest="password",
                    help="senha")
    optp.add_option("--host", type="string", dest="host",
                    help="IP da interface de escuta")
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
    return jid, password


main()
