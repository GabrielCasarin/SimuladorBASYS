from PSE.SO import Job, Maquina, Evento
from PSE.Base import Simulador
import re

## Le os parametro globais da simulacao
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
        elif atributo[0] == 'memoria_tempo_relocacao':
          memoria_tempo_relocacao = int(atributo[1])
        elif atributo[0] == 'memoria_tempo_transferencia':
          memoria_tempo_transferencia = int(atributo[1])
        elif atributo[0] == 'memoria_tamanho':
          memoria_tamanho = int(atributo[1])

with open('so1.txt') as arq_jobs:
  linhas = arq_jobs.readlines()
  # determina o tempo de inicio do clock
  T_acionamento_clk = int(linhas[0])
  # e o de termino da simulacao
  T_final = int(linhas[1])

  # carrega todos os jobs que serao simulados
  padrao = re.compile(r'\((\w),([0-9]+)\)')
  jobs = list()
  for linha in linhas[2:]:  # pula as duas primeiras linhas do arquivo de jobs
      linha = linha.split()
      nome = linha[0] # identificador do job
      ti = int(linha[1]) # tempo de chegada
      tmax = int(linha[2]) # tempo maximo de cpu
      estrutura_seg = list() # estrutura de segmentos do tipo (nome, tamanho)
      seg_iter = padrao.finditer(linha[3])
      for seg in seg_iter:
          estrutura_seg.append((seg.group(1),int(seg.group(2))))
      ioqtde = int(linha[4]) # quantidade de acessos ao disco

      # cria um novo job
      novo_job = Job(nome, T_chegada=ti, T_MaxCPU=tmax, segmentos=estrutura_seg, DiscoCount=0, LeitoraCount=0, ImpressoraCount=0)
      jobs.append(novo_job)

mac = Maquina(T_acionamento_clk, T_final, time_slice_size=time_slice_size, max_processos=max_processos, disco_tempo_leitura=disco_tempo_leitura, disco_tempo_escrita=disco_tempo_escrita, disco_tamanho=disco_tamanho, memoria_tempo_relocacao=memoria_tempo_relocacao, memoria_tempo_transferencia=memoria_tempo_transferencia, memoria_tamanho=memoria_tamanho)#, jobs=jobs)
sim = Simulador(mac)
for job in jobs:
  eventoChegadaJob = Evento('<Iniciar>', job.T_chegada, job)
  sim.addTask(eventoChegadaJob, 1, eventoChegadaJob.T_ocorrencia)
