#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
from PSE.Base.maquina import MaquinaBase
from PSE.Logica.fita import Fita
from PSE.Logica.estado import Estado


class MaquinaTuring(MaquinaBase):
    """docstring for MaquinaTuring"""

    conjuntosValidos = ('estados', 'alfabeto', 'alfabetoGama', )
    def __init__(self, **kwargs):
        super(MaquinaTuring, self).__init__()

        self._fita = Fita()
        u"""@ivar:Uma fita para servir de memória ao Autômato
        @type: Fita"""

        if 'nomeMaquina' in kwargs and kwargs['nomeMaquina'] is not None:
            self._nome = kwargs['nomeMaquina']

        # estados
        if 'estados' in kwargs and kwargs['estados'] is not None:
            self._estados = [Estado(nomeEstado) for nomeEstado in kwargs['estados']]

        if 'estadoInicial' in kwargs and kwargs['estadoInicial'] is not None:
            self._estadoInicial = next(filter(lambda estado: estado == kwargs['estadoInicial'], self._estados))

        if 'estadosFinais' in kwargs and kwargs['estadosFinais'] is not None:
            for nomeEstado in kwargs['estadosFinais']:
                estado = next(filter(lambda estado: estado == nomeEstado, self._estados))
                estado.setFinal()

        # alfabetos
        if 'alfabeto' in kwargs and kwargs['alfabeto'] is not None:
            self._alfabeto = list(kwargs['alfabeto'])

        if 'alfabetoGama' in kwargs and kwargs['alfabetoGama'] is not None:
            self._alfabetoGama = list(kwargs['alfabetoGama'])

        # transicoes
        if 'transicoes' in kwargs and kwargs['transicoes'] is not None:
            for group in kwargs['transicoes']:
                estIni, simbLido = group[:2]
                proxEst = group[3]
                acao = group[5]
                index = self._estados.index(estIni)
                self._estados[index][simbLido] = (proxEst, acao)

        self._cadeiaInicial = kwargs['cadeia']

        self._estadoAtual = None
        self._simboloAtual = None
        self._bufferSimboloEscrita = None
        self._proxMovimento = None


    def PartidaInicial(self):
        self._estadoAtual = self._estadoInicial
        self._fita.iniciar(self._cadeiaInicial, comecarDoComeco=False)
        self._simulator.addTask('<LeituraSimbolo>', 1, datetime.timedelta(seconds=1))


    def LeituraSimbolo(self):
        self._simboloAtual = self._fita.ler()
        houveTransicao = self.fazerTransicao()

        if houveTransicao:
            if self._bufferSimboloEscrita is not None:
                self._simulator.addTask('<GravacaoSimbolo>', 1, datetime.timedelta(seconds=1))
            else:
                # movimenta o cursor dependendo da movimentacao programada
                if self._proxMovimento == '>':
                    self._simulator.addTask('<CabecoteParaDireita>', 1, datetime.timedelta(seconds=1))
                elif self._proxMovimento == '<':
                    self._simulator.addTask('<CabecoteParaEsquerda>', 1, datetime.timedelta(seconds=1))
        else: # se não houve transicao
            if self._estadoAtual.isFinal() and self._simboloAtual == '#':
                self._simulator.addTask('<AtingiuEstadoH>', 0, datetime.timedelta(seconds=1))
            else:
                self._simulator.addTask('<Erro>', 0, datetime.timedelta(seconds=1))


    def GravacaoSimbolo(self):
        # grava o simbolo que esta no buffer na memoria da fita
        self._fita.gravar(self._bufferSimboloEscrita)
        self._bufferSimboloEscrita = None
        self._simulator.addTask('<LeituraSimbolo>', 1, datetime.timedelta(seconds=1))


    def CabecoteParaDireita(self):
        self._fita.avancar()
        self._simulator.addTask('<LeituraSimbolo>', 1, datetime.timedelta(seconds=1))


    def CabecoteParaEsquerda(self):
        try:
            self._fita.recuar()
            self._simulator.addTask('<LeituraSimbolo>', 1, datetime.timedelta(seconds=1))
        except Exception as e:
            self._simulator.addTask('<Bloqueio>', 0, datetime.timedelta(seconds=1))


    def AtingiuEstadoH(self):
        pass


    def Bloqueio(self):
        pass


    def Erro(self):
        pass


    def fazerTransicao(self):
        # se existe uma transicao associada ao estado atual
        if self._simboloAtual in self._estadoAtual:
            nomeProxEst, acao = self._estadoAtual[self._simboloAtual]
            # nomeProxEst, simbDeEscrita, movimento = self._estadoAtual[self._simboloAtual]
            proxEst = next(filter(lambda estado : estado == nomeProxEst, self._estados))
            self._estadoAtual = proxEst
            if acao == '<' or acao == '>':
                self._proxMovimento = acao
                self._bufferSimboloEscrita = None
            else:
                self._proxMovimento = None
                self._bufferSimboloEscrita = acao
            return True
        return False

    def fim(self, task):
        if task == '<FimSimulacao>':
            return True
        return False

    Eventos = {
        '<PartidaInicial>': PartidaInicial,
        '<LeituraSimbolo>': LeituraSimbolo,
        '<GravacaoSimbolo>': GravacaoSimbolo,
        '<CabecoteParaDireita>': CabecoteParaDireita,
        '<CabecoteParaEsquerda>': CabecoteParaEsquerda,
        '<AtingiuEstadoH>': AtingiuEstadoH,
        '<Bloqueio>': Bloqueio,
        '<Erro>': Erro,
    }


    def printEvent(self, task):
        if task == '<PartidaInicial>':
            print("{task}: a Maquina iniciou no estado {est}".format(task=task, est=self._estadoInicial._nome))

        if task == '<LeituraSimbolo>':
            print("{task}: leu o simbolo '{simb}' da fita".format(task=task, simb=self._simboloAtual))

        if task == '<GravacaoSimbolo>':
            print("{task}: gravou o simbolo '{simb}' na fita".format(task=task, simb=self._fita.ler()))

        if task == '<CabecoteParaDireita>':
            print("{task}: movimentou o cursor da fita para DIReita".format(task=task))

        if task == '<CabecoteParaEsquerda>':
            print("{task}: movimentou o cursor da fita para ESQuerda".format(task=task))

        if task == '<AtingiuEstadoH>':
            print("{task}: ".format(task=task))

        if task == '<Bloqueio>':
            print("{task}: o cursor tentou recuar aquem do inicio da fita. Maquina BLOQUEADA".format(task=task))

        if task == '<Erro>':
            print("{task}: atingiu estado de erro.".format(task=task))
            print("Resultado: cadeia {cad} REJEITADA".format(cad=self._cadeiaInicial))

        print("Conf.: {alfa} {estado} {beta}".format(task=task, estado=self._estadoAtual, alfa=''.join(self._fita._cadeia[0:self._fita._cursor]), beta=''.join(self._fita._cadeia[self._fita._cursor:])))
        print()
