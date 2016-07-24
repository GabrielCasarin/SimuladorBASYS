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
from PSE.SO import Segmento, Mensagem


class Memoria(object):
    def __init__(self, T_relocacao, T_acesso, tamanho):
        super(Memoria, self).__init__()
        self.tamanho = tamanho
        self.mem_disponivel = tamanho
        self.T_relocacao = T_relocacao
        self.segmentos = dict()
        self.fila = ListaPrioritaria()
        self.agora = 0

    def requisitar(self, nome, tamamanhoSegmento, job, tempoAtual):
        # verificam se o segmento ja foi alocado ao job
        for seg in self.segmentos:
            if self.segmentos[seg].nome == nome and \
                self.segmentos[seg].job == job:
                    raise Mensagem('segmento ja alocado')

        # caso nao haja espaco suficiente
        if tamamanhoSegmento > self.mem_disponivel:
            self.fila.push((nome, tamamanhoSegmento, job), 1, tempoAtual)
            raise Mensagem('inserido na fila da memoria')
        else:
        # caso haja
            self.mem_disponivel -= tamamanhoSegmento
            novoSegmento = Segmento(nome, tamamanhoSegmento, job)
            self.segmentos[nome] = novoSegmento
            raise Mensagem('alocado com sucesso')


    def liberar(self, nome):
        if nome in self.segmentos:
            self.mem_disponivel += self.segmentos[nome].tamamanhoSegmento
            self.segmentos.pop(nome)
            if len(self.fila) > 0:
                # verifica se ha possibilidade de colocar novo segmento na memoria
                p, t = self.fila.pop()
                tamamanhoSegmento = p[1]
                if tamamanhoSegmento <= self.mem_disponivel:
                    raise Mensagem('processo desempilhado', p)
                else:
                    # se nao adianta tentar alocar memoria, coloca de novo na fila com mesmo tempo de chegada
                    self.fila.push(p, 1, t)
            else:
                raise Mensagem('espaco liberado')
        else:
            raise Mensagem('segmento nao encontrado', nome)
