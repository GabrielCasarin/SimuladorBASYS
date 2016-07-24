# coding=utf-8
u"""Simulador Estocástico dirigido por Eventos."""
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


from PSE.Base.lista import ListaPrioritaria
from PSE.Base.maquinaBase import MaquinaBase
import itertools

class Simulador(object):
    """simulate a machine according to the McDougall algorithm."""

    def __init__(self, machine=None):
        u"""constructor.
        @param machine: uma instancia de uma máquina a ser simulada
        @type machine: Maquina"""
        self._listaEventos = ListaPrioritaria()
        self._agora = 0
        self.serie = itertools.count()

        if isinstance(machine, MaquinaBase):
                self._Maquina = machine
                self._Maquina.setSimulator(self)

    def addTask(self, task, priority, time):
        """Add a new task."""
        self._listaEventos.push((next(self.serie), task), priority, time) # diminui a prioridade de quem chegou depois

    def nextTask(self):
        """Remove and return the lowest priority task."""
        p = self._listaEventos.pop()
        return p[0][1], p[1]

    def simulate(self):
        """Run the simulation."""
        chegouFimSimulacao = False
        print("##  STARTED simulation at:", self._agora, " ##")

        while len(self._listaEventos) > 0 and not chegouFimSimulacao:
            task, time = self.nextTask()
            self._agora = max(self._agora, time)
            self._Maquina.trataEvento(task)
            chegouFimSimulacao = self._Maquina.fim(task)

        print("## STOPED simulation at:", self._agora, " ##")
