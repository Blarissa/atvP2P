import socket
import json
import threading
from time import sleep

SERVER_NAME = '192.168.100.3'
SERVER_PORT = 12000

stop_event = threading.Event()

def create_and_connect(server_name, server_port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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

def test_thread():
    while not stop_event.is_set():
        pass

if __name__ == "__main__":
    thread = threading.Thread(target=test_thread, args=())
    thread.start()
    main()
    thread.join()
