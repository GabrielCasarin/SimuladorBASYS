#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime

from PSE.Base.maquina import MaquinaBase
from PSE.Logica.fita import Fita
from PSE.Logica.estado import Estado
from PSE.Logica.automatoFinito import AutomatoFinito


class AutomatoPilhaEstruturado(MaquinaBase):
    """docstring for AutomatoPilhaEstruturado"""
    def __init__(self, **kwargs):
        super(AutomatoPilhaEstruturado, self).__init__()

        self._fita = Fita()  # if 'fita' not in kwargs else kwargs['fita']
        u"""@ivar:Uma fita para servir de memória ao Autômato
        @type: Fita"""
        self._pilha = None

        if 'nomeMaquina' in kwargs and kwargs['nomeMaquina'] is not None:
            self._nome = kwargs['nomeMaquina']

        # sub-maquinas
        if 'sub-maquinas' in kwargs and kwargs['sub-maquinas'] is not None:
            self._subMaquinasDict = dict()
            for subMaqDict in kwargs['sub-maquinas']:
                subMaq = AutomatoFinito(fita=self._fita, **subMaqDict)
                self._subMaquinasDict[subMaq._nome] = subMaq

        # transicoes
        if 'transicoes' in kwargs and kwargs['transicoes'] is not None:
            self._chamadaSubMaq = dict()
            for group in kwargs['transicoes']:
                nomeSubMaq, estadoChamada = group[:2]
                proxSubMaq = group[3]
                estadoRetorno = group[4]
                submaqtransition = Estado(nomeSubMaq)
                submaqtransition[estadoChamada] = (proxSubMaq, estadoRetorno)
                self._chamadaSubMaq[nomeSubMaq] = submaqtransition

        # sub-maquina inicial
        if 'estadoInicial' in kwargs and kwargs['estadoInicial'] is not None:
            self._submaquinaInicial = kwargs['estadoInicial'][1:-1]

        self._cadeiaInicial = kwargs['cadeia']

        self._pilha = list()

    def PartidaInicial(self):
        """põe o Automato de Pilha Estruturado no estado inicial e dá outras providências."""
        self._submaquinaAtual = self._subMaquinasDict[self._submaquinaInicial]
        self._submaquinaAtual.inicializar()
        self._fita.iniciar(self._cadeiaInicial)
        self._simulator.addTask('<LeituraSimbolo>', 1, datetime.timedelta(seconds=1))

    def LeituraSimbolo(self):
        """atualiza o símbolo atual e dá outras providências."""
        # lê  o próximo símbolo da fita e atualiza
        simboloAtual = self._fita.ler()
        self._submaquinaAtual._simboloAtual = simboloAtual

        # tenta fazer uma transição dentro da sub-máquina atual
        houveTransicao = self._submaquinaAtual.fazerTransicao()

        # determina próximo passo da execução
        if houveTransicao:
            self._simulator.addTask('<CabecoteParaDireita>', 1, datetime.timedelta(seconds=1))
        # se está em estado final, vê se a pilha esta vazia ou não
        # elif self._submaquinaAtual._estadoAtual.isFinal():
        #     if self._pilha:
        #         self._simulator.addTask('<RetornoSubmaquina>', 1, datetime.timedelta(seconds=1))
        #     elif not self._pilha:
        #         self._simulator.addTask('<AtingiuEstadoFinal>', 1, datetime.timedelta(seconds=1))
        # tenta transitar
        else:
            tagMaqAtual = self._submaquinaAtual._nome
            estadoAtual = self._submaquinaAtual._estadoAtual._nome

            # verifica se há uma chamada possível entre sub-máquinas
            if tagMaqAtual in self._chamadaSubMaq and estadoAtual in self._chamadaSubMaq[tagMaqAtual]:
                self._simulator.addTask('<ChamadaSubmaquina>', 1, datetime.timedelta(seconds=1))
            # caso não fôra possível fazer uma transição desde a sub-máquina atual, analisa as ações passíveis de serem tomadas
            else:
                # se a sub-máquina atual estiver em um estado final,
                if self._submaquinaAtual._estadoAtual.isFinal():
                    #  1) se a cadeia foi consumida por completo, resta saber se a pilha também o fôra
                    if self._submaquinaAtual._simboloAtual == '#':
                            if not self._pilha:
                                #  A pilha está vazia => não há retorno a realizar
                                self._simulator.addTask('<AtingiuEstadoFinal>', 0, datetime.timedelta())
                            else:
                                self._simulator.addTask('<Erro>', 0, datetime.timedelta())
                    #   2) se se está em estado final e resta cadeia para analisar, retorna para sub-máquina anterior
                    else:
                        self._simulator.addTask('<RetornoSubmaquina>', 1, datetime.timedelta(seconds=1))
                # se não houve transição e não se chegou a um estado final, logo não houve reconhecimento da cadeia
                else:
                    self._simulator.addTask('<Erro>', 0, datetime.timedelta())


    def CabecoteParaDireita(self):
        """avança um caracter da fita"""
        self._fita.avancar()
        self._simulator.addTask('<LeituraSimbolo>', 1, datetime.timedelta(seconds=1))

    def AtingiuEstadoFinal(self):
        print("cadeia", self._cadeiaInicial, "aceita.")
        self._simulator.addTask('<FimSimulacao>', 0, datetime.timedelta())

    def ChamadaSubmaquina(self):
        tagMaqAtual = self._submaquinaAtual._nome
        estadoAtual = self._submaquinaAtual._estadoAtual._nome

        # Pega a próxima sub-máquina e o estado de retorno
        proxMaquina, estadoRetorno = self._chamadaSubMaq[tagMaqAtual][estadoAtual]
        # Empilha a sub-máquina de retorno e o estado de retorno
        self._pilha.append((tagMaqAtual, estadoRetorno))

        self._submaquinaAtual = self._subMaquinasDict[proxMaquina]
        self._submaquinaAtual.inicializar()
        self._simulator.addTask('<LeituraSimbolo>', 1, datetime.timedelta(seconds=1))

    def RetornoSubmaquina(self):
        if len(self._pilha) > 0:
            submaqRet, estadoRetorno = self._pilha.pop()
            self._submaquinaAtual = self._subMaquinasDict[submaqRet]
            self._submaquinaAtual._estadoAtual = next(filter(lambda estado: estado == estadoRetorno, self._submaquinaAtual._estados))
            self._submaquinaAtual._simboloAtual = self._fita.ler()
            self._simulator.addTask('<LeituraSimbolo>', 1, datetime.timedelta(seconds=1))
        else:
            self._simulator.addTask('<Erro>', 0, datetime.timedelta())

    def Erro(self):
        print("cadeia", self._cadeiaInicial, "NAO foi aceita.")
        self._simulator.addTask('<FimSimulacao>', 0, datetime.timedelta())

    def FimSimulacao(self):
        pass


    Eventos = {
        '<PartidaInicial>': PartidaInicial,
        '<LeituraSimbolo>': LeituraSimbolo,
        '<CabecoteParaDireita>': CabecoteParaDireita,
        '<AtingiuEstadoFinal>': AtingiuEstadoFinal,
        '<ChamadaSubmaquina>': ChamadaSubmaquina,
        '<RetornoSubmaquina>': RetornoSubmaquina,
        '<Erro>': Erro,
        '<FimSimulacao>': FimSimulacao
    }

    def printPilha(self):
        pilha = self._pilha
        if pilha:
            pilhaStrs = []
            for el in pilha:
                pilhaStrs.append(" {SubMaq}/{EstRet} |".format(SubMaq=el[0], EstRet=el[1]))

            print('-', end='')
            for elStr in pilhaStrs:
                print('{0:-<{1}}'.format('', len(elStr)), end='')
            print()
            print('|', end='')
            for elStr in pilhaStrs:
                print(elStr, end='')
            print()
            print('-', end='')
            for elStr in pilhaStrs:
                print('{0:-<{1}}'.format('', len(elStr)), end='')
            print()
        else:
            print('----')
            print('|Z0|')
            print('----')


    def printEvent(self, taskType):
        estadoAtual, simboloAtual = self._submaquinaAtual.getConfiguracao()
        print( "({estado}, {cadeia}, {topo}) :".format(estado=estadoAtual, cadeia=simboloAtual, topo=self._submaquinaAtual._nome), taskType)
        self.printPilha()

    def __eq__(self, maq):
    	if isinstance(maq, AutomatoPilhaEstruturado):
    		return self == name._nome
    	else:
    		return self._nome == maq
