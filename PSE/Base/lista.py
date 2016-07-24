# coding=utf-8
"""Lista de eventos."""
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


import heapq as hp


class ListaPrioritaria:
    """Lista que retorna seus elementos em ordem de prioridade e de chegada."""

    def __init__(self):
        """constructor."""
        self.pq = []

    def push(self, task, priority, time):
        entry = [priority, time, task]
        hp.heappush(self.pq, entry)

    def pop(self):
        while self.pq:
            priority, time, task = hp.heappop(self.pq)
            return task, time

    def __len__(self):
        return len(self.pq)

    def __bool__(self):
        return bool(self.pq)

    def __contains__(self, item):
        return item in self.pq
