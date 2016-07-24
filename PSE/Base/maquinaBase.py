#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""base class for Maquina."""
# Copyright (c) 2016 Gabriel Casarin da Silva.

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


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
