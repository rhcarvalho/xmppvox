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

import requests

from version import __version__


#TRACKER_URL = "http://xmppvox.rodolfocarvalho.net/api/1/"
TRACKER_URL = "http://localhost:9090/1/"
MACHINE_ID = "de63fa34-2f5c-11e3-821a-60fb42f754da"


def new_session(jid):
    u"""Cria uma nova sessão no tracker central do XMPPVOX."""
    r = requests.post("{}session/new".format(TRACKER_URL),
                      data=dict(jid=jid,
                                machine_id=MACHINE_ID,
                                xmppvox_version=__version__))
    return r.text.strip()

def close_session(session_id):
    u"""Encerra uma sessão no tracker central do XMPPVOX."""
    r = requests.post("{}session/close".format(TRACKER_URL),
                      data=dict(session_id=session_id,
                                machine_id=MACHINE_ID))
    return r.text.strip()
