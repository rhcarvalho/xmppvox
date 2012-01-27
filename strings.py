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
XMPPVOX - módulo de strings

Este módulo contém strings transmitidas para o Papovox.
"""

WELCOME = (u"Olá {nick}, bem-vindo ao XMPPVOX {version}! \n"
           u"Tecle /ajuda para obter ajuda. \n")
ONLINE_CONTACTS_INFO = (u"{amount} {contacts}. \n"
                        u"/l para listar. \n"
                        u"/n para falar com o contato número n. \n")

MSG = u"{body}"
MSG_FROM = u"{sender} disse: {body}"

FIRST_INCOME_MSG_HELP = u". \nDica: tecle /r para falar com {name}"

WARN_MSG_TO_OFFLINE_USER = (u"* {name} está indisponível agora. "
                            u"Talvez a mensagem não tenha sido recebida.")
WARN_MSG_TO_NOBODY = (u"Mensagem não enviada. "
                      u"Com quem deseja falar? \n"
                      u"Tecle /para seguido do número do contato. \n"
                      u"Se não souber o número tecle /lista ou /todos.")

# Comandos

# Prefixo que ativa o modo de comando
CMD_PREFIX = '/'

CMD_UNKNOWN = u"Comando desconhecido: {cmd}"

CMD_HELP1, CMD_HELP2, CMD_HELP3, CMD_HELP4 = (
    u"""\

    Ajuda do XMPPVOX:

    Tecle normalmente termine suas frases com ENTER.
    Cada frase é enviada para apenas um contato.

    """,
    u"""\
    Para saber quais são os contatos disponíveis tecle %(prefix)slista.
    Para saber todos os contatos (inclusive indisponíveis) tecle %(prefix)stodos.
    Para conversar com alguém tecle %(prefix)spara seguido do número do contato.
    """,
    u"""\
    Para falar com a última pessoa que enviou mensagem para você, tecle %(prefix)sresponder.
    Para saber com quem fala agora tecle %(prefix)squem.
    Para adicionar ou remover um contato tecle %(prefix)sadicionar ou %(prefix)sremover seguido do contato.

    """,
    u"""\
    Atalhos para os comandos:
    %(prefix)sajuda = %(prefix)s? .
    %(prefix)slista = %(prefix)sl .
    %(prefix)stodos = %(prefix)st .
    %(prefix)spara = %(prefix)sp ou %(prefix)s seguido de um número.
    %(prefix)sresponder = %(prefix)sr .
    %(prefix)squem = %(prefix)sq .
    %(prefix)sadicionar = %(prefix)sa .

    """,
    )

CMD_WHO = u"Falando com {who}."
CMD_WHO_WARN = u"Falando com ¬ {who} ({warning})."

CMD_LIST_ITEM = u"{number} {name}"
CMD_LIST_ALL_OFFLINE = u"Nenhum contato disponível agora!"

CMD_ALL_ITEM = u"{number} {name}"
CMD_ALL_NOBODY = u"Nenhum contato na sua lista!"

CMD_TO_WRONG_NUMBER = u"Número de contato inexistente! Use %slista." % CMD_PREFIX
CMD_TO_MISSING_NUMBER = u"Faltou número do contato! Use %slista." % CMD_PREFIX

CMD_ADD_OK = u"Adicionei contato: {jid}"
CMD_ADD_FAIL = (u"Não entendi: {invalid_jid}. "
                u"Exemplos: fulano@gmail.com, ou amigo@chat.facebook.com")
