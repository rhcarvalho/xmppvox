@ECHO OFF
REM Este script Ç parte do XMPPVOX.
REM Escrito por Rodolfo Carvalho em 08/01/2012
REM
REM
REM Para distribuir o projeto usando o PyInstaller:
REM
REM 1. Baixar o PyInstaller:
REM    http://www.pyinstaller.org/changeset/latest/trunk?old_path=%2F&format=zip
REM 2. Descompactar em C:\pyinstaller
REM 3. Baixar o UPX:
REM    http://upx.sourceforge.net/download/upx308w.zip
REM 4. Extrair o execut†vel upx.exe em C:\Python27 (ou outro lugar no PATH)
REM
REM
REM OBS: O PyInstaller n∆o funciona bem com eggs descompactados (diret¢rios),
REM      mas funciona bem com eggs compactados (zip).
REM      Antes de executar este script, certifique-se que os eggs est∆o
REM      compactados:
REM         pip zip dns
REM         pip zip sleekxmpp
REM

REM Executa o pyinstaller.py se existir ou exibe mensagem e termina.
IF EXIST c:\pyinstaller\pyinstaller.py (
    c:\pyinstaller\pyinstaller.py --onefile xmppvox.py
) ELSE (
    ECHO Atená∆o: PyInstaller n∆o encontrado!
    GOTO END
)

REM Verifica se o upx.exe est† no PATH e avisa caso contr†rio.
FOR %%G IN ("%path:;=" "%") DO IF EXIST %%G\upx.exe GOTO END
ECHO.
ECHO.
ECHO Atená∆o: UPX n∆o encontrado! Verifique se foi instalado corretamente.
:END

REM TODO: 
REM   * Remover m¢dulos n∆o usados, gerar .exe menor que 5.85 MB
REM   * Manter apenas *.pyc dentro dos eggs
