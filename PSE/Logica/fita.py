#!/usr/bin/env python3
# -*- coding: utf-8 -*-
u"""Classe Fita para Autômatos Finitos e Máquinas de Turing."""


class Fita:
    u"""Classe Fita para Máquinas de Turing e Autômatos Finitos."""

    def __init__(self, cadeiaInicial="", max_length=None):
        self._max_length = max_length
        self.iniciar(cadeiaInicial)

    def iniciar(self, cadeiaInicial, comecarDoComeco=True):
        # '#' simboliza o final da cadeia de entrada
        self._cadeia = list(cadeiaInicial)[0:self._max_length] + ['#']
        self._cursor = 0 if comecarDoComeco else len(cadeiaInicial)
        self._cursorUltimoSimboloLido = self._cursor

    def ler(self):
        self._cursorUltimoSimboloLido = self._cursor
        return self._cadeia[self._cursor]

    def gravar(self, simbolo):
        if len(simbolo) == 1:
            if self._cadeia[self._cursor] == '#' and self._cursor == len(self._cadeia)-1:
                self._cadeia.append('#')
            self._cadeia[self._cursor] = simbolo

    def avancar(self):
        if self._max_length is not None:
            if self._cursor < self._max_length-1:
                self._cursor += 1
        else:
            if self._cursor >= len(self._cadeia)-1:
                self._cadeia.append('#')
            self._cursor += 1

    def recuar(self):
        if self._cursor > 0:
            self._cursor -= 1
        else:
            raise Exception('Recuo aquem da fita')

    def __str__(self, cursor=True):
        i = self._cursorUltimoSimboloLido if not cursor else self._cursor
        return ''.join(self._cadeia[:i]) + self._cadeia[i] + ''.join(self._cadeia[i+1: self._max_length])
