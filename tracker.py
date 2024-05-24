from socket import *
import json 

tracking = {} # dicionário de peers(keys) e seus arquivos(values)

serverPort = 12000
serverSocket = socket(AF_INET,SOCK_STREAM) # welcoming socket
serverSocket.bind(('192.168.100.76',serverPort))
print('The server is ready to receive')

while True:
    serverSocket.listen(5) # pode ter até 5 conexões pendentes
    connectionSocket, addr = serverSocket.accept()
    opcode = connectionSocket.recv(1024).decode()

    ip_address = addr[0] #endereço ip da nova conexão
    if(opcode == 'a'): #entrar na rede
        connectionSocket.send(ip_address.encode())
        if ip_address not in tracking:
            tracking.update({ip_address: []})  
        connectionSocket.close()
    if(opcode == 'b'): #registrar arquivo
        if ip_address in tracking.keys():
            nome_arquivo = json.loads(connectionSocket.recv(1024).decode())
            tracking.setdefault(ip_address, []).append(nome_arquivo)
            connectionSocket.send(json.dumps(nome_arquivo).encode())
            connectionSocket.close()
        else:
            connectionSocket.send((json.dumps("403")).encode())
            connectionSocket.close()
    if(opcode == 'c'): #listar arquivos
        connectionSocket.send((json.dumps(tracking)).encode())
        connectionSocket.close()
    if(opcode == 'd'): #baixar arquivo
        notfound = True;
        nome_arquivo = json.loads(connectionSocket.recv(1024).decode())
        if(tracking): # if tracking is not empty
            for ip in tracking.keys():
                for arquivos in tracking.get(ip):
                    if nome_arquivo in arquivos:
                        connectionSocket.send(json.dumps(ip).encode())
                        notfound = False;
        if (notfound):
            connectionSocket.send(json.dumps("404").encode())
        connectionSocket.close()
    if(opcode == 'e'): #sair da rede
        if(tracking):
            tracking.pop(addr[0])
        connectionSocket.close()


            

