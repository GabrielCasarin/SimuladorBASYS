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

        if 'estadoIncial' in kwargs and kwargs['estadoIncial'] is not None:
            self._estadoInicial = next(filter(lambda estado: estado == kwargs['estadoIncial'], self._estados))

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
                simbEscrito, mov = group[5:7]
                index = self._estados.index(estIni)
                self._estados[index][simbLido] = (proxEst, simbEscrito, mov)

        self._cadeiaInicial = kwargs['cadeia']

        self._estadoAtual = None
        self._simboloAtual = None
        self._bufferSimboloEscrita = None
        self._proxMovimento = None


    def PartidaInicial(self):
        self._estadoAtual = self._estadoInicial
        self._fita.iniciar(self._cadeiaInicial)
        self._simulator.addTask('<LeituraSimbolo>', 1, datetime.timedelta(seconds=1))


    def LeituraSimbolo(self):
        self._simboloAtual = self._fita.ler()
        houveTransicao = self.fazerTransicao()


    def GravacaoSimbolo(self):
        # grava o simbolo que esta no buffer na memoria da fita
        self._fita.gravar(self._bufferSimboloEscrita)
        # movimenta o cursor dependendo da movimentacao programada
        if self._proxMovimento == '>':
            self._simulator.addTask('<CabecoteParaDireita>', 1, datetime.timedelta(seconds=1))

        elif self._proxMovimento == '<':
            self._simulator.addTask('<CabecoteParaEsquerda>', 1, datetime.timedelta(seconds=1))
            
        # caso o movimento programado nao seja nem para direita nem para esquerda
        else:
            self._simulator.addTask('<Erro>', 0, datetime.timedelta(seconds=1))


    def CabecoteParaDireita(self):
        self._fita.avancar()
        self._simulator.addTask('<LeituraSimbolo>', 1, datetime.timedelta(seconds=1))


    def CabecoteParaEsquerda(self):
        self._fita.recuar()
        self._simulator.addTask('<LeituraSimbolo>', 1, datetime.timedelta(seconds=1))


    def AtingiuEstadoH(self):
        pass


    def Bloqueio(self):
        pass


    def Erro(self):
        pass


    def fazerTransicao(self):
        pass


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
