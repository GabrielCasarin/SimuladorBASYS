from PSE.SO import Job, Maquina, Evento
from PSE.Base import Simulador
import json
# import re

def main():
    ## Le os parametro globais da simulacao
    with open('parametros_simulador.json') as conf_sim:
        parametros = json.load(conf_sim)

    with open('arquivos.json') as arquivos_conf:
        arquivos_conf_dict = json.load(arquivos_conf)

    # nome_arq_jobs = input('Digite o nome do arquivo de especificacao dos jobs: ')
    nome_arq_jobs = 'jobs1.json'
    with open(nome_arq_jobs) as arq_jobs:
      jobs_conf = json.load(arq_jobs)

      # determina o tempo de inicio do clock
      T_acionamento_clk = jobs_conf['T_acionamento_clk']
      # e o de termino da simulacao
      T_final = jobs_conf['T_final_clk']

      # carrega todos os jobs que serao simulados
      jobs = jobs_conf['jobs']
      for job in jobs:

          # cria um novo job
          novo_job = Job(nome=job['nome'],      # identificador do job
                        T_chegada=job['Ti'],    # tempo de chegada
                        T_MaxCPU=job['Tmax'],       # tempo maximo de cpu
                        segmentos=job['segmentos'], # estrutura de segmentos do tipo (nome, tamanho)
                        arquivos=job['arquivos'],
                        DiscoCount=job['IO'],              # quantidade de acessos ao disco
                        ImpressoraCount=job['impressoes'], # quantidade de impressoes
                        LeitoraCount=job['leituras']       # quantidade de leituras
                     )
          novo_job.log_job()

    #       jobs.append(novo_job)

    # mac = Maquina(T_acionamento_clk, T_final, **parametros)#, jobs=jobs)
    # sim = Simulador(mac)
    # for job in jobs:
    #   eventoChegadaJob = Evento('<Iniciar>', job.T_chegada, job)
    #   sim.addTask(eventoChegadaJob, 1, eventoChegadaJob.T_ocorrencia)
    # sim.simulate()
    #
    # print('\n')
    # print('################')
    # print('#     Jobs     #')
    # print('################')
    # for job in jobs:
    #     job.log_job()
    #     print()

if __name__ == '__main__':
    main()
