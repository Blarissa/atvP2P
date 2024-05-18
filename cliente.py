import socket, sys, select

class cliente:
    def __init__(self, ip, porta):
        self.ip = ip
        self.porta = porta
        self.conexao = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.arquivos = []
        self.conectar()
        self.run()
        
        
    def conectar(self):
        self.conexao.connect((self.ip, self.porta))
        
    def enviarMensagem(self, mensagem):
        self.conexao.send(mensagem.encode())
        
    def receberMensagem(self):
        return self.conexao.recv(1024)
    
    def enviarArquivo(self, arquivo):
        self.conexao.send(arquivo.encode())
        return self.receberMensagem()
    
    def receberArquivo(self, arquivo):
        with open(arquivo, 'wb') as f:
            while True:
                data = self.conexao.recv(1024)
                if not data:
                    break
                f.write(data)
                
        print('Arquivo recebido com sucesso')
        self.enviarMensagem('Arquivo enviado com sucesso')
    
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
                    data = self.receberMensagem()
                    print('{}'.format(data.decode()))
                
                else:
                    # enviar informacao
                    arquivo = input()
                    self.enviarMensagem(arquivo)
                    
                    # receber informacao
                    data = self.receberMensagem()
                    
                    # se o arquivo nao for encontrado
                    if data == 'Arquivo não encontrado':
                        print('Arquivo não encontrado')
                        continue
                    else:
                        print('Arquivo encontrado')
                        self.receberArquivo(arquivo)
                        continue
                            
                    
                    
            
            
            
            

cliente = cliente('192.168.0.5', 1234)
cliente.run()