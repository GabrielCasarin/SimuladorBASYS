#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Contém funções auxiliares à análise dos arquivos de especificação de autômatos
'''
import re

def parse(spec_input, tipo=None, nome=None):
    """
    Dada uma especificação dada em spec_input, retorna um dicionário contendo os campos decodificados.
    parse([string]) -> [dict]
    """
    if nome is None:
        nome = '\w+'
    if tipo is None:
        tipo = 'AF|AP|MT'
    dictRetorno = dict()
    dictRetorno.setdefault('estados', None)
    dictRetorno.setdefault('alfabeto', None)
    dictRetorno.setdefault('alfabetoGama', None)
    dictRetorno.setdefault('transicoes', None)
    dictRetorno.setdefault('sub-maquinas', None)
    dictRetorno.setdefault('estadoIncial', None)
    dictRetorno.setdefault('estadosFinais', None)
    dictRetorno.setdefault('nomeMaquina', None)
    # dictRetorno.setdefault('', None)

    stringMatchPattern = '(?P<type_tag>{tipo})\s+<(?P<nomeMaquina>{nome})>\s+is\n(?P<conteudoDescricao>.*)\n\s*end\s+<(?P=nomeMaquina)>\s*;'.format(tipo=tipo, nome=nome)
    matchObj = re.search(stringMatchPattern, spec_input, re.DOTALL)
    if matchObj is not None:
        nomeMaquina, conteudoDescricao = matchObj.group('nomeMaquina', 'conteudoDescricao')
        # print(nomeMaquina, conteudoDescricao)
        dictRetorno['nomeMaquina'] = nomeMaquina
        for conjunto in re.finditer('^\s*(?P<nomeConjunto>estados|Q|alfabeto|E|Σ|alfabetoGama|Γ|transicoes|d|δ|sub-maquinas|S|I|F)\s*=\s*{(?P<elementos>.*?)}(?:\n|$)', conteudoDescricao, re.MULTILINE | re.DOTALL):
            nomeConjunto, elementos = conjunto.group('nomeConjunto', 'elementos')
            # print(nomeConjunto, elementos)
            # analisa transições
            if re.search('transicoes|d|δ', nomeConjunto) is not None:
                dictRetorno['transicoes'] = []
                regraIterator = re.finditer('\((?P<el1>\w+),\s*(?P<el2>.*?)\s*\)\s*->\s*(?:(?P<par>\()?(?P<el3>\w+)(?:/(?P<el4>\w+)|\s*,\s*(?P<el5>\w+)\s*,\s*(?P<el6>[DE]))?(?(par)\)))\s*(?:,|$)', elementos, re.DOTALL)
                for regra in regraIterator:
                    dictRetorno['transicoes'].append(regra.groups())
            # analisa alfabeto de fita
            elif re.search('alfabeto|E|Σ', nomeConjunto) is not None:
                dictRetorno['alfabeto'] = []
                tokenPattern = re.compile('\'(?P<token>[^\n]+?)\'')
                for tok in tokenPattern.finditer(elementos):
                    dictRetorno['alfabeto'].append(tok.group('token'))
            # analisa alfabeto Gama
            elif re.search('alfabetoGama|G|Γ', nomeConjunto) is not None:
                dictRetorno['alfabetoGama'] = []
                tokenPattern = re.compile('\'(?P<token>[^\n]+?)\'')
                for tok in tokenPattern.finditer(elementos):
                    dictRetorno['alfabetoGama'].append(tok.group('token'))
            # analisa estados
            elif re.search('estados|Q', nomeConjunto):
                dictRetorno['estados'] = re.split(',', elementos.replace(' ', ''))
            # analisa sub-máquinas
            elif re.search('sub-maquinas|S', nomeConjunto) is not None:
                dictRetorno['sub-maquinas'] = []
                for subm in re.finditer('<(?P<nomeMaquina>\w+)>\s*(?:,|$)', elementos):
                    dictRetorno['sub-maquinas'].append(subm.group('nomeMaquina'))
            elif nomeConjunto == 'I':
                dictRetorno['estadoIncial'] = re.split(',', elementos.replace(' ', ''))[0]
            elif nomeConjunto == 'F':
                dictRetorno['estadosFinais'] = re.split(',', elementos.replace(' ', ''))

    return dictRetorno


def parseMT(spec_input, nome=None):
    return parse(spec_input, tipo='MT', nome=nome)

def parseAP(spec_input, nome=None):
    return parse(spec_input, tipo='AP', nome=nome)

def parseAF(spec_input, nome=None):
    return parse(spec_input, tipo='AF', nome=nome)
