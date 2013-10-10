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

import sleekxmpp

from xmppvox import client
from xmppvox import tracker
from xmppvox import server
from xmppvox.strings import safe_unicode, get_string as S

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
    S.show_code = args.show_code
    try:
        return _main(args)
    except Exception, e:
        log.critical(safe_unicode(e))
        return 42
    finally:
        log.info(u"Fim do XMPPVOX.")

def _main(args):
    # Instancia servidor e aguarda conexão do Papovox.
    papovox = server.PapovoxLikeServer(args.host, args.port)
    if not papovox.connect():
        log.error(u"Não foi possível conectar ao Papovox.")
        return 1
    try:
        jid, password = get_jid_and_password(args)
        try:
            # Inicia cliente XMPP.
            xmpp = client.BotXMPP(jid, password, papovox)
            # Para especificar o mecanismo de autenticação:
            #xmpp = client.BotXMPP(jid, password, papovox, sasl_mech="X-GOOGLE-TOKEN")
        except sleekxmpp.jid.InvalidJID:
            log.error(u"A conta '%s' é inválida.", jid)
            papovox.sendmessage(S.ERROR_INVALID_JID.format(jid=jid))
            return 2
        # Verifica JID.
        if not xmpp.validate_jid():
            log.warn(u"A conta '%s' parece ser inválida.", jid)
            # Avisa ao Papovox que o JID é inválido.
            papovox.sendmessage(S.WARN_INVALID_JID.format(jid=jid))
        # Cria sessão no tracker.
        session_id, message = tracker.new_session(jid)
        if message is not None:
            papovox.sendmessage(message)
        if session_id is None:
            return 3
        # Envia um PING para o tracker a cada 20 minutos.
        timer = tracker.ping(session_id, 20 * 60)
        try:
            # Tenta conectar ao servidor XMPP.
            if not xmpp.connect():
                return 4
            try:
                # Executa cliente XMPP em outra thread.
                xmpp.process(block=False)
                # Bloqueia processando mensagens do Papovox.
                # Sem o bloqueio, a thread principal termina e o executável
                # gerado pelo PyInstaller termina prematuramente.
                papovox.process(xmpp)
            finally:
                # Interrompe cliente XMPP quando Papovox desconectar.
                xmpp.disconnect()
        finally:
            # Cancela envio de PINGs para o tracker.
            timer.cancel()
            # Encerra sessão no tracker.
            tracker.close_session(session_id)
    finally:
        papovox.disconnect()

def parse_command_line():
    u"""Processa opções de linha de comando passadas para o XMPPVOX."""
    parser = argparse.ArgumentParser(description='XMPPVOX: cliente de bate-papo XMPP para o DOSVOX.')
    # Configuração de verbosidade.
    parser.add_argument('-v', '--verbose',
                        help=u"exibe mais detalhes sobre a execução",
                        action='count', dest='verbose')
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
    basic_format = '%(levelname)-8s %(message)s'
    detailed_format = '%(levelname)-8s %(asctime)s [%(module)s:%(lineno)d:%(funcName)s] %(message)s'
    date_format = '%H:%M:%S'
    # Mostra informações mínimas na tela
    if not args.verbose:
        logging.basicConfig(level=logging.ERROR, format=basic_format, datefmt=date_format)
        logging.getLogger('xmppvox').setLevel(logging.INFO)
    # Gradualmente, mostra mais e mais detalhes
    if args.verbose >= 1:
        logging.basicConfig(level=logging.ERROR, format=detailed_format, datefmt=date_format)
        logging.getLogger('xmppvox').setLevel(logging.DEBUG)
        logging.getLogger('xmppvox.commands').setLevel(logging.WARNING)
    if args.verbose >= 2:
        logging.getLogger('xmppvox.commands').setLevel(logging.DEBUG)

def get_jid_and_password(args):
    jid = args.jid or raw_input("Conta (ex.: fulano@gmail.com): ")
    password = args.password or getpass.getpass("Senha para %r: " % jid)
    return jid, password


if __name__ == "__main__":
    import sys
    sys.exit(main())
