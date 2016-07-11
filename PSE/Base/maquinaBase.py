#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""base class for Maquina."""

class MaquinaBase(object):
    """Provides a base class (or an interface) of a machine to the Simulador class algorithm. Do not instantiate it."""

    def __init__(self):
        """constructor."""
        self.simulador = None
        u"""@ivar:uma referência para o simulador associado à máquina
        @type: Simulador.Simulador """

    def setSimulator(self, simulador):
        """set a reference of the Simulator caller for the Maquina instance.
        @param simulador: uma referência para o simulador associado à máquina
        @type simulador: Simulador"""
        from PSE.Base.simulador import Simulador
        if isinstance(simulador, Simulador):
            self.simulador = simulador

    def trataEvento(self, task):
        """chama a sub-rotina apropriada que trata o evento dado.
        @param task: o evento a ser tratado
        @type task: string
        """
        if task in self.Eventos:
            self.__class__.Eventos[task](self)

    def fim(self, task):
        """returns if the task is a final task (end of simulation)
        @param task: o evento a ser testado
        @type task: string
        @return: bool
        """
        return False

    Eventos = dict()
