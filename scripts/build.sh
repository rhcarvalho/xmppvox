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

if  [[ `uname` == MINGW* ]] ;
then

    SCRIPTS_DIR="$(cd "$(dirname "$0")" && pwd)"
    PROJECT_HOME_DIR=SCRIPTS_DIR/..

    pushd $PROJECT_HOME_DIR > /dev/null
    cmd.exe //c "$SCRIPTS_DIR\\build.bat"
    popd > /dev/null
else
    echo "Este script deve ser executado usando o MSYS (sh no Windows)"
fi
