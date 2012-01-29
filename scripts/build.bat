@ECHO OFF

REM    XMPPVOX: XMPP client for DOSVOX.
REM    Copyright (C) 2012  Rodolfo Henrique Carvalho
REM
REM    This file is part of XMPPVOX.
REM
REM    XMPPVOX is free software: you can redistribute it and/or modify
REM    it under the terms of the GNU General Public License as published by
REM    the Free Software Foundation, either version 3 of the License, or
REM    (at your option) any later version.
REM
REM    This program is distributed in the hope that it will be useful,
REM    but WITHOUT ANY WARRANTY; without even the implied warranty of
REM    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
REM    GNU General Public License for more details.
REM
REM    You should have received a copy of the GNU General Public License
REM    along with this program.  If not, see <http://www.gnu.org/licenses/>.

REM ----------------------------------------------------------------------------
REM  Este script Ç parte do XMPPVOX.
REM  Escrito por Rodolfo Carvalho em 08/01/2012
REM
REM
REM  Para distribuir o projeto usando o PyInstaller:
REM
REM  0. Instalar pywin32
REM     http://sourceforge.net/projects/pywin32/files/pywin32/Build216/
REM  1. Baixar o PyInstaller:
REM     http://www.pyinstaller.org/changeset/latest/trunk?old_path=%2F&format=zip
REM     (testado com pyinstalller-trunk-1899.zip)
REM  2. Descompactar em C:\pyinstaller
REM  3. Baixar o UPX:
REM     http://upx.sourceforge.net/download/upx308w.zip
REM  4. Extrair o execut†vel upx.exe em C:\Python27 (ou outro lugar no PATH)
REM
REM
REM  OBS: O PyInstaller n∆o funciona bem com eggs descompactados (diret¢rios),
REM       mas funciona bem com eggs compactados (zip).
REM       Antes de executar este script, certifique-se que os eggs est∆o
REM       compactados:
REM          pip zip dns
REM          pip zip sleekxmpp
REM
REM Execute este script a partir do diret¢rio principal do projeto:
REM     scripts\build.bat
REM Ou use o bash script (com MINGW)

REM Remove arquivos antigos se existirem
IF EXIST dist (
    RMDIR /Q /S dist
)

SETLOCAL
SET DNSPYTHON_ZIP=%CD%\thirdparty\dnspython-master-d5dc023.zip
SET SLEEKXMPP_ZIP=%CD%\thirdparty\sleekxmpp-develop-3ab7c8b.zip

IF NOT EXIST "%DNSPYTHON_ZIP%" (
    ECHO Atená∆o: falta dependància -- dnspython
    EXIT 2
)
IF NOT EXIST "%SLEEKXMPP_ZIP%" (
    ECHO Atená∆o: falta dependància -- sleekxmpp
    EXIT 3
)

REM Executa o pyinstaller.py se existir ou exibe mensagem e termina.
IF EXIST c:\pyinstaller\pyinstaller.py (
    c:\pyinstaller\pyinstaller.py --onefile --version-file=version ^
        --paths="%DNSPYTHON_ZIP%;%SLEEKXMPP_ZIP%" src/xmppvox.py
) ELSE (
    ECHO Atená∆o: PyInstaller n∆o encontrado!
    EXIT 1
)
ENDLOCAL

IF NOT EXIST dist (
    ECHO Atená∆o: PyInstaller falhou!
    GOTO:EOF
)

REM Copia c¢digo-fonte para ser distribu°do:
bzr export dist\xmppvox-src

REM ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
REM Abaixo seguem dois mÇtodos diferentes para descobrir se um execut†vel
REM est† no PATH. A princ°pio um Ç t∆o bom quanto o outro, e os dois s∆o
REM usados s¢ para demonstrar as duas possibilidades.
REM Se um for definitivamente melhor que o outro, podemos passar a us†-lo
REM sempre que necess†rio.
REM ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

for %%G in (zip.exe) do (set FOUND=%%~$PATH:G)
IF DEFINED FOUND (
    REM Compacta todos os arquivos em um zip.
    PUSHD dist
    zip -v -9 -r xmppvox-1.0.zip *
    POPD
) ELSE (
    ECHO.
    ECHO.
    ECHO Atená∆o: zip n∆o encontrado!
)

REM Verifica se o upx.exe est† no PATH e avisa caso contr†rio.
FOR %%G IN ("%path:;=" "%") DO IF EXIST %%G\upx.exe GOTO:EOF
ECHO.
ECHO.
ECHO Atená∆o: UPX n∆o encontrado! Verifique se foi instalado corretamente.
