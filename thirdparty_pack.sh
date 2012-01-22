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


# Use este script para preparar as dependencias do XMPPVOX para serem
# distribuidas com o PyInstaller.


if test -z "$1"
then
    echo "Uso: $0 lib-dir."
    exit 1
fi

if test ! -d "$1/dnspython"
then
    echo "Falta dependencia: dnspython"
    exit 2
fi

if test ! -d "$1/SleekXMPP"
then
    echo "Falta dependencia: SleekXMPP"
    exit 3
fi

out=$PWD/thirdparty

pushd $1

# Compila codigo-fonte e comprime apenas o byte-code em um zip.
pushd dnspython
python -m compileall dns
zip -v -9 -r "$out/dnspython-$(git name-rev --name-only HEAD)-$(git rev-parse --short HEAD).zip" dns -x \*.py
popd

# Compila codigo-fonte e comprime apenas o byte-code em um zip.
pushd SleekXMPP
python -m compileall sleekxmpp
zip -v -9 -r "$out/sleekxmpp-$(git name-rev --name-only HEAD)-$(git rev-parse --short HEAD).zip" sleekxmpp -x \*.py
popd

popd
