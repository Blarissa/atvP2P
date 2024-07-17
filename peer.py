from socket import *
import json, threading, os, random, string

SERVER_NAME = '10.13.78.132'
SERVER_PORT = 12000

PEER_PORT = 12001

DATA_DIR = './data'

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)                
    # Generate a random word
    random_word = ''.join(random.choices(string.ascii_lowercase, k=8))

    # Create the full file path with .txt extension
    file_path = os.path.join(DATA_DIR, f"{random_word}.txt")

    # Create the file with the random word and .txt extension
    with open(file_path, 'w') as file:
        file.write(f"This is a file named {random_word}.txt")

    print(f"\nArquivo {random_word}.txt criado.", flush=True)

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
    arquivos = []
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
            receive_file(leechSocket, DATA_DIR)
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
    peerSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    peerSocket.bind((get_ip(),PEER_PORT))
    while not stop_event.is_set():
        peerSocket.listen(5) # pode ter até 5 conexões pendentes
        peerConnectionSocket, addr = peerSocket.accept()
        nome_arquivo = peerConnectionSocket.recv(1024).decode()
        nome_arquivo = nome_arquivo.strip('"')
        print(f'peer {addr[0]} quer {nome_arquivo}\nenviando...')
        filepath = os.path.join(DATA_DIR, nome_arquivo)
        send_file(peerConnectionSocket,filepath)
        print(f'arquivo enviado.\n')

def send_file(sock, filename):
    file_size = os.path.getsize(filename)
    
    sock.sendall(f"{filename}|{file_size}".encode())

    with open(filename, "rb") as file:
        while chunk := file.read(1024):
            sock.sendall(chunk)

def receive_file(sock, save_directory):
    file_info = sock.recv(1024).decode()
    filename, file_size = file_info.split('|')
    print(f'salvando {filename} de tamanho {file_size}...')
    file_size = int(file_size)

    save_path = os.path.join(save_directory, os.path.basename(filename))

    with open(save_path, "wb") as file:
        received = 0
        while received < file_size:
            chunk = sock.recv(1024)
            if not chunk:
                break
            file.write(chunk)
            received += len(chunk)
    print(f'arquivo salvo.\n')


if __name__ == "__main__":
    thread = threading.Thread(target=peer_seeding, args=())
    thread.start()
    main()
    thread.join()
    
