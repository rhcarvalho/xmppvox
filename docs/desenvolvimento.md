Dependências
------------

*Atenção: Esta seção é destinada a usuários avançados do XMPPVOX
que desejam alterar seu código-fonte. Se você não sabe o que isto
significa, ignore esta seção.*

Para utilizar o XMPPVOX é preciso que estejam instalados os seguintes
programas e bibliotecas:

- DOSVOX / Papovox (testado com DOSVOX 4.2alfa, Papovox 3.3B)
- Python 2.7 (testado com 2.7.5)
- Bibliotecas descritas no arquivo "requirements.txt"

Para instalar as dependências:

    pip install -r requirements.txt

Dependências para gerar executável:

- pywin32 (testado com Build 218)
- PyInstaller (testado com versão 2.1)
- UPX (testado com versão 3.91)

Opcionais:

- MinGW (para usar scripts ".sh")
- snakefood (para gerar grafo de dependências do projeto)
