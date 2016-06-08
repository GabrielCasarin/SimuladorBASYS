#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime

from PSE.ProjetoBase.maquinaBase import MaquinaBase
from PSE.ProjetoLogica.fita import Fita
from PSE.ProjetoLogica.estado import Estado


class AutomatoFinito(MaquinaBase):
    """docstring for AutomatoFinito"""
    def __init__(self, **kwargs):
        super(AutomatoFinito, self).__init__()

        self._fita = Fita() if 'fita' not in kwargs else kwargs['fita']
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

        # transicoes
        if 'transicoes' in kwargs and kwargs['transicoes'] is not None:
            for group in kwargs['transicoes']:
                estIni, simbLido = group[:2]
                proxEst = group[3]
                index = self._estados.index(estIni)
                self._estados[index][simbLido] = next(filter(lambda estado: estado == proxEst, self._estados))

        self._cadeiaInicial = kwargs['cadeia']

        self._estadoAtual = None
        self._simboloAtual = None


    # methods for events management

    def PartidaInicial(self):
        u"""põe o Automato Finito no Estado Inicial e da outras providências."""
        self._estadoAtual = self._estadoInicial
        self._fita.iniciar(self._cadeiaInicial)
        self._simulator.addTask('<LeituraSimbolo>', 1, datetime.timedelta(seconds=1))

    def LeituraSimbolo(self):
        u"""atualiza o símbolo atual e dá outras providências."""

        self._simboloAtual = self._fita.ler()
        houveTransicao = self.fazerTransicao()

        if houveTransicao:
            self._simulator.addTask('<CabecoteParaDireita>', 1, datetime.timedelta(seconds=1))
        else:  # se não houve transição, há quatro hipóteses possíveis
            # se a cadeia acabou e se se atigingiu um estado final
            if self._estadoAtual.isFinal() and self._simboloAtual == '#':
                self._simulator.addTask('<AtingiuEstadoFinal>', 0, datetime.timedelta())
            # ou em qualquer outro caso
            else:
                self._simulator.addTask('<Erro>', 0, datetime.timedelta())


    def CabecoteParaDireita(self):
        self._fita.avancar()
        self._simulator.addTask('<LeituraSimbolo>', 1, datetime.timedelta(seconds=1))

    def AtingiuEstadoFinal(self):
        print("cadeia", self._cadeiaInicial, "aceita.")
        self._simulator.addTask('<FimSimulacao>', 0, datetime.timedelta())

    def Erro(self):
        print("cadeia", self._cadeiaInicial, "NAO foi aceita.")
        self._simulator.addTask('<FimSimulacao>', 0, datetime.timedelta())

    def FimSimulacao(self):
        pass


    def fazerTransicao(self):
        if self._simboloAtual != '#':   # se não se consumiu todos os caracteres
            if self._simboloAtual in self._estadoAtual:  # verifica se há transição associada ao simboloAtual in estadoAtual
                proxEst = self._estadoAtual[self._simboloAtual]
                self._estadoAtual = proxEst
                return True

        # retorna False em dois casos:
        #    1) atigingiu-se o fim da cadeia; ou
        #    2) não havia regra associada ao par (estadoAtual, simboloAtual)
        return False


    Eventos = {
        '<PartidaInicial>': PartidaInicial,
        '<LeituraSimbolo>': LeituraSimbolo,
        '<CabecoteParaDireita>': CabecoteParaDireita,
        '<AtingiuEstadoFinal>': AtingiuEstadoFinal,
        '<Erro>': Erro,
        '<FimSimulacao>': FimSimulacao
    }

    def printEvent(self, taskType):
        print("({estado}, {cadeia}) :".format(estado=self._estadoAtual, cadeia=self._simboloAtual), taskType)

    def getConfiguracao(self):
        return self._estadoAtual, self._simboloAtual
