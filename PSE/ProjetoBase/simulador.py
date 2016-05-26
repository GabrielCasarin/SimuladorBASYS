#!/usr/bin/env python3
# -*- coding: utf-8 -*-
u"""Simulador Estocástico dirigido por Eventos."""
import datetime
from PSE.ProjetoBase.lista import ListaPrioritaria
from PSE.ProjetoBase.maquina import MaquinaBase


class Simulador(object):
    """simulate a machine according to the McDougall algorithm."""

    def __init__(self, machine=None):
        u"""constructor.
        @param machine: uma instancia de uma máquina a ser simulada
        @type machine: Maquina"""
        self._listaEventos = ListaPrioritaria()
        self._agora = datetime.timedelta()

        if isinstance(machine, MaquinaBase	):
                self._Maquina = machine
                self._Maquina.setSimulator(self)

    def addTask(self, task, priority, time):
        """Add a new task."""
        self._listaEventos.push(task, priority, self._agora + time)

    def nextTask(self):
        """Remove and return the lowest priority task."""
        return self._listaEventos.pop()

    def simulate(self):
        """Run the simulation."""
        chegouFimSimulacao = False
        print("##  STARTED simulation at:", self._agora, " ##")

        while len(self._listaEventos) > 0 and not chegouFimSimulacao:
            task, time = self.nextTask()
            self._Maquina.trataEvento(task)
            self._agora = max(self._agora, time)
            chegouFimSimulacao = self._Maquina.fim(task)
            self._Maquina.printEvent(task)

        print("## STOPED simulation at:", self._agora, " ##")
