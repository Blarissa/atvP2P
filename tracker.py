from socket import *
import json 

tracking = {}

serverPort = 12000
serverSocket = socket(AF_INET,SOCK_STREAM) #welcoming socket
serverSocket.bind(('192.168.100.76',serverPort))
print('The server is ready to receive')

while True:
    serverSocket.listen(5)
    connectionSocket, addr = serverSocket.accept()
    opcode = connectionSocket.recv(1024).decode()

    address = addr[0]
    if(opcode == 'a'):
        connectionSocket.send(address.encode())
        if address not in tracking:
            tracking.update({address: []})  
        connectionSocket.close()
    if(opcode == 'b'):
        nome_arquivo = connectionSocket.recv(1024).decode()
        tracking.setdefault(address, []).append(nome_arquivo)
        connectionSocket.send(nome_arquivo.encode())
        connectionSocket.close()
    if(opcode == 'c'):
        connectionSocket.send((json.dumps(tracking)).encode())
        connectionSocket.close()
    if(opcode == 'd'):
        nome_arquivo = connectionSocket.recv(1024).decode()
        for ip in tracking.keys():
            for arquivos in tracking.get(ip):
                if nome_arquivo in arquivos:
                    connectionSocket.send(json.dumps(ip).encode())
                else: 
                    connectionSocket.send(json.dumps("404").encode())

            

