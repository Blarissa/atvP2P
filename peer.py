from socket import *
import json
serverName = '192.168.100.76'
serverPort = 12000

def createAndConnect(serverName,serverPort):
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName,serverPort))
    return clientSocket

menu = ('\na - Registrar-se como peer' +
        '\nb - Registrar arquivo' +
        '\nc - Listar arquivos' +
        '\nd - Baixar arquivo' +
        '\ne - Sair da rede'
        '\nf - Sair\n')

while True:
    print(menu)
    opcode = input()
    clientSocket = createAndConnect(serverName,serverPort)
    clientSocket.send(opcode.encode())
    if (opcode == 'a'):
        myip = clientSocket.recv(1024)
        print(f'\nip: {myip.decode()} registrado.')
        clientSocket.close()
    if (opcode == 'b'):
        nome_arquivo = input("Nome do Arquivo: ")
        clientSocket.send(json.dumps(nome_arquivo).encode())
        arquivo = json.loads(clientSocket.recv(1024))
        if (arquivo == "403"):
            print(f'\npeer não registrado na rede')
            clientSocket.close()
        else:
            print(f'\narquivo {arquivo} registrado.')
            clientSocket.close()
    if (opcode == 'c'):
        arquivos = json.loads(clientSocket.recv(1024))
        print(f'\narquivos: {arquivos}')
    if(opcode == 'd'):
        nome_arquivo = input("Nome do Arquivo: ")
        clientSocket.send(json.dumps(nome_arquivo).encode())
        answer = json.loads(clientSocket.recv(1024).decode())
        if (answer == "404"):
            print(f'\narquivo não encontrado.')
        else:
            print(f'\narquivo encontrado no ip {answer}')
        clientSocket.close()
    if(opcode == 'e'):
        print(f'\nsaiu da rede.')
        clientSocket.close()
    if(opcode == 'f'):
        break