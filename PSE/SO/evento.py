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


class Evento(object):
    """docstring for Evento"""
    def __init__(self, tipo, T_ocorrencia, job=None, recurso=None):
        super(Evento, self).__init__()
        self.tipo = tipo
        self.T_ocorrencia = T_ocorrencia
        self.job = job
        self.recurso = recurso

    def __str__(self):
        if self.recurso is not None:
            return "{0:>5}:\t{1:<20}\trecurso utilizado -> {2}".format(self.T_ocorrencia, self.tipo, self.recurso)
        else:
            return "{0:<5}:{1:<20}".format(self.T_ocorrencia, self.tipo)
