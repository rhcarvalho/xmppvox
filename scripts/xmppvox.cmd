*XMPPVox
*Autor: Neno Henrique Albernaz
*Em 16/02/2012
*Modificado por: Rodolfo Henrique Carvalho
*Em 26/02/2012

escreve "Iniciando o XMPPVOX"

cor 15
fundo 0
tela limpa
escreve "Digite o JID"
cor 14
le c
cor 15
se c=""
    escreve "Desistiu"
    desvia @fim
fim se

escreve "Digite a senha"
Lê Senha s
se s=""
    escreve "Desistiu"
    desvia @fim
fim se
tela limpa

seja x "c:\winvox\xmppvox.exe -j "
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
    se i <=5  desvia @loopBipa
*escreve "Ok"
executa "c:\winvox\papovox.exe"&
@fim
termina mudo
