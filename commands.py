# -*- coding: utf-8 -*-
u"""
XMPPVOX - módulo comandos

Este módulo implementa comandos que o servidor reconhece.
"""

import re

from server import sendmessage

import logging
log = logging.getLogger(__name__)

def process_commands(sock, xmpp, data):
    def is_friend(jid):
        return xmpp.client_roster[jid]['subscription'] in ('both', 'to', 'from')
    
    if data.startswith("?quem"):
        log.debug("[comando ?quem]")
        for f, friend in enumerate(filter(is_friend, xmpp.client_roster), 1):
            name = xmpp.client_roster[friend]['name'] or xmpp.client_roster[friend].jid
            subscription = xmpp.client_roster[friend]['subscription']
            extra = u""
            if subscription == 'to':
                extra = u" * não estou na lista deste contato."
            elif subscription == 'from':
                extra = u" * este contato me adicionou mas não autorizei."
            sendmessage(sock, u"%d %s%s" % (f, name, extra))
        return True
    elif data.startswith("?para"):
        log.debug("[comando ?para]")
        mo = re.match(r"\?para (\d+)", data)
        if mo is None:
            sendmessage(sock, u"Faltou número do contato! Use ?quem.")
        else:
            idx = int(mo.group(1))
            xmpp.last_sender = dict(enumerate(filter(is_friend, xmpp.client_roster), 1)).get(idx, None)
            if xmpp.last_sender is None:
                sendmessage(sock, u"Número de contato inexistente! Use ?quem.")
        sendmessage(sock, u"Agora estou falando com %s." % (xmpp.last_sender or u"ninguém"))
        return True
    else:
        return False
