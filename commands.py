# -*- coding: utf-8 -*-
u"""
XMPPVOX - módulo comandos

Este módulo implementa comandos que o servidor reconhece.
"""

import re

import server

import logging
log = logging.getLogger(__name__)


# Prefixo que ativa o modo de comando
PREFIX = '/'

# Origem: http://www.regular-expressions.info/email.html
email_regexp = re.compile(r'^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$', re.I)


def process_command(sock, xmpp, data):
    u"""Tenta processar algum comando contido em 'data'.
    
    Retorna um booleano indicando se algum comando foi executado.
    """
    if not data.startswith(PREFIX):
        return False
    # Remove prefixo
    cmd = data[len(PREFIX):]
    
    # Comandos disponíveis. Cada comando é uma tupla:
    #   (expressão regular, função)
    # As expressões regulares são testadas em ordem e o primeiro comando que der
    # match é executado. Os comandos posteriores não são testados.
    commands = (
        (r'q(?:uem)?\s*$', quem),
        (r'l(?:ista)?\s*$', lista),
        (r'p(?:ara)?\s*(\d*)\s*$', para),
        (r'a(?:dicionar)?\s*([^\s*]*)\s*$', adicionar),
    )
    
    # Tenta encontrar um comando dentre os existentes
    for cmd_re, cmd_func in commands:
        mo = re.match(cmd_re, cmd)
        # Se o comando for encontrado...
        if mo is not None:
            log.debug("[comando %s]" % cmd_func.__name__)
            # ... executa o comando e encerra o loop
            cmd_func(sock, xmpp, mo)
            break
    else:
        # Nenhum comando foi executado no loop
        server.sendmessage(sock, u"Comando desconhecido: %s" % cmd)
    return True


# Comandos --------------------------------------------------------------------#

def quem(sock, xmpp, mo=None):
    server.sendmessage(sock, u"Falando com %s." % (xmpp.last_sender or u"ninguém"))

def lista(sock, xmpp, mo=None):
    for number, friend in enumerate_friends(xmpp):
        name = xmpp.client_roster[friend]['name'] or xmpp.client_roster[friend].jid
        subscription = xmpp.client_roster[friend]['subscription']
        extra = u""
        if subscription == 'to':
            extra = u" * não estou na lista deste contato."
        elif subscription == 'from':
            extra = u" * este contato me adicionou mas não autorizei."
        server.sendmessage(sock, u"%d %s%s" % (number, name, extra))
    else:
        # FIXME
        server.sendmessage(sock, u"Nenhum contato na sua lista!")

def para(sock, xmpp, mo):
    try:
        number = int(mo.group(1))
        friend = dict(enumerate_friends(xmpp)).get(number, None)
        if friend is None:
            server.sendmessage(sock, u"Número de contato inexistente! Use %slista." % PREFIX)
        else:
            xmpp.last_sender = friend
    except ValueError:
        server.sendmessage(sock, u"Faltou número do contato! Use %slista." % PREFIX)
    quem(sock, xmpp)

def adicionar(sock, xmpp, mo):
    email_mo = email_regexp.match(mo.group(1))
    if email_mo is not None:
        user_jid = email_mo.group(0)
        xmpp.send_presence_subscription(pto=user_jid, ptype='subscribe')
        server.sendmessage(sock, u"Adicionei contato: %s" % user_jid)
    else:
        server.sendmessage(sock, u"Usuário inválido: %s\nExemplos: fulano@gmail.com, ou amigo@chat.facebook.com" % mo.group(1))


# Utilitários -----------------------------------------------------------------#

def enumerate_friends(xmpp, start=1):
    def is_friend(jid):
        return xmpp.client_roster[jid]['subscription'] in ('both', 'to', 'from')
    return enumerate(filter(is_friend, xmpp.client_roster), start)
