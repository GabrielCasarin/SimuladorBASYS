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

import os
import json
from PSE.SO import Job
from PSE.SO import Maquina
from PSE.SO import Evento
from PSE.Base import Simulador


def main():
    etc = os.path.join(os.curdir, 'PSE', 'SO', 'etc')

    ## Le os parametro globais da simulacao
    with open(os.path.join(etc, 'parametros_simulador.json')) as conf_sim:
        parametros = json.load(conf_sim)

    with open(os.path.join(etc, 'arquivos.json')) as arquivos_conf:
        arquivos_conf_dict = json.load(arquivos_conf)

    nome_arq_jobs = input('Digite o nome do arquivo de especificacao dos jobs: ') + '.json'
    # nome_arq_jobs = 'jobs2.json'
    with open(os.path.join(etc, nome_arq_jobs)) as arq_jobs:
      jobs_conf = json.load(arq_jobs)

      # determina o tempo de inicio do clock
      T_acionamento_clk = jobs_conf['T_acionamento_clk']
      # e o de termino da simulacao
      T_final = jobs_conf['T_final_clk']

      # carrega todos os jobs que serao simulados
      jobs = []
      for job in jobs_conf['jobs']:
          # cria um novo job
          novo_job = Job(nome=job['nome'],      # identificador do job
                        T_chegada=job['Ti'],    # tempo de chegada
                        T_MaxCPU=job['Tmax'],       # tempo maximo de cpu
                        segmentos=job['segmentos'], # estrutura de segmentos do tipo (nome, tamanho)
                        arquivos=job['arquivos'],   # lista de arquivos
                        DiscoCount=job['IO'],   # quantidade de acessos ao disco
                        ImpressoraCount=job['P'],   # quantidade de impressoes
                        LeitoraCount=job['R']   # quantidade de leituras
                     )

          jobs.append(novo_job)

    mac = Maquina(T_acionamento_clk, T_final, arquivos_conf_dict=arquivos_conf_dict,**parametros)
    sim = Simulador(mac)

    for job in jobs:
      eventoChegadaJob = Evento('<Iniciar>', job.T_chegada, job)
      sim.addTask(eventoChegadaJob, 1, eventoChegadaJob.T_ocorrencia)

    ## Roda a simulacao
    sim.simulate()

    print('\n')
    print('################')
    print('#     Jobs     #')
    print('################')
    for job in jobs:
        job.log_job()
        print()

if __name__ == '__main__':
    main()
