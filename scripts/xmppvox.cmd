* XMPPVOX: XMPP client for DOSVOX.
* Copyright (C) 2012  Rodolfo Henrique Carvalho
*
* This file is part of XMPPVOX.
*
* XMPPVOX is free software: you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation, either version 3 of the License, or
* (at your option) any later version.
*
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
* GNU General Public License for more details.
*
* You should have received a copy of the GNU General Public License
* along with this program.  If not, see <http://www.gnu.org/licenses/>.
*
* ----------------------------------------------------------------------------
* Este script é parte do XMPPVOX.

* Autores:
*   Neno Henrique Albernaz
*   Rodolfo Henrique Carvalho

escreve "Iniciando o XMPPVOX"

cor 15
fundo 0
tela limpa
escreve "Digite sua conta"
cor 14
le c
cor 15
se c = ""
    escreve "Desistiu"
    desvia @fim
fim se

escreve "Digite sua senha"
Lê Senha s
se s = ""
    escreve "Desistiu"
    desvia @fim
fim se
tela limpa

seja x "xmppvox.exe -j "
concatena x c
concatena x " -s "
concatena x s

cor 4
escreve "Aguarde"
executa x&
@loopBipa
    bipa
    espera 1
    soma i 1
    se i < 3 desvia @loopBipa
*escreve "Ok"
executa "papovox.exe"&
@fim
termina mudo
