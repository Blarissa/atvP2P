import socket, threading, pickle, struct, time, os

class servidor:
    def __init__(self, ip, porta):        
        self.addr = (ip, porta)
        self.socket = socket.socket()
        self.peers = []
        self.diretorio = 'data'        
        self.arquivos = self.retornaArquivos() 
        self.conectar()               
        
    def conectar(self):        
        # reutilizar endereco logo a seguir a fechar o servidor
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
        
        # vincula o socket a um endereco e porta
        self.socket.bind(self.addr)
        
        # coloca o socket em modo de espera
        self.socket.listen(5)                                      
        print('Aguardando conexões...')

        while True:
            # aceita uma nova conexao e retorna um novo socket e o endereco do cliente            
            conn, addr = self.aceitarConexao()
            
            print('Conectado com {}'.format(addr))            
            #self.enviarMensagem('Bem vindo {}'.format(addr), conn)
            
            # adiciona o novo socket a lista de conexoes
            self.adicionarPeer(addr)
            
            # cria uma thread para lidar com a nova conexão
            threading.Thread(target=self.run, args=(conn, addr)).start()
        
    def aceitarConexao(self):        
        return self.socket.accept()
    
    def retornaArquivos(self):   
        self.arquivos = set()          
        for arquivo in os.listdir(self.diretorio):
            self.arquivos.add((arquivo, self.addr))     
            
        return self.arquivos               
    
    def adicionarPeer(self, addr):
        self.peers.append(addr)
    
    def enviarMensagem(self, mensagem, conn):
        conn.send(mensagem.encode())
    
    def esperaMensagem(self, conn, addr):
        # aguarda a chegada de dados
        while True:
            data = conn.recv(1024)
            
            # se o cliente tiver desligado
            if not data:
                print('Desconectado de {}'.format(addr))
                self.peers.remove(addr)
                break
            
            return data
    
    def enviarArquivo(self, arquivo, conn):   
        try:     
            with open(arquivo.decode(), 'rb') as arq:
                texto = arq.read()      

                # envia o tamanho do arquivo      
                self.enviarMensagem(len(texto), conn) 
                # envia conteudo do arquivo    
                self.enviarMensagem(texto, conn)   
                print('Arquivo {} enviado com sucesso'.format(arquivo.decode()))
        except:
            print('Erro ao enviar arquivo')
    
    def listarArquivos(self, conn):       
        arquivos = ', '.join([arquivo[0] for arquivo in self.arquivos])
        self.enviarMensagem(arquivos, conn)      
    
    def fechar(self):
        self.conexao.close()
        
    def run(self, conn, addr): 
        while True:                 
            # exibe o menu
            self.enviarMensagem('MENU', conn)
            time.sleep(1)
            self.exibeMenu(conn)    
                        
            while True:
                opt = conn.recv(1024)

                # se a opcao for 1, listar arquivos
                if opt.decode() == '1':
                    self.enviarMensagem('LISTAR', conn)
                    time.sleep(1)
                    self.listarArquivos(conn)                
                
                # se a opcao for 2, enviar arquivo
                elif opt.decode() == '2':
                    self.enviarMensagem('BAIXAR', conn)
                    time.sleep(1)
                    self.enviarMensagem('Digite o nome do arquivo: ', conn)                
                    arquivo = self.esperaMensagem(conn, addr)                
                    
                    self.enviarArquivo(arquivo, conn)
                    status = self.esperaMensagem(conn, addr).decode()
                    
                    if status == 'OK':
                        # altera o endereco do arquivo para o endereco do cliente
                        self.arquivos[arquivo.decode()] = addr                    
                        print('Arquivo {} baixado por {} com sucesso'.format(arquivo.decode(), addr))                   
                    else:
                        print('Peer {} não conseguir baixar o arquivo {}'.format(addr, arquivo.decode()))                                                                      
                
                # se a opcao for 3, sair   
                elif opt.decode() == '3':
                    self.enviarMensagem('DESCONECTAR', conn)
                    status = self.esperaMensagem(conn, addr).decode()
                    
                    if status == 'OK':
                        print('Desconectando do peer {}'.format(addr))
                        self.peers.remove(conn)                                    
                    
                elif opt.decode() == '4':
                    self.enviarMensagem('PEERS', conn)
                    time.sleep(1)
                    
                    peers = ', '.join([str(peer) for peer in self.peers])
                    self.enviarMensagem(peers, conn)
                    
                elif opt.decode() == '5':
                    self.enviarMensagem('DESCONECTAR', conn)   

                else:
                    self.enviarMensagem('Opção inválida', conn)
            # aguarda a opcao do cliente    
            #opt = self.esperaMensagem(conn, addr)        
            
                
    def exibeMenu(self, conn):
        msg = ('\nSelecione uma opção' +
               '\n1 - Listar arquivos' +
               '\n2 - Baixar arquivo' +
               '\n3 - Enviar arquivo' +               
               '\n4 - Mostrar Peers' +
               '\n5 - Sair\n')               
        
        self.enviarMensagem(msg, conn)
                
    def lerArquivo(self, arquivo):
        try:
            with open(os.path.join(arquivo), 'r+') as file:
                text_lines = file.readlines()
        except:
            print('File not found')
            return False

        return text_lines
        
servidor('192.168.0.5', 1234)    