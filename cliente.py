import socket, sys, select, os, time

class cliente:
    def __init__(self, ip, porta):
        self.addr = (ip, porta)
        self.conexao = socket.socket()
        self.arquivos = []
        self.diretorio = './data'

        if not os.path.exists(self.diretorio):
            os.makedirs(self.diretorio)                

        self.conectar()
        self.run()   
        
    def conectar(self):
        self.conexao.connect(self.addr)
        print('Conectado ao servidor {} na porta {}'.format(self.addr[0], self.addr[1]))
        
    def enviarMensagem(self, mensagem):
        self.conexao.send(mensagem.encode())
        
    def receberMensagem(self):
        return self.conexao.recv(1024)
    
    def enviarArquivo(self, arquivo):
        self.conexao.send(arquivo.encode())
        return self.receberMensagem()
    
    def receberArquivo(self, arquivo):
        # recebendo o tamanho do arquivo
        tam = int(self.receberMensagem().decode())

        # recebendo dados do arquivo
        dados = self.receberMensagem().decode()

        # salvando arquivo
        url = '{}/{}'.format(self.diretorio, arquivo)
        try:
            with open(url, 'wb') as f:
                f.write(dados)
                print('Arquivo {} baixado com sucesso'.format(arquivo))
                return 'OK'
        except:
            print('Erro ao baixar arquivo')
            return 'ERRO'        
    
    def listarArquivos(self):
        self.enviarMensagem('LISTAR')
        arquivos = self.receberMensagem()
        self.arquivos = arquivos.split(',')
        return self.arquivos
    
    def fechar(self):
        self.conexao.close()
        
    def run(self):
        while True:
            io_list = [sys.stdin, self.conexao]
            ready_to_read, ready_to_write, in_error = select.select(io_list , [], [])
            
            for io in ready_to_read:
                # se tivermos recebido uma mensagem
                if io is self.conexao:   

                    msg = self.receberMensagem()

                    if not msg:
                        print('Desconectado do servidor')
                        sys.exit()

                    elif msg.decode() in ['MENU', 'LISTAR', 'PEERS']:
                        exibir = self.receberMensagem().decode()
                        print('{}'.format(exibir))                        

                    elif msg.decode() == 'BAIXAR':
                        exibir = self.receberMensagem().decode()
                        print('{}'.format(exibir))
                        
                        arquivo = input()
                        self.enviarMensagem(arquivo)                                            

                        status = self.receberArquivo(arquivo)
                        self.enviarMensagem(status) 
                        
                    elif msg.decode() == 'DESCONECTAR':
                        print('Desconectando do servidor ...')
                        self.enviarMensagem('OK')
                        self.fechar()
                        sys.exit()

                else:
                    # enviar informacao
                    resp = input()
                    self.enviarMensagem(resp)  
                    sys.stdout.flush()

cliente('192.168.0.5', 1234)