#!/bin/bash
if  [[ `uname` == MINGW* ]] ;
then
    cmd.exe //c build.bat
else
    echo "Este script deve ser executado usando o MSYS (sh no Windows)"
fi
