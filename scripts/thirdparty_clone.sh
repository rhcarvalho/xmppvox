#!/bin/bash

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


# Use este script para baixar as dependencias do XMPPVOX.
# Depois de baixar em algum diret髍io de sua preferencia, instale
# no Python usando:
#    pip install -e ..../dnspython
#    pip install -e ..../SleekXMPP

if test -z "$1"
then
    echo "Uso: $0 lib-dir."
    exit 1
fi

pushd $1

git clone git://github.com/rthalley/dnspython.git
git clone git://github.com/fritzy/SleekXMPP.git

# Muda para o branch de desenvolvimento do SleekXMPP, o mais atualizado.
pushd SleekXMPP
git checkout develop
popd

popd
