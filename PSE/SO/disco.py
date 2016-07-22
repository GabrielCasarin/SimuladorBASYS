import os
import itertools
from PSE.SO import Mensagem

class Disco(object):
    def __init__(self, T_leitura, T_escrita, tamanho, dict_arquivos_conf):
        super(Disco, self).__init__()
        self.T_leitura = T_leitura
        self.T_escrita = T_escrita
        self.tamanho = tamanho
        self.espaco_ocupado = 0

        self.dict_arquivos_conf = dict_arquivos_conf

        self.particoes_cont = itertools.count()
        self.SFD = {} # Symbolic File Directory
        self.particoes = [] # formato da particao: (tamanho, arquivo)

        self.fila = []
        self.fila_dos_que_esperam_particao_livre = []

    def abrir(self, nome, job_requisitante):
        try:
            arquivo_dict = next(
                filter(
                    lambda d : d['nome'] == nome,
                    self.dict_arquivos_conf
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
                    arquivo.aberto = True
                    return arquivo
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
                    arquivo.aberto = True
                    raise Mensagem("arquivo aberto com sucesso", arquivo)
                else:
                    # busca uma particao livre
                    particao_boa = self.buscaParticaoBoa(tamanho)
                    if particao_boa is not None:
                        self.liberarParticao(particao_boa)
                        arquivo = Arquivo(nome, tamanho, proprietario, controle)
                        self.alocarParticao(particao_boa, arquivo)
                        raise Mensagem("arquivo aberto com sucesso", arquivo)
                    else:
                        self.fila_dos_que_esperam_particao_livre.insert(0, job_requisitante)
                        raise("inserido na fila dos que esperam particao livre")

        # manda mensagem de erro de falta de permissao
        else:
            raise Mensagem("o job '{}' nao tem direito de acesso ao arquivo '{}'".format(job_requisitante, nome))

    def fechar(self, nome):
        if nome in self.SFD:
            part = self.SFD[nome]
            _, arquivo = self.particoes[part]
            arquivo.aberto = False
            if not arquivo.fila:
                raise Mensagem("arquivo {} fechado com sucesso".format(nome))
            else:
                raise Mensagem("job desempilhado", arquivo.fila.pop())
        else:
            raise Mensagem('arquivo nao esta aberto')

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
        print("--------------------------------------------------------------")
        print("| Particao |     Nome     | Proprietario | Tamanho | Acesso  |")
        print("|----------|--------------|--------------|---------|---------|")
        i = 0
        while i < len(self.particoes):
            _, arquivo = self.particoes[i]
            nome = arquivo.nome
            tamanho = arquivo.tamanho
            proprietario = arquivo.proprietario
            controle = arquivo.controle
            print("| {Particao:^8} | {Nome:12} | {Proprietario:12} | {Tamanho:<7} | {Acesso:7} |".format(Particao=i, Nome=nome, Proprietario=proprietario, Tamanho=tamanho, Acesso=controle))
            i += 1
        print("|------------------------------------------------------------|")
        print("| Espaco ocupado: {:<42} |".format(self.espaco_ocupado))
        print("| Espaco desalocado: {:<39} |".format(self.espaco_disponivel()))
        print("--------------------------------------------------------------")

class Arquivo(object):
    def __init__(self, nome, tamanho, proprietario, controle):
        self.nome = nome
        self.tamanho = tamanho
        self.controle = controle
        self.proprietario = proprietario
        self.conteudo = ''
        self.aberto = False
        self.fila = []

    def ler(self):
        return self.conteudo

    def escrever(self, novo_conteudo):
        self.conteudo = novo_conteudo

    def __del__(self):
        self.aberto = False
