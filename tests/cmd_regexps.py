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

import re

add = re.compile(r'a(?:dicionar)?(?:\s+([^\s*]*)\s*)?$', re.I)

assert add.match('adicionar')
assert add.match('adicionar tereza@gmail.com')

without_jid = add.match('a')
with_jid = add.match('a tereza@gmail.com')
with_spaces = add.match('a     ')
with_jid_and_spaces = add.match('a   tereza@gmail.com   ')
assert without_jid
assert with_jid
assert with_spaces
assert with_jid_and_spaces

assert not without_jid.group(1)
assert with_jid.group(1) == 'tereza@gmail.com'
assert not with_spaces.group(1)
assert with_jid_and_spaces.group(1) == 'tereza@gmail.com'

assert not add.match('adicionartereza@gmail.com')
assert not add.match('atereza@gmail.com')

print '/adicionar..............ok'


to = re.compile(r'(?:p(?:ara)?)?\s*(\d*)\s*$', re.I)

assert to.match('para')
assert to.match('p')
assert to.match('')
assert to.match('  ')
assert to.match('23')
assert to.match('  23')
assert to.match('  23  ')
assert to.match('23  ')
assert to.match('para 23')
assert to.match('p 23')

#assert not to.match('para23')
#assert not to.match('p23')

print '/para...................ok'
