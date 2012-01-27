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
XMPPVOX - módulo comandos

Este módulo implementa comandos que o servidor reconhece.
"""

import re
import textwrap

import server
import strings as S

import logging
log = logging.getLogger(__name__)


# Origem: http://www.regular-expressions.info/email.html
# Um JID não é um email, mas serve como boa aproximação para o que é
# preciso neste módulo.
email_regexp = re.compile(r'^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$', re.I)


def process_command(sock, xmpp, data):
    u"""Tenta processar algum comando contido em 'data'.

    Retorna um booleano indicando se algum comando foi executado.
    """
    if not data.startswith(S.CMD_PREFIX):
        return False
    # Remove prefixo
    cmd = data[len(S.CMD_PREFIX):]

    # Comandos disponíveis. Cada comando é uma tupla:
    #   (expressão regular, função)
    # As expressões regulares são testadas em ordem e o primeiro comando que der
    # match é executado. Os comandos posteriores não são testados.
    # Não é feita distinção entre maiúsculas e minúsculas.
    commands = (
        (r'(\?|ajuda)\s*$', ajuda),
        (r'q(?:uem)?\s*$', quem),
        (r'l(?:ista)?\s*$', lista),
        (r't(?:odos)?\s*$', todos),
        (r'(?:p(?:ara)?)?\s*(\d*)\s*$', para),
        (r'r(?:esponder)?\s*$', responder),
        (r'a(?:dicionar)?\s*([^\s*]*)\s*$', adicionar),
        (r'remover\s*([^\s*]*)\s*$', remover),
    )

    # Tenta encontrar um comando dentre os existentes
    for cmd_re, cmd_func in commands:
        mo = re.match(cmd_re, cmd, re.I)
        # Se o comando for encontrado...
        if mo is not None:
            log.debug("[comando %s]" % cmd_func.__name__)
            # ... executa o comando e encerra o loop
            cmd_func(sock, xmpp, mo)
            break
    else:
        # Nenhum comando foi executado no loop
        server.sendmessage(sock, S.CMD_UNKNOWN.format(cmd=cmd))
    return True


# Comandos --------------------------------------------------------------------#

def ajuda(sock, xmpp=None, mo=None):
    # Ajuda dividida em blocos para facilitar a leitura.
    help = (S.CMD_HELP1, S.CMD_HELP2, S.CMD_HELP3, S.CMD_HELP4)
    def send_help(help):
        # Completa string com o prefixo de comando.
        help = help % dict(prefix=S.CMD_PREFIX)
        # Adiciona espaço em branco no fim das linhas para que o Papovox leia
        # corretamente. Sem espaço ele lê "ponto".
        help = u" \n".join(textwrap.dedent(help).splitlines())
        # Envia uma única mensagem. Sua leitura pode ser interrompida no
        # Papovox usando Backspace.
        server.sendmessage(sock, help)
    map(send_help, help)

def quem(sock, xmpp, mo=None):
    warning = u""
    if xmpp.talking_to is None:
        # Caso 1: nenhuma conversa iniciada.
        who =  u"ninguém"
    else:
        # O bare_jid é algo do tipo fulano@gmail.com.
        bare_jid = xmpp.get_bare_jid(xmpp.talking_to)
        roster = xmpp.client_roster
        if bare_jid in roster and roster[bare_jid]['name']:
            # Caso 2: contato no meu roster e com nome.
            # Fulano da Silva (fulano@gmail.com)
            who = u"%s (%s)" % (roster[bare_jid]['name'], bare_jid)
        else:
            # Caso 3: contato não está no meu roster ou está sem nome.
            # Usa o bare JID (fulano@gmail.com)
            who = bare_jid

        # Adiciona número do contato se ele está no roster
        if bare_jid in roster:
            jid2number = dict([ri.jid, n] for n, ri in enumerate_roster(xmpp))
            number = jid2number.get(bare_jid)
            if number:
                who = u"%d %s" % (number, who)

        # Verifica se algum aviso adicional deve ser dado.
        if bare_jid not in roster:
            warning = u"não está na minha lista de contatos"
        elif not roster[bare_jid].resources:
            warning = u"não está disponível agora"
    if not warning:
        server.sendmessage(sock, S.CMD_WHO.format(who=who))
    else:
        server.sendmessage(sock, S.CMD_WHO_WARN.format(who=who,
                                                       warning=warning))

def lista(sock, xmpp, mo=None):
    u"""Lista contatos disponíveis/online."""
    for number, roster_item in enumerate_online_roster(xmpp):
        name = roster_item['name'] or roster_item.jid
        server.sendmessage(sock, S.CMD_LIST_ITEM.format(number=number,
                                                        name=name))
    # Se 'number' não está definido, então nenhum contato foi listado.
    try:
        number
    except NameError:
        server.sendmessage(sock, S.CMD_LIST_ALL_OFFLINE)

def todos(sock, xmpp, mo=None):
    u"""Lista todos os contatos (online/offline)."""
    for number, roster_item in enumerate_roster(xmpp):
        name = roster_item['name'] or roster_item.jid
        server.sendmessage(sock, S.CMD_ALL_ITEM.format(number=number,
                                                       name=name))
    # Se 'number' não está definido, então nenhum contato foi listado.
    try:
        number
    except NameError:
        server.sendmessage(sock, S.CMD_ALL_NOBODY)

def para(sock, xmpp, mo):
    try:
        number = int(mo.group(1))
        roster_item = dict(enumerate_roster(xmpp)).get(number, None)
        if roster_item is None:
            server.sendmessage(sock, S.CMD_TO_WRONG_NUMBER)
        else:
            xmpp.talking_to = roster_item.jid
    except ValueError:
        server.sendmessage(sock, S.CMD_TO_MISSING_NUMBER)
    quem(sock, xmpp)

def responder(sock, xmpp, mo=None):
    if xmpp.last_sender is not None:
        xmpp.talking_to = xmpp.last_sender
    quem(sock, xmpp)

def adicionar(sock, xmpp, mo):
    maybe_jid = mo.group(1)
    email_mo = email_regexp.match(maybe_jid)
    if email_mo is not None:
        user_jid = email_mo.group(0)
        xmpp.send_presence_subscription(pto=user_jid,
                                        ptype='subscribe',
                                        pnick=xmpp.nickname)
        server.sendmessage(sock, S.CMD_ADD_OK.format(jid=user_jid))
    else:
        server.sendmessage(sock, S.CMD_ADD_FAIL.format(invalid_jid=maybe_jid))

def remover(sock, xmpp, mo):
    maybe_jid = mo.group(1)
    email_mo = email_regexp.match(maybe_jid)
    if email_mo is not None:
        user_jid = email_mo.group(0)
        xmpp.send_presence_subscription(pto=user_jid, ptype='unsubscribe')
        # ... ou talvez usar xmpp.del_roster_item(user_jid)
        server.sendmessage(sock, S.CMD_DEL_OK.format(jid=user_jid))
    else:
        server.sendmessage(sock, S.CMD_DEL_FAIL.format(invalid_jid=maybe_jid))


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
    # Ordena por JID
    roster_items.sort(key=lambda item: item.jid)
    return enumerate(roster_items, 1)

def enumerate_online_roster(xmpp):
    u"""Enumera minha lista de contatos que estão online."""
    def is_online((number, roster_item)):
        # Um contato está online se ele está conectado em algum resource.
        return bool(roster_item.resources)
    return filter(is_online, enumerate_roster(xmpp))
