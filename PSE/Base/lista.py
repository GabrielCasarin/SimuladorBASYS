#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lista de eventos."""

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
