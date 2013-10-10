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

import argparse
import getpass

from xmppvox import client
from xmppvox import tracker
from xmppvox import server
from xmppvox import strings

import logging
log = logging.getLogger('xmppvox')

# import apenas para ajudar o PyInstaller a detectar dependências do projeto.
import _pyinstaller
del _pyinstaller


def main():
    u"""Executa o cliente XMPP e o servidor compatível com Papovox.

    Esta função é o ponto de partida da execução do XMPPVOX."""
    # Configuração.
    args = parse_command_line()
    configure_logging(args)
    strings.get_string.show_code = args.show_code

    # Instancia servidor e aguarda conexão do Papovox.
    papovox = server.PapovoxLikeServer(args.host, args.port)

    if papovox.connect():
        jid, password = get_jid_and_password(args)

        # Inicia cliente XMPP.
        xmpp = client.BotXMPP(jid, password, papovox)
        # Para especificar o mecanismo de autenticação:
        #xmpp = client.BotXMPP(jid, password, papovox, sasl_mech="X-GOOGLE-TOKEN")

        # Valida JID e tenta conectar ao servidor XMPP.
        if xmpp.validate_jid():
            # Cria sessão no tracker.
            session_id, message = tracker.new_session(jid)

            if message is not None:
                papovox.sendmessage(message)

            if session_id is not None:
                # Envia um PING para o tracker a cada 20 minutos.
                timer = tracker.ping(session_id, 20 * 60)

                if xmpp.connect():
                    # Executa cliente XMPP em outra thread.
                    xmpp.process(block=False)

                    # Bloqueia processando mensagens do Papovox.
                    # Sem o bloqueio, a thread principal termina e o executável
                    # gerado pelo PyInstaller termina prematuramente.
                    papovox.process(xmpp)

                    # Interrompe cliente XMPP quando Papovox desconectar.
                    xmpp.disconnect()

                # Cancela envio de PINGs para o tracker.
                timer.cancel()
                # Encerra sessão no tracker.
                tracker.close_session(session_id)
            else:
                papovox.disconnect()
    else:
        log.error(u"Não foi possível conectar ao Papovox.")
    log.info(u"Fim do XMPPVOX.")


def parse_command_line():
    u"""Processa opções de linha de comando passadas para o XMPPVOX."""
    parser = argparse.ArgumentParser(description='XMPPVOX: cliente de bate-papo XMPP para o DOSVOX.')
    # Configuração de verbosidade.
    parser.add_argument('-d', '--debug',
                        help=u"exibe mais detalhes sobre a execução",
                        action='store_const', dest='loglevel',
                        const=logging.DEBUG, default=logging.INFO)
    # Configuração de strings.
    parser.add_argument('-c', '--codificar',
                        help=u"envia strings codificadas",
                        action='store_true', dest='show_code', default=False)
    # JID e senha
    parser.add_argument("-j", "--jid", dest="jid",
                        help="identificador do usuário")
    parser.add_argument("-s", "--senha", dest="password",
                        help="senha", metavar="XXX")
    parser.add_argument("--host", help="IP da interface de escuta")
    parser.add_argument("-p", "--porta", type=int, dest="port",
                        help="porta de escuta", metavar="XXX")
    return parser.parse_args()

def configure_logging(args):
    # Configura logging.
    if args.loglevel == logging.DEBUG:
        _format = '%(levelname)-8s %(asctime)s [%(module)s:%(lineno)d:%(funcName)s] %(message)s'
    else:
        _format = '%(levelname)-8s %(message)s'
    logging.basicConfig(format=_format,
                        datefmt='%H:%M:%S')
    logging.getLogger('xmppvox').setLevel(args.loglevel)

def get_jid_and_password(args):
    jid = args.jid or raw_input("Conta (ex.: fulano@gmail.com): ")
    password = args.password or getpass.getpass("Senha para %r: " % jid)
    return jid, password


main()
