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
import os
import shutil
import subprocess
import sys

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


BUNDLED = getattr(sys, 'frozen', False)


if BUNDLED:
    # we are running in a PyInstaller bundle
    import win32api

    def run_script(name):
        # run "scripvox.exe /path/to/script/name.cmd"
        basedir = sys._MEIPASS
        script = os.path.join(basedir, "%s.cmd" % name)
        return subprocess.call(["scripvox.exe", script], close_fds=True)

    def assert_can_run_launch_script(canonical_exe_name):
        # the launch script needs to call this program again,
        # so we must have the same name as the script expects
        my_name = os.path.basename(sys.executable)
        assert my_name.lower() == canonical_exe_name.lower()
        # the launch script uses relative paths to executables, so we
        # need to ensure that the current working directory is correct
        os.chdir(os.path.dirname(sys.executable))
        # check for required executables for the launch script
        required_executables = ("scripvox.exe", "papovox.exe")
        missing = [exe for exe in required_executables if not os.path.isfile(exe)]
        assert not missing

    def install(destination):
        try:
            shutil.copy2(sys.executable, destination)
            return True
        except:
            return False

    def find_dosvox_root(vals):
        first_executable = vals[0].split(',', 2)[1]
        dosvox_root = os.path.dirname(first_executable)
        return dosvox_root

    def is_program_in_dosvox_menu(exe_name, vals):
        programs = set(os.path.basename(val.split(',', 2)[1]).lower() for val in vals)
        return exe_name.lower() in programs

    def append_to_dosvox_menu(exe_path, keys):
        next_index = max(int(''.join(c for c in key if c.isdigit())) for key in keys) + 1
        new_key = 'Rede%d' % next_index
        new_val = 'X,%s,-RDXMPP,XMPPVOX bate-papo com amigos do Google e Facebook' % (exe_path,)
        win32api.WriteProfileVal("PROGREDE", new_key, new_val, "dosvox.ini")

def main():
    u"""Executa o cliente XMPP e o servidor compatível com Papovox.

    Esta função é o ponto de partida da execução do XMPPVOX."""
    # check if we need to use the launch script
    # the launch script uses ScriptVox to
    # ask the user for JID and password,
    # then calls XMMPVOX again with arguments
    need_launch_script = (BUNDLED and len(sys.argv) == 1)
    if need_launch_script:
        xmppvox_exe = "xmppvox.exe"
        keys = win32api.GetProfileVal("PROGREDE", None, "", "dosvox.ini").split("\x00")[:-1]
        vals = [win32api.GetProfileVal("PROGREDE", key, "", "dosvox.ini") for key in keys]
        # make sure DOSVOX is installed
        dosvox_installed = bool(keys)
        if not dosvox_installed:
            print(u'Não foi possível encontrar a instalação do DOSVOX.\n'
                  u'Antes de usar o XMPPVOX, é preciso instalar o DOSVOX.\n'
                  u'Para mais ajuda, visite http://xmppvox.rodolfocarvalho.net')
            raw_input(u"Pressione qualquer tecla para continuar. . .")
            return 1
        dosvox_root = find_dosvox_root(vals)
        canonical_exe_path = os.path.join(dosvox_root, xmppvox_exe)
        # try to add an entry for XMMPVOX in DOSVOX menu
        if not is_program_in_dosvox_menu(xmppvox_exe, vals):
            append_to_dosvox_menu(canonical_exe_path, keys)
        try:
            assert_can_run_launch_script(xmppvox_exe)
            return run_script("launch")
        except AssertionError:
            if install(canonical_exe_path):
                # run my new self in a another process
                os.spawnl(os.P_NOWAIT, canonical_exe_path, xmppvox_exe)
                return 0
            else:
                print(u'O "%s" deve ficar no diretório onde o DOSVOX foi instalado.\n'
                      u'Para instalar o XMPPVOX, copie ou mova este arquivo para "%s".' %
                      (xmppvox_exe, dosvox_root))
                raw_input(u"Pressione qualquer tecla para continuar. . .")
                return 1
    else:
        # normal execution
        # <config>
        args = parse_command_line()
        configure_logging(args.verbose)
        S.show_code = args.show_code
        # </config>
        host, port = args.host, args.port
        jid, password = get_jid_and_password(args.jid, args.password)
        return start_client_server(host, port, jid, password)

def start_client_server(host, port, jid, password):
    try:
        return _start_client_server(host, port, jid, password)
    except Exception, e:
        log.critical(safe_unicode(e))
        return 1
    finally:
        log.info(u"Fim do XMPPVOX.")

def _start_client_server(host, port, jid, password):
    # Instancia servidor e aguarda conexão do Papovox.
    papovox = server.PapovoxLikeServer(host, port)
    if not papovox.connect():
        log.error(u"Não foi possível conectar ao Papovox.")
        return 1
    try:
        try:
            # Inicia cliente XMPP.
            xmpp = client.BotXMPP(jid, password, papovox)
            # Para especificar o mecanismo de autenticação:
            #xmpp = client.BotXMPP(jid, password, papovox, sasl_mech="X-GOOGLE-TOKEN")
        except sleekxmpp.jid.InvalidJID:
            log.error(u"A conta '%s' é inválida.", jid)
            papovox.sendmessage(S.ERROR_INVALID_JID.format(jid=jid))
            return 1
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
            return 1
        # Envia um PING para o tracker a cada 20 minutos.
        timer = tracker.ping(session_id, 20 * 60)
        try:
            # Tenta conectar ao servidor XMPP.
            if not xmpp.connect():
                return 1
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
        return 0

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

def configure_logging(verbose):
    # Configura logging.
    basic_format = '%(levelname)-8s %(message)s'
    detailed_format = '%(levelname)-8s %(asctime)s [%(module)s:%(lineno)d:%(funcName)s] %(message)s'
    date_format = '%H:%M:%S'
    # Mostra informações mínimas na tela
    if not verbose:
        logging.basicConfig(level=logging.ERROR, format=basic_format, datefmt=date_format)
        logging.getLogger('xmppvox').setLevel(logging.INFO)
    # Gradualmente, mostra mais e mais detalhes
    if verbose >= 1:
        logging.basicConfig(level=logging.ERROR, format=detailed_format, datefmt=date_format)
        logging.getLogger('xmppvox').setLevel(logging.DEBUG)
        logging.getLogger('xmppvox.commands').setLevel(logging.WARNING)
    if verbose >= 2:
        logging.getLogger('xmppvox.commands').setLevel(logging.DEBUG)

def get_jid_and_password(jid, password):
    jid = jid or raw_input("Conta (ex.: fulano@gmail.com): ")
    password = password or getpass.getpass("Senha para %r: " % jid)
    return jid, password


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(1)
