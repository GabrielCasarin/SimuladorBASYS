from datetime import time, timedelta
import random
from math import floor, ceil

from PSE.SO.job import Job
from PSE.SO.maquina import Maquina


with open('so1.txt') as fin:
  linhas = fin.readlines()
  T_acionamento_clk = int(linhas[0])
  T_final = int(linhas[1])

  jobs = list()

  for linha in linhas[2:]:
      linha = linha.split()
      nome = linha[0]
      ti, tmax, memqtde, ioqtde = [int(p) for p in linha[1:]]

      times = [i*tmax/(ioqtde + 1) for i in range(1, ioqtde + 1)]
      random.seed(tmax+ti)
      m = map(lambda e: e+random.gauss(0.0, tmax*.08), times)
      times = [ceil(e) for e in m]
      jobs.append(Job(nome=nome, tChegada=ti, tMaxCPU=tmax, tamMem=memqtde, IOcount=ioqtde, printCount=0))
      print(times)
      print(jobs[0].nome, jobs[0].tChegada, jobs[0].tMaxCPU, jobs[0].tamMem, jobs[0].IOcount)

  mac = Maquina(T_acionamento_clk, T_final, jobs)
