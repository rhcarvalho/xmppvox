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
XMPPVOX - módulo de utilitários de produção

Este módulo contém rotinas usadas quando o XMPPVOX está sendo executado em produção.
"""

import os
import shutil
import subprocess
import sys
import win32api


def do_the_magic():
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
    # to run external programs we use relative paths, therefore
    # we set the current working directory to a known place
    os.chdir(dosvox_root)
    # try to add an entry for XMMPVOX in DOSVOX menu
    if not is_program_in_dosvox_menu(xmppvox_exe, vals):
        try:
            append_to_dosvox_menu(canonical_exe_path, keys)
        except:
            run_script("failed-append-menu")
        else:
            run_script("success-append-menu")
    try:
        assert_can_run_launch_script(canonical_exe_path)
        return run_script("launch")
    except AssertionError:
        if install(canonical_exe_path):
            run_script("success-install")
            # run my new self in a another process
            os.spawnl(os.P_NOWAIT, canonical_exe_path, xmppvox_exe)
            return 0
        else:
            run_script("failed-install")
            print(u'O "%s" deve ficar no diretório onde o DOSVOX foi instalado.\n'
                  u'Para instalar o XMPPVOX, copie ou mova este arquivo para "%s".' %
                  (xmppvox_exe, dosvox_root))
            raw_input(u"Pressione qualquer tecla para continuar. . .")
            return 1

def run_script(name):
    # run "scripvox.exe /path/to/script/name.cmd"
    basedir = sys._MEIPASS
    script = os.path.join(basedir, "%s.cmd" % name)
    return subprocess.call(["scripvox.exe", script], close_fds=True)

def assert_can_run_launch_script(canonical_exe_path):
    # check that we are the canonical executable
    assert sys.executable.lower() == canonical_exe_path.lower()
    xmppvox_exe = os.path.basename(canonical_exe_path)
    # check for required executables for the launch script
    required_executables = (xmppvox_exe, "scripvox.exe", "papovox.exe")
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
