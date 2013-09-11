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

class get_string(object):
    u"""Retorna uma string marcada para ser interpretada pelo Papovox."""
    _show_code = False

    @property
    def show_code(self):
        return self._show_code
    @show_code.setter
    def show_code(self, value):
        self._show_code = bool(value)

    def __getattr__(self, attr):
        # Suporte à sintaxe get_string.SOME_STRING
        s = globals()[attr]
        if isinstance(s, tuple):
            if self.show_code:
                return u"%{:03d} {}".format(*s)
            else:
                return s[1]
        elif isinstance(s, basestring):
            return s
        else:
            raise AttributeError

    # Suporte à sintaxe get_string(SOME_STRING)
    __call__ = __getattr__

# get_string é um objeto especial para ser usado como função ou para acessar
# seus atributos. As duas sintaxes tem o mesmo efeito.
get_string = get_string()

#------------------------------------------------------------------------------#
# As strings aqui definidas devem ser usadas através do 'get_string'.

# Mensagens gerais ------------------------------------------------------------#
WELCOME = (0, u"Olá {nick}, bem-vindo ao XMPPVOX {version}! \n"
              u"Tecle /ajuda para obter ajuda. \n")
ONLINE_CONTACTS_INFO = (1, u"{amount} {contacts}. \n"
                           u"/l para listar. \n"
                           u"/n para falar com o contato número n. \n")

FIRST_INCOME_MSG_HELP = (2, u". \nDica: tecle /r para falar com {name}.")

# Conversação -----------------------------------------------------------------#
MSG_FROM = (101, u"{sender} disse: {body}")
MSG = (102, u"{body}")

# Comandos --------------------------------------------------------------------#

# Prefixo que ativa o modo de comando
CMD_PREFIX = '/'

CMD_UNKNOWN = (200, u"Comando desconhecido: {cmd}")

CMD_HELP1, CMD_HELP2, CMD_HELP3, CMD_HELP4 = (
    (211, u"""\

    Ajuda do XMPPVOX:

    Tecle normalmente, termine suas frases com ENTER.
    Cada frase é enviada para apenas um contato.

    """),
    (212, u"""\
    Para saber quais são os contatos disponíveis tecle {prefix}lista.
    Para saber todos os contatos (inclusive indisponíveis) tecle {prefix}todos.
    Para conversar com alguém tecle {prefix}para seguido do número do contato.
    """),
    (213, u"""\
    Para falar com a última pessoa que enviou mensagem para você, tecle {prefix}responder.
    Para saber com quem fala agora tecle {prefix}quem.
    Para adicionar ou remover um contato tecle {prefix}adicionar ou {prefix}remover seguido do contato.

    """),
    (214, u"""\
    Atalhos para os comandos:
    {prefix}ajuda = {prefix}? .
    {prefix}lista = {prefix}l .
    {prefix}todos = {prefix}t .
    {prefix}para = {prefix}p ou {prefix} seguido de um número.
    {prefix}responder = {prefix}r .
    {prefix}quem = {prefix}q .
    {prefix}adicionar = {prefix}a .

    """),
    )

CMD_WHO = (220, u"Falando com {who}.")
CMD_WHO_WARN = (121, u"Falando com ¬ {who} ({warning}).")

CMD_LIST_ITEM = (230, u"{number} {name}")
CMD_LIST_ALL_OFFLINE = (131, u"Nenhum contato disponível agora!")

CMD_ALL_ITEM = (240, u"{number} {name}")
CMD_ALL_NOBODY = (241, u"Nenhum contato na sua lista!")

CMD_TO_WRONG_NUMBER = (250, u"Número de contato inexistente! Use %slista." % CMD_PREFIX)
CMD_TO_MISSING_NUMBER = (251, u"Faltou número do contato! Use %slista." % CMD_PREFIX)

CMD_ADD_OK = (260, u"Adicionei contato: {jid}.")
CMD_ADD_FAIL = (261, u"Não entendi: {invalid_jid}. "
                     u"Exemplos: \n/a fulano@gmail.com, ou \n/a amigo@chat.facebook.com")

CMD_DEL_OK = (270, u"Removi contato: {jid}.")
CMD_DEL_FAIL = (271, u"Não entendi: {invalid_jid}. "
                     u"Exemplos: \n/remover fulano@gmail.com, ou \n/remover amigo@chat.facebook.com")

# Avisos ----------------------------------------------------------------------#
WARN_MSG_TO_OFFLINE_USER = (801, u"* {name} está indisponível agora. "
                                 u"Talvez a mensagem não tenha sido recebida.")
WARN_MSG_TO_NOBODY = (802, u"Mensagem não enviada. "
                           u"Com quem deseja falar? \n"
                           u"Tecle /para seguido do número do contato. \n"
                           u"Se não souber o número tecle /lista ou /todos.")

# Erros -----------------------------------------------------------------------#
ERROR_NO_AUTH = (901, u"Erro: usuário ou senha incorretos.")
ERROR_INVALID_JID = (902, u"Erro: conta inválida ({jid}).")
ERROR_SOCKET_ERROR = (903, u"Erro: falha na conexão com o servidor {host}.")
