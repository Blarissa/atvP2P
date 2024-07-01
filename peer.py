#import socket
from socket import *
import json
import threading
import os

SERVER_NAME = '192.168.100.3'
SERVER_PORT = 12000

PEER_PORT = 12001

arquivos = []
diretorio = './data'

if not os.path.exists(diretorio):
    os.makedirs(diretorio)                

stop_event = threading.Event()

def create_and_connect(server_name, server_port):
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect((server_name, server_port))
    return client_socket

def register_peer(client_socket):
    myip = client_socket.recv(1024)
    print(f'\nIP: {myip.decode()} registrado.')

def register_file(client_socket):
    nome_arquivo = input("Nome do Arquivo: ")
    client_socket.send(json.dumps(nome_arquivo).encode())
    arquivo = json.loads(client_socket.recv(1024).decode())
    if arquivo == "403":
        print('\nPeer não registrado na rede')
    else:
        print(f'\nArquivo {arquivo} registrado.')

def list_files(client_socket):
    arquivos = json.loads(client_socket.recv(1024).decode())
    print(f'\nArquivos: {arquivos}')

def download_file(client_socket):
    nome_arquivo = input("Nome do Arquivo: ")
    client_socket.send(json.dumps(nome_arquivo).encode())
    answer = json.loads(client_socket.recv(1024).decode())
    if answer == "404":
        print('\nArquivo não encontrado.')
    else:
        print(f'\nArquivo encontrado no IP {answer}')
        leechSocket = create_and_connect(answer,PEER_PORT) # establish TCP connection with peer
        try:
            leechSocket.send(json.dumps(nome_arquivo).encode())
            save_directory = 'data/'  # Directory to save the received file
            receive_file(leechSocket, save_directory)
        except Exception as e:
            print(f'Error: {e}')
        finally:
            leechSocket.close()

def leave_network():
    print('\nSaiu da rede.')

def main():
    menu = (
        '\na - Registrar-se como peer'
        '\nb - Registrar arquivo'
        '\nc - Listar arquivos'
        '\nd - Baixar arquivo'
        '\ne - Sair da rede'
        '\nf - Sair\n'
    )

    while True:
        print(menu)
        opcode = input()
        client_socket = create_and_connect(SERVER_NAME, SERVER_PORT)

        try:
            client_socket.send(opcode.encode())

            if opcode == 'a':
                register_peer(client_socket)
            elif opcode == 'b':
                register_file(client_socket)
            elif opcode == 'c':
                list_files(client_socket)
            elif opcode == 'd':
                download_file(client_socket)
            elif opcode == 'e':
                leave_network()
            elif opcode == 'f':
                stop_event.set()
                break
            else:
                print('\nOpção inválida.')
        except Exception as e:
            print(f'Error: {e}')
        finally:
            client_socket.close()

def get_ip():
    machine_name = gethostname()
    machine_address = gethostbyname(machine_name)
    return machine_address

def peer_seeding():
    peerSocket = socket(AF_INET,SOCK_STREAM) # welcoming socket
    peerPort = 12001
    peerSocket.bind((get_ip(),peerPort))
    print(f'{get_ip()} is ready to receive')
    while not stop_event.is_set():
        peerSocket.listen(5) # pode ter até 5 conexões pendentes
        peerConnectionSocket, addr = peerSocket.accept()
        nome_arquivo = peerConnectionSocket.recv(1024).decode()
        nome_arquivo = nome_arquivo.strip('"')
        print(f'peer {addr} quer {nome_arquivo}')
        filepath = os.path.join('data', nome_arquivo)
        send_file(peerConnectionSocket,filepath)

def send_file(sock, filename):
    # Get the size of the file
    file_size = os.path.getsize(filename)
    
    # Send the file name and size
    sock.sendall(f"{filename}|{file_size}".encode())

    # Open the file in binary mode and send it in chunks
    with open(filename, "rb") as file:
        while chunk := file.read(1024):
            sock.sendall(chunk)

def receive_file(sock, save_directory):
    # Receive the file name and size
    file_info = sock.recv(1024).decode()
    print(file_info)
    filename, file_size = file_info.split('|')
    file_size = int(file_size)

    # Save the file in the specified directory
    save_path = os.path.join(save_directory, os.path.basename(filename))

    # Receive the file in chunks
    with open(save_path, "wb") as file:
        received = 0
        while received < file_size:
            chunk = sock.recv(1024)
            if not chunk:
                break
            file.write(chunk)
            received += len(chunk)


if __name__ == "__main__":
    thread = threading.Thread(target=peer_seeding, args=())
    thread.start()
    main()
    thread.join()
    
