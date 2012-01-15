# -*- coding: utf-8 -*-
u"""
XMPPVOX - módulo comandos

Este módulo implementa comandos que o servidor reconhece.
"""

import re

from server import sendmessage

import logging
log = logging.getLogger(__name__)


# Prefixo que ativa o modo de comando
PREFIX = '/'

# Origem: http://www.regular-expressions.info/email.html
# Um JID não é um email, mas serve como boa aproximação para o que é
# preciso neste módulo.
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
        (r'(\?|ajuda)\s*$', ajuda),
        (r'q(?:uem)?\s*$', quem),
        (r'l(?:ista)?\s*$', lista),
        (r'lt\s*$', lista_todos),
        (r'p(?:ara)?\s*(\d*)\s*$', para),
        (r'a(?:dicionar)?\s*([^\s*]*)\s*$', adicionar),
        (r'r(?:emover)?\s*([^\s*]*)\s*$', remover),
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
        sendmessage(sock, u"Comando desconhecido: %s" % cmd)
    return True


# Comandos --------------------------------------------------------------------#

def ajuda(sock, xmpp=None, mo=None):
    help = u"""\
    Para ver sua lista de contatos, digite %(prefix)slista
    Para conversar com alguém, digite %(prefix)spara, seguido do número do contato
    Para saber com quem fala agora, digite %(prefix)squem
    Para adicionar ou remover um contato, digite /adicionar ou /remover, seguido do contato
    """ % dict(prefix=PREFIX)
    # Envia uma mensagem por linha/comando
    map(lambda m: sendmessage(sock, m), help.splitlines())

def quem(sock, xmpp, mo=None):
    sendmessage(sock, u"Falando com %s." % (xmpp.last_sender_jid or u"ninguém"))

def lista(sock, xmpp, mo=None):
    u"""Lista contatos disponíveis/online."""
    def is_online((number, roster_item)):
        # Um contato está online se ele está conectado em algum resource.
        return bool(roster_item.resources)
    
    for number, roster_item in filter(is_online, enumerate_roster(xmpp)):
        name = roster_item['name'] or roster_item.jid
        sendmessage(sock, u"%d %s" % (number, name))
    # Se 'number' não está definido, então nenhum contato foi listado.
    try:
        number
    except NameError:
        sendmessage(sock, u"Nenhum contato disponível agora!")

def lista_todos(sock, xmpp, mo=None):
    u"""Lista todos os contatos (online/offline)."""
    for number, roster_item in enumerate_roster(xmpp):
        name = roster_item['name'] or roster_item.jid
        sendmessage(sock, u"%d %s" % (number, name))
    # Se 'number' não está definido, então nenhum contato foi listado.
    try:
        number
    except NameError:
        sendmessage(sock, u"Nenhum contato na sua lista!")

def para(sock, xmpp, mo):
    try:
        number = int(mo.group(1))
        roster_item = dict(enumerate_roster(xmpp)).get(number, None)
        if roster_item is None:
            sendmessage(sock, u"Número de contato inexistente! Use %slista." % PREFIX)
        else:
            xmpp.last_sender_jid = roster_item.jid
    except ValueError:
        sendmessage(sock, u"Faltou número do contato! Use %slista." % PREFIX)
    quem(sock, xmpp)

def adicionar(sock, xmpp, mo):
    email_mo = email_regexp.match(mo.group(1))
    if email_mo is not None:
        user_jid = email_mo.group(0)
        xmpp.send_presence_subscription(pto=user_jid, ptype='subscribe')
        sendmessage(sock, u"Adicionei contato: %s" % user_jid)
    else:
        sendmessage(sock, u"Não entendi: %s. Exemplos: fulano@gmail.com, ou amigo@chat.facebook.com" % mo.group(1))

def remover(sock, xmpp, mo):
    email_mo = email_regexp.match(mo.group(1))
    if email_mo is not None:
        user_jid = email_mo.group(0)
        xmpp.send_presence_subscription(pto=user_jid, ptype='unsubscribe')
        # ... ou talvez usar xmpp.del_roster_item(user_jid)
        sendmessage(sock, u"Removi contato: %s" % user_jid)
    else:
        sendmessage(sock, u"Não entendi: %s. Exemplos: fulano@gmail.com, ou amigo@chat.facebook.com" % mo.group(1))


# Utilitários -----------------------------------------------------------------#

def enumerate_roster(xmpp):
    u"""Enumera minha lista de contatos."""
    roster = xmpp.client_roster
    
    def is_contact(jid):
        u"""Retorna True se 'jid' é meu contato, False caso contrário."""
        # Tipos comuns de subscription:
        # 'both': eu estou na lista do outro e o outro está na minha lista
        # 'to'  : eu *não* estou na lista do outro e o outro está na minha lista
        # 'from': eu estou na lista do outro e o outro *não* está na minha lista
        # 'none': eu mesmo estou no roster com subscription none.
        # 'remove': contato marcado para ser removido.
        #
        # Tipos considerados para formar a lista de contatos:
        subscription_types = ('both', 'to')
        return roster[jid]['subscription'] in subscription_types
    
    # Filtra todos os contatos "válidos" do meu roster.
    roster_items = [roster[jid] for jid in roster if is_contact(jid)]
    return enumerate(roster_items, 1)
