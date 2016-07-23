import os
import itertools
from PSE.Base import ListaPrioritaria
from PSE.SO import Mensagem

class Disco(object):
    def __init__(self, T_leitura, T_escrita, tamanho, arquivos_conf_dict):
        super(Disco, self).__init__()
        self.T_leitura = T_leitura
        self.T_escrita = T_escrita
        self.tamanho = tamanho
        self.espaco_ocupado = 0

        self.arquivos_conf_dict = arquivos_conf_dict

        self.particoes_cont = itertools.count()
        self.SFD = {} # Symbolic File Directory
        self.particoes = [] # formato da particao: (tamanho, arquivo)

        self.busy = False
        self.processo_atual = None
        self.fila = ListaPrioritaria()
        self.fila_dos_que_esperam_particao_livre = ListaPrioritaria()
        self.agora = 0

    def abrir(self, nome, job_requisitante):
        try:
            arquivo_dict = next(
                filter(
                    lambda d : d['nome'] == nome,
                    self.arquivos_conf_dict
                )
            )
        except Exception as e:
            raise Mensagem("arquivo nao especificado")

        # antes de qualquer coisa, verifica se o job requisitante tem direito de acesso ao arquivo
        if arquivo_dict['controle'] == 'publico' or arquivo_dict['proprietario'] == job_requisitante:
            # verifica se o arquivo já se encontra no sistema
            if nome in self.SFD:
                # obtem o arquivo
                particao = self.SFD[nome]
                arquivo = self.particoes[particao][1]

                # verifica se o arquivo nao se encontra aberto por outro job
                if not arquivo.aberto:
                    arquivo.abrir(job_requisitante)
                    raise Mensagem("arquivo aberto com sucesso", arquivo)
                # senao, coloca o job na fila de espera
                else:
                    arquivo.fila.insert(0, job_requisitante)
                    raise Mensagem('inserido na fila do arquivo')

            # tenta criar um novo arquivo
            else:
                tamanho = arquivo_dict['tamanho']
                proprietario = arquivo_dict['proprietario']
                controle = arquivo_dict['controle']
                # caso haja espaco livre, cria uma nova particao para o arquivo
                if tamanho <= self.espaco_disponivel():
                    arquivo = Arquivo(nome, tamanho, proprietario, controle)
                    pos = self.criarParticao(tamanho)
                    self.alocarParticao(pos, arquivo)
                    arquivo.abrir(job_requisitante)
                    raise Mensagem("arquivo aberto com sucesso", arquivo)
                else:
                    # busca uma particao livre
                    particao_boa = self.buscaParticaoBoa(tamanho)
                    if particao_boa is not None:
                        # libera a particao para que o novo arquivo possa ocupa-la
                        self.liberarParticao(particao_boa)
                        # cria o arquivo
                        arquivo = Arquivo(nome, tamanho, proprietario, controle)
                        # coloca-o na particao encontrada
                        self.alocarParticao(particao_boa, arquivo)
                        # e abre o arquivo, dando acesso a ele para o job requisitante
                        arquivo.abrir(job_requisitante)
                        raise Mensagem("arquivo aberto com sucesso", arquivo)
                    else:
                        self.fila_dos_que_esperam_particao_livre.push((job_requisitante, nome), 1, self.agora)
                        raise("inserido na fila dos que esperam particao livre")

        # manda mensagem de erro de falta de permissao
        else:
            raise Mensagem("acesso negado")

    def fechar(self, nome):
        if nome in self.SFD:
            part = self.SFD[nome]
            _, arquivo = self.particoes[part]
            arquivo.fechar()
            if not arquivo.fila:
                raise Mensagem("arquivo fechado com sucesso")
            else:
                raise Mensagem("job desempilhado", arquivo.fila.pop())
        else:
            raise Mensagem('arquivo nao esta aberto')

    def requisita(self, job_requisitante, nome_arquivo):
        # verifica se o job requisitante tem acesso ao arquivo
        particao_num = self.SFD[nome_arquivo]
        _, arquivo = self.particoes[particao_num]
        if arquivo._job_usufrutario == job_requisitante:
            # verifica se o disco em si nao esta ocupado
            if not self.busy:
                self.processo_atual = job_requisitante
                self.busy = True
                raise Mensagem('alocado com sucesso')
            else:
                self.fila.push((job_requisitante, nome_arquivo), 1, self.agora)
                raise Mensagem('disco ocupado')
        else:
            raise Mensagem('acesso negado')

    def libera(self):
        self.busy = False
        self.processo_atual = None
        if self.fila:
            raise Mensagem('job desempilhado', self.fila.pop())
        else:
            raise Mensagem('disco livre')

    def espaco_disponivel(self):
        return self.tamanho - self.espaco_ocupado

    def criarParticao(self, tamanho):
        # determina a posicao da nova particao no disco
        posicao_nova_particao = next(self.particoes_cont)
        # cria a nova particao de mesmo tamanho do arquivo
        nova_particao = [tamanho, None]
        self.particoes.append(nova_particao)
        self.espaco_ocupado += tamanho
        return posicao_nova_particao

    def alocarParticao(self, pos, arquivo):
        # coloca o arquivo na particao
        self.particoes[pos][1] = arquivo
        # cria uma nova entrada para o arquivo na tabela SFD
        self.SFD[arquivo.nome] = pos

    def liberarParticao(self, pos):
        _, arquivo = self.particoes[pos]
        del self.SFD[arquivo.nome]

    def buscaParticaoBoa(self, tamanho):
        i = 0
        # achou = False
        while i < len(self.particoes):# and not achou:
            tamanho_particao, arquivo = self.particoes[i]
            if not arquivo.aberto and \
                not arquivo.fila and \
                tamanho_particao >= tamanho:
                    return i
            i += 1

        return None

    def log_tabelaParticoes(self):
        print("\t---------------------------------------------------------------------------")
        print("\t| Particao |     Nome     | Proprietario | Aberto por | Tamanho | Acesso  |")
        print("\t|----------|--------------|--------------|------------|---------|---------|")
        i = 0
        while i < len(self.particoes):
            _, arquivo = self.particoes[i]
            nome = arquivo.nome
            tamanho = arquivo.tamanho
            proprietario = arquivo.proprietario
            controle = arquivo.controle
            usufrutario = arquivo._job_usufrutario.nome if arquivo._job_usufrutario is not None else '(fechado)'
            print("\t| {Particao:^8} | {Nome:12} | {Proprietario:12} | {Usufrutario:10} | {Tamanho:<7} | {Acesso:7} |".format(Particao=i, Nome=nome, Proprietario=proprietario, Usufrutario=usufrutario, Tamanho=tamanho, Acesso=controle))
            i += 1
        print("\t|-------------------------------------------------------------------------|")
        print("\t| Espaco ocupado: {:<55} |".format(self.espaco_ocupado))
        print("\t| Espaco desalocado: {:<52} |".format(self.espaco_disponivel()))
        print("\t---------------------------------------------------------------------------")

class Arquivo(object):
    def __init__(self, nome, tamanho, proprietario, controle):
        self.nome = nome
        self.tamanho = tamanho
        self.controle = controle
        self.proprietario = proprietario
        self.conteudo = ''
        self.aberto = False
        self.fila = []
        self._job_usufrutario = None

    def abrir(self, job):
        self.aberto = True
        self._job_usufrutario = job

    def fechar(self):
        self.aberto = False
        self._job_usufrutario = None

    def ler(self):
        return self.conteudo

    def escrever(self, novo_conteudo):
        self.conteudo = novo_conteudo

    def __del__(self):
        self.aberto = False
