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

from threading import Event

from optparse import OptionParser
import getpass

import client
import server

import logging
log = logging.getLogger(__name__)


def main():
    u"""Executa o cliente XMPP e o servidor compatível com Papovox.

    Esta função é o ponto de partida da execução do XMPPVOX."""
    # Configuração.
    opts, args = parse_command_line()
    configure_logging(opts)
    jid, password = get_jid_and_password(opts)

    # Mecanismo para interromper o servidor quando necessário
    stop = Event()
    def do_stop():
        log.debug(u"Interrompendo a conexão com o Papovox...")
        stop.set()

    # Inicia cliente XMPP.
    xmpp = client.BotXMPP(jid, password, do_stop)
    if xmpp.connect():
        log.info(u"Conectado ao servidor XMPP")
        # Executa cliente XMPP em outra thread.
        xmpp.process(block=False)

    # Bloqueia executando o servidor para o Papovox.
    server.run(xmpp, stop)


def parse_command_line():
    u"""Processa opções de linha de comando passadas para o XMPPVOX."""
    optp = OptionParser()
    # Configuração de verbosidade.
    optp.add_option('-q', '--quiet', help=u"exibe apenas erros",
                    action='store_const', dest='loglevel',
                    const=logging.ERROR, default=logging.INFO)
    optp.add_option('-d', '--debug', help=u"exibe mensagens de depuração",
                    action='store_const', dest='loglevel',
                    const=logging.DEBUG, default=logging.INFO)
    # JID e senha
    optp.add_option("-j", "--jid", dest="jid",
                    help="identificador do usuário")
    optp.add_option("-p", "--password", dest="password",
                    help="senha")
    return optp.parse_args()

def configure_logging(opts):
    # Configura logging.
    logging.basicConfig(level=opts.loglevel,
                        format='%(levelname)-8s %(asctime)s %(message)s',
                        datefmt='%H:%M')
    # Não mostrar mensagens de DEBUG do SleekXMPP.
    logging.getLogger('sleekxmpp').setLevel(max(logging.INFO, opts.loglevel))

def get_jid_and_password(opts):
    jid = opts.jid or raw_input("Conta (ex.: fulano@gmail.com): ")
    password = opts.password or getpass.getpass("Senha para %r: " % jid)
    return jid, password


main()
