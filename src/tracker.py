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
XMPPVOX - módulo tracker

Este módulo implementa comunicação com servidor central remoto para tracking de
atividade do XMPPVOX.
"""

import json
import os
import platform
import uuid

import logging
log = logging.getLogger(__name__)

import requests

from version import __version__


#TRACKER_URL = "http://xmppvox.rodolfocarvalho.net/api/1/"
TRACKER_URL = "http://localhost:9090/1/"

def read_machine_id(config_path):
    u"""Lê identificador desta máquina num arquivo de configuração."""
    try:
        with open(config_path) as config_file:
            config = json.load(config_file)
            try:
                mid = config.get("machine_id")
            except (ValueError, AttributeError):
                # invalid config file
                mid = None
    except IOError:
        mid = None
    return mid

def write_machine_id(config_path, mid):
    u"""Persiste um identificador para esta máquina num arquivo de configuração."""
    if not os.path.isfile(config_path):
        os.makedirs(os.path.dirname(config_path))
    with open(config_path, "w") as config_file:
        json.dump(dict(machine_id=mid), config_file)

def machine_id():
    u"""Retorna um identificador único para esta máquina/usuário."""
    if platform.system() == "Windows":
        config_path = os.path.expandvars("$APPDATA\\XMPPVOX\\config.json")
    else:
        config_path = os.path.expanduser("~/.xmppvox/config.json")
    mid = read_machine_id(config_path)
    if mid is None:
        mid = str(uuid.uuid4())
        write_machine_id(config_path, mid)
    return mid

MACHINE_ID = machine_id()

def new_session(jid):
    u"""Cria uma nova sessão no tracker central do XMPPVOX."""
    try:
        r = requests.post("{}session/new".format(TRACKER_URL),
                          data=dict(jid=jid,
                                    machine_id=MACHINE_ID,
                                    xmppvox_version=__version__))
        r.raise_for_status()
        session_id = r.text.strip()
        log.debug(u"Identificador de sessão do XMPPVOX: %s" % session_id)
    except requests.exceptions.RequestException, e:
        session_id = None
        log.error(u"Falha ao obter identificador de sessão: %s" % e)
    return session_id

def close_session(session_id):
    u"""Encerra uma sessão no tracker central do XMPPVOX."""
    try:
        r = requests.post("{}session/close".format(TRACKER_URL),
                          data=dict(session_id=session_id,
                                    machine_id=MACHINE_ID))
        r.raise_for_status()
        session_id = r.text.strip()
        log.debug(u"Sessão encerrada: %s" % session_id)
    except requests.exceptions.RequestException, e:
        session_id = None
        log.error(u"Falha ao encerrar sessão: %s" % e)
    return session_id
