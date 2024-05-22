from socket import *
serverName = '192.168.100.76'
serverPort = 12000

def createAndConnect(serverName,serverPort):
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName,serverPort))
    return clientSocket

menu = ('\nSelecione uma opção' +
        '\na - Registrar-se como peer' +
        '\nb - Registrar arquivo' +
        '\nc - Baixar arquivo' +
        '\nd - Sair\n')

while True:
    print(menu)
    opcode = input()
    clientSocket = createAndConnect(serverName,serverPort)
    clientSocket.send(opcode.encode())
    if (opcode == 'a'):
        myip = clientSocket.recv(1024)
        print('\nip: ', myip.decode())
        clientSocket.close()
    if (opcode == 'b'):
        nome_arquivo = input("Nome do Arquivo: ")
        clientSocket.send(nome_arquivo.encode())
        arquivo = clientSocket.recv(1024)
        print('\narquivo:', arquivo.decode())
        clientSocket.close()
    if(opcode == 'd'):
        break