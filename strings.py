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