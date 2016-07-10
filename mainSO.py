from PSE.SO import Job, Maquina
from PSE.Base import Simulador
from math import floor, ceil
import random
import re

with open('parametros_simulador.txt') as conf_sim:
    linhas = conf_sim.readlines()
    for i in range(len(linhas)):
        linhas[i]= re.split(r'\s*=\s*', linhas[i][:-1])
    for atributo in linhas:
        if atributo[0] == 'time_slice_size':
          time_slice_size = int(atributo[1])
        elif atributo[0] == 'max_processos':
          max_processos = int(atributo[1])
        elif atributo[0] == 'disco_tempo_leitura':
          disco_tempo_leitura = int(atributo[1])
        elif atributo[0] == 'disco_tempo_escrita':
          disco_tempo_escrita = int(atributo[1])
        elif atributo[0] == 'disco_tamanho':
          disco_tamanho = int(atributo[1])
        elif atributo[0] == 'memoria_tempo_transferencia':
          memoria_tempo_transferencia = int(atributo[1])
        elif atributo[0] == 'memoria_tamanho':
          memoria_tamanho = int(atributo[1])

 
# time_slice_size
# max_processos
# disco_tempo_leitura
# disco_tempo_escrita
# disco_tamanho
# memoria_tempo_transferencia
# memoria_tamanho


# with open('so1.txt') as fin:
#   linhas = fin.readlines()
#   T_acionamento_clk = int(linhas[0])
#   T_final = int(linhas[1])
#
#   jobs = list()
#
#   for linha in linhas[2:]:
#       linha = linha.split()
#       nome = linha[0]
#       ti, tmax, memqtde, ioqtde = [int(p) for p in linha[1:]]
#
#       times = [i*tmax/(ioqtde + 1) for i in range(1, ioqtde + 1)]
#       random.seed(tmax+ti)
#       m = map(lambda e: e+random.gauss(0.0, tmax*.08), times)
#       times = [ceil(e) for e in m]
#       jobs.append(Job(nome=nome, tChegada=ti, tMaxCPU=tmax, tamMem=memqtde, IOcount=ioqtde, printCount=0))
#       print(times)
#       print(jobs[0].nome, jobs[0].tChegada, jobs[0].tMaxCPU, jobs[0].tamMem, jobs[0].IOcount)
#
#   mac = Maquina(T_acionamento_clk, T_final, jobs)
#   sim = Simulador(mac)
#   for job in jobs:
#       eventoInicial = Evento
#       sim.addTask()
