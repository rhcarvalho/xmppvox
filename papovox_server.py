#!/usr/bin/env python
# -*- coding: utf8 -*-
'''
Essência do protocolo papovox:

   PORTA_PAPOVOX = 1963;
   PORTA_URGENTE = 1964;
   PORTA_NOMES   = 1956;

Papovox:

Todas as mensagens têm o mesmo formato:
    1 byte com o tipo de mensagem (valor binário)
    2 bytes com o tamanho da mensagem (binário little endian)
    n bytes com a mensagem
    (não há terminador nem checksum)

const
   DADOTECLADO       = 1;    texto da mensagem (sem tab, nem lf nem cr ao final)
   INICIOSOM         = 2;    sem parâmetros
   FIMSOM            = 3;    sem parâmetros
   DADOSOM           = 4;    enviados dados raw
   INICIOARQENVIA    = 5;    parâmetro: nome do arquivo
   FIMARQENVIA       = 6;    sem parâmetros
   DADOENVIA         = 7;    sem parâmetros
   CANCARQENVIA      = 8;    pode enviar uma frase junto
   PODEMANDAR        = 9;    sem parâmetros
   CANCELAMANDAR     = 10;   sem parâmetros

Mensagens urgentes:

   três linhas contendo ao final de cada uma um CR LF

       nomeUsuario   a repassar a mensagem
       enderUsuario   a repassar a mensagem
       msg

   Resposta:  +OK

Consulta ao servidor de nomes:  (pouco usado hoje em dia)

            HELP                   Fornece informações sobre os comandos"
            QUIT                   Encerra o serviço do servidor"
            NOOP                  Apenas responde +OK"
            NOW                   Mostra data/hora da máquina"
            IP <email>           Obtém o IP do usuário"
            GET <email>            Obtém IP e outras informações do usuário"
            REGISTER <email>       Registra informação do usuário"
            REMOVE <email>         Remove o registro de um usuário"
            LOGON <email>          Altera o IP de um usuário já cadastrado"
            LOGON <email> <informação sobre o logon>"
            LOGOFF <email>         Limpa informação do IP, mantendo as outras"
            FIND <nome_buscado>    Busca um nome e retorna seu
endereço eletrônico"
                           Para procurar só os ativos acrescentar + na
frente do e-mail"
            DATE <email> dd/mm/aaaa hh:mm  Muda data/hora de um nome
no registro"
            STOP                   Encerra o Findip"
               Para email com senha, acrescentar dois pontos e a senha
após o email."
               Exemplo:  eu@da.silva:minhasenha"
               Nota1: Não coloque espaços no e-mail e na senha.

   Respostas: +OK
                   -ERR
   Resposta com linhas múltiplas: terminar por uma linha contendo só
um ponto (.).
'''

PORTA_PAPOVOX = 1963
#PORTA_URGENTE = 1964
#PORTA_NOMES   = 1956

DADOTECLADO       = 1   # texto da mensagem (sem tab, nem lf nem cr ao final)
INICIOSOM         = 2   # sem parâmetros
FIMSOM            = 3   # sem parâmetros
INICIOARQENVIA    = 5   # parâmetro: nome do arquivo
FIMARQENVIA       = 6   # sem parâmetros
DADOSOM           = 4   # enviados dados raw
DADOENVIA         = 7   # sem parâmetros
CANCARQENVIA      = 8   # pode enviar uma frase junto
PODEMANDAR        = 9   # sem parâmetros
CANCELAMANDAR     = 10; # sem parâmetros

# -----------------------------------------------------------------------------

# Echo server program
import socket
import struct
import time

# Constants
SYSTEM_ENCODING = 'cp1252'

def sendmessage(msg, sock):
        print msg
        conn.sendall(struct.pack('<BH', DADOTECLADO, len(msg)) + msg.encode(SYSTEM_ENCODING))

if __name__ == "__main__":
    HOST = ''                 # Symbolic name meaning all available interfaces
    PORT = PORTA_PAPOVOX      # Arbitrary non-privileged port
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Reuse open port
    #s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(1)
    print "Serving on port %s" % PORT
    conn, addr = s.accept()
    print "Connected by %s" % (addr,)
    conn.sendall("+OK\n")
    print "OK sent"
    nickname = conn.recv(1024)
    print nickname
    conn.sendall("+OK\n")
    print "+OK sent"
    while True:
        time.sleep(5)
        sendmessage(u"Agora são %s" % time.ctime(), conn)
        #break
    print s.getpeername()
    print "Closing connection..."
    conn.close()
    print "Bye!"

