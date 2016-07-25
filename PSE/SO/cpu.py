# coding=utf-8

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


from PSE.Base import ListaPrioritaria
from PSE.SO import Mensagem

class CPU(object):
    def __init__(self, timeSlice):
        super(CPU, self).__init__()
        self.timeSlice = timeSlice
        self.busy = False
        self.fila = ListaPrioritaria()
        self.job_em_execucao = None
        self.agora = 0

    def reserva(self, job, prioridade):
        if self.busy:
            if job not in self.fila:
                self.fila.push(job, 1, self.agora)
            raise Mensagem('inserido na fila da CPU')
        else:
            self.job_em_execucao = job
            self.busy = True
            raise Mensagem('alocado com sucesso')

    def libera(self):
        self.busy = False
        self.job_em_execucao = None
        if self.fila:
            raise Mensagem('job desempilhado', self.fila.pop())
        else:
            raise Mensagem('CPU livre')
