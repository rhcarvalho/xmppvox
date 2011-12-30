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
#------------------------------------------------------------------------------#

import socket
import struct
import time
from functools import partial
from itertools import count
from cStringIO import StringIO

import getpass
import logging
from echo_client import EchoBot

#---------------- Constantes --------------------------------------------------#

# Todas as strings passadas para o Papovox devem ser codificadas usando a
# codificação padrão do Windows.
SYSTEM_ENCODING = 'cp1252'

PORTA_PAPOVOX = 1963
#PORTA_URGENTE = 1964
#PORTA_NOMES   = 1956

DADOTECLADO       = 1   # texto da mensagem (sem tab, nem lf nem cr ao final)
#INICIOSOM         = 2   # sem parâmetros
#FIMSOM            = 3   # sem parâmetros
#INICIOARQENVIA    = 5   # parâmetro: nome do arquivo
#FIMARQENVIA       = 6   # sem parâmetros
#DADOSOM           = 4   # enviados dados raw
#DADOENVIA         = 7   # sem parâmetros
#CANCARQENVIA      = 8   # pode enviar uma frase junto
#PODEMANDAR        = 9   # sem parâmetros
#CANCELAMANDAR     = 10  # sem parâmetros

#------------------------------------------------------------------------------#

def sendmessage(sock, msg):
    print "[[[[ %s ]]]]" % (msg,)
    msg = msg.encode(SYSTEM_ENCODING)
    sock.sendall("%s%s" % (struct.pack('<BH', DADOTECLADO, len(msg)),
                           msg))

def sendline(sock, line):
    print "==>> %s ==>>" % (line,)
    line = line.encode(SYSTEM_ENCODING)
    sock.sendall("%s\r\n" % (line,))

def recv(sock, size):
    data = sock.recv(size)
    if not data and size:
        raise socket.error(u"Nenhum dado recebido do socket, conexão perdida.")
    return data

def recvall(sock, size):
    data = StringIO()
    while data.tell() < size:
        data.write(recv(sock, size - data.tell()))
    data_str = data.getvalue()
    data.close()
    return data_str

#------------------------------------------------------------------------------#

def main():
    # Setup logging.
    logging.basicConfig(level=logging.INFO,
                        format='%(levelname)-8s %(message)s')

    jid = raw_input("Conta (ex.: fulano@gmail.com): ")
    password = getpass.getpass("Senha para %r: " % jid)
    xmpp = EchoBot(jid, password)
    xmpp.register_plugin('xep_0030') # Service Discovery
    xmpp.register_plugin('xep_0004') # Data Forms
    xmpp.register_plugin('xep_0060') # PubSub
    xmpp.register_plugin('xep_0199') # XMPP Ping
    
    if xmpp.connect():
        print "<<XMPP conectado>>"
        xmpp.process(threaded=True)

    HOST = ''                 # Symbolic name meaning all available interfaces
    PORT = PORTA_PAPOVOX      # Arbitrary non-privileged port
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Reuse open port
    #s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(1)
    while True:
        try:
            print u"XMPPVOX servindo na porta %s" % PORT
            
            # Aceita conexão do Papovox
            conn, addr = s.accept()
            print u"Aceitei conexão de %s:%s" % addr
            
            # Funções úteis usando a conexão atual
            _sendline, _sendmessage, _recvall = map(partial,
                                                    (sendline, sendmessage, recvall),
                                                    (conn, conn, conn))
            xmpp.func_receive_msg = _sendmessage
            
            #------------------ Handshake inicial -----------------------------#
            _sendline(u"+OK - %s:%s conectado" % addr)
            nickname = conn.recv(1024)
            print u"Apelido: %s" % (nickname,)
            _sendline(u"+OK")
            #------------------------------------------------------------------#
            
            # Se enviar mensagens logo em seguida, o Papovox não recebe
            # corretamente. O SítioVox aguarda 100ms (arquivo SVPROC.PAS).
            # Provavelmente está relacionado a alguma temporização / espera
            # na leitura de algum buffer.
            time.sleep(0.1)
            _sendmessage(u"Olá companheiro, bem-vindo ao Gugou Tolk Vox!")
            for i in count(1):
                datatype, datalen = struct.unpack('<BH', _recvall(3))
                
                # Recusa dados do Papovox que não sejam do tipo DADOTECLADO
                if datatype != DADOTECLADO:
                    print u"<<== Recebi tipo de dados desconhecido: (%d) <<==" % datatype
                    continue
                
                # Recebe dados/mensagem do Papovox
                data = _recvall(datalen)
                
                # Envia mensagem XMPP para o último remetente
                if xmpp.last_sender is not None:
                    xmpp.send_message(mto=xmpp.last_sender,
                                      mbody=data,
                                      mtype='chat')
                print u"#%03d. %s ** para %s" % (i, repr(data),
                                                 xmpp.last_sender or u"ninguém")
        except socket.error, e:
            print u"Erro: %s" % (e,)
        finally:
            conn.close()
            print u"Conexão encerrada."


if __name__ == '__main__':
    main()