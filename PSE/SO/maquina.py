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

from PSE.Base import MaquinaBase, Simulador, ListaPrioritaria
from PSE.SO import CPU, Disco, Evento, Impressora, Job, Leitora, Memoria, Mensagem, Segmento

class Maquina(MaquinaBase):
    def __init__(self, T_acionamento_clk, T_final, arquivos_conf_dict, time_slice_size, max_processos, disco_tempo_leitura, disco_tempo_escrita, gerenciador_arquivos_tempo_abertura, disco_tamanho, memoria_tempo_transferencia, memoria_tamanho, impressora_tempo_impressao, leitora_tempo_leitura):#, jobs):
        super(Maquina, self).__init__()

        ## Seta o tempo de acionamento do RTC
        if T_acionamento_clk >= 0:
            self.T_acionamento_clk = T_acionamento_clk
        else:
            self.T_acionamento_clk = 0

        ## Seta o tempo final de máquina
        if T_final >= 0:
            self.T_final = T_final
        else:
            self.T_final = 0

        ## seta os valores das configuracoes globais
        self.max_processos = max_processos

        self.gerenciador_arquivos_tempo_abertura = gerenciador_arquivos_tempo_abertura

        ## dispositivos que a maquina deve conter
        self.CPU = CPU(time_slice_size)
        self.memoria = Memoria(memoria_tempo_transferencia, memoria_tamanho)
        self.disco = Disco(disco_tempo_leitura, disco_tempo_escrita, disco_tamanho, arquivos_conf_dict)
        # impressoras
        self.impressora1 = Impressora('P1', impressora_tempo_impressao)
        self.impressora2 = Impressora('P2', impressora_tempo_impressao)
        self.impressorasID = {
            'P1': self.impressora1,
            'P2': self.impressora2,
        }
        # leitoras
        self.leitora1 = Leitora('L1', leitora_tempo_leitura)
        self.leitora2 = Leitora('L2', leitora_tempo_leitura)
        self.leitorasID = {
            'L1': self.leitora1,
            'L2': self.leitora2,
        }

        ## Job table
        self.job_table = list()

        self.agora = 0

    def trataEvento(self, evento):
        self.sincRelogio(self.simulador._agora)

        if self.agora <= self.T_final:
            if evento.tipo == '<Iniciar>':
                # pega o job que foi carregado durante o carregamento do arquivo de jobs
                # e chama a rotina de inicialização
                self.Iniciar(evento.job)

            elif evento.tipo == '<RequisitarMemoria>':
                job = evento.job
                nome, tamamanhoSegmento, _ = job.prox_segmento()
                self.RequisitarMemoria(nome, tamamanhoSegmento, job, evento.T_ocorrencia)

            elif evento.tipo == '<RequisitarCPU>':
                self.RequisitarCPU(evento.job)

            elif evento.tipo == '<AbrirArquivo>':
                self.AbrirArquivo(evento.job, nome_arquivo=evento.recurso)

            elif evento.tipo == '<AcessarArquivo>':
                self.AcessarArquivo(evento.job, nome_arquivo=evento.recurso)

            elif evento.tipo == '<LiberarDisco>':
                self.LiberarDisco(evento.job)

            elif evento.tipo == '<Imprimir>':
                self.Imprimir(evento.job, evento.recurso)

            elif evento.tipo == '<LiberarImpressora>':
                self.LiberarImpressora(job=evento.job, impressora=evento.recurso)

            elif evento.tipo == '<Leitura>':
                self.Leitura(evento.job, evento.recurso)

            elif evento.tipo == '<LiberarLeitora>':
                self.LiberarLeitora(job=evento.job, leitora=evento.recurso)

            elif evento.tipo == '<LiberarCPU>':
                self.LiberarCPU(evento.job)

            elif evento.tipo == '<LiberarMemoria>':
                self.LiberarMemoria(evento.job)

            elif evento.tipo == '<FinalizarJob>':
                self.FinalizarJob(evento.job)

            elif evento.tipo == '<EncerrarSimulacao>':
                self.EncerrarSimulacao()

    #### Rotinas de tratamento de INTERRUPCOES ####
    ## ---------------- ROTINAS DO JOB --------------- ##
    def Iniciar(self, novo_job):
        # seguindo o modelo de estados proposto no enunciado, todo job ao chegar no sistema entra no estado de 'chegada'
        novo_job.atualizarStatus('chegada')
        # insere o job na tabela de jobs ativos
        self.job_table.append(novo_job)
        # agenda uma requisição de memória
        eventoRequisicaoMem = Evento('<RequisitarMemoria>', novo_job.T_chegada, novo_job)
        self.simulador.addTask(eventoRequisicaoMem, 1, novo_job.T_chegada)
        novo_job.atualizarStatus('aguardando memoria')
        print('{0:<10}<Iniciar>{1:>18}\tchegou. Job inserido na tabela'.format(self.agora, novo_job.nome))

    def FinalizarJob(self, job):
        # calcula o tempo total que o job permaneceu no sistema
        job.tempo_total_sistema = self.agora - job.T_chegada

        # libera a CPU
        try:
            self.CPU.libera()
        except Mensagem as e:
            job.atualizarStatus('completo')
            print("{0:<10}<FinalizarJob>{1:>13}\ttempo maximo de CPU completou-se".format(self.agora, job.nome))
            if e.msg == 'job desempilhado':
                job_desempilhado, tempoEntradaFila = e.value
                job_desempilhado.tempo_espera_CPU += self.agora - tempoEntradaFila
                print('{1:40}job {0} foi desempilhado da fila da CPU'.format(job_desempilhado.nome, ''))
                eventoRequisicaoCPU = Evento('<RequisitarCPU>', self.agora, job=job_desempilhado)
                self.simulador.addTask(eventoRequisicaoCPU, 1, eventoRequisicaoCPU.T_ocorrencia)
            elif e.msg == 'CPU livre':
                print("{0:40}a CPU esta livre".format(''))

        # libera a memoria
        for seg in list(job.segmentos_ativos):
            try:
                self.memoria.liberar(seg)
            except Mensagem as e:
                # remove da lista de segmentos ativos aquele que acabou de ser retirado da memoria
                job.segmentos_ativos.remove(seg)
                if e.msg == 'processo desempilhado':
                    # pega o job que estava pedindo memoria e marca uma requisicao de memoria para ele
                    nome, tamamanhoSegmento, job_desempilhado = e.value
                    eventoRequisicaoMem = Evento('<RequisitarMemoria>', self.agora + tamamanhoSegmento*self.memoria.T_acesso, job_desempilhado)
                    print("{3:40}job {1} liberou o segmento '{2}'".format(self.agora, job.nome, seg, ''))
                    self.simulador.addTask(eventoRequisicaoMem, 1, eventoRequisicaoMem.T_ocorrencia)
                elif e.msg == 'espaco liberado':
                    print("{3:40}job {1} liberou o segmento '{2}'".format(self.agora, job.nome, seg, ''))
                elif e.msg == 'segmento nao encontrado':
                    print("{3:40}falta de segmento {2} (job {1})".format(self.agora, job.nome, e.value, ''))

        # fecha os arquivos
        if job.arquivosAbertos:
            for arquivo in job.arquivosAbertos:
                try:
                    self.disco.fechar(arquivo.nome)
                except Mensagem as e:
                    if e.msg == 'arquivo fechado com sucesso':
                        print("{1:40}arquivo {0} foi fechado com sucesso".format(arquivo.nome, ''))
                    elif e.msg == 'job desempilhado':
                        print("{1:40}arquivo {0} foi fechado com sucesso. Job {2} saiu da fila".format(arquivo.nome, '', e.value.nome))
                        eventoRequisicaoArquivo = Evento('<AbrirArquivo>', self.agora, job=e.value, recurso=arquivo.nome)
                        self.simulador.addTask(eventoRequisicaoArquivo, 1, eventoRequisicaoArquivo.T_ocorrencia)
            print('{0:40}Tabela de Particoes do Disco'.format(''))
            self.disco.log_tabelaParticoes()

        self.job_table.remove(job)
        print("{0:40}job terminou".format(''))

    def EncerrarSimulacao(self):
        print('{0:<10}<EncerrarSimulacao>\t\tSimulacao acabou-se'.format(self.agora))
    ## ---------------- FIM ROTINAS DO JOB --------------- ##

    ## ---------------- MEMORIA CM ---------------- ##
    def RequisitarMemoria(self, nome_seg, tamamanhoSegmento, job, T_ocorrencia):
        agora = self.agora
        try:
            self.memoria.requisitar(nome_seg, tamamanhoSegmento, job, agora)
        except Mensagem as e:
            if e.msg == 'alocado com sucesso' or e.msg == 'segmento ja alocado':
                # caso o job tenha que fazer acesso a arquivo(s)
                if job.arquivos:
                    for arquivo in job.arquivos:
                        eventoRequisicaoArquivo = Evento('<AbrirArquivo>', self.agora + int(tamamanhoSegmento*self.memoria.T_acesso), job, recurso=arquivo)
                        self.simulador.addTask(eventoRequisicaoArquivo, 1, eventoRequisicaoArquivo.T_ocorrencia)
                    # atualiza o status do job para 'aguardando arquivo'
                    job.atualizarStatus('espera arquivos')
                # caso o job não faça acesso a arquivo, passa direto para requisição de CPU
                else:
                    eventoRequisicaoCPU = Evento('<RequisitarCPU>', self.agora + int(tamamanhoSegmento*self.memoria.T_acesso), job)
                    self.simulador.addTask(eventoRequisicaoCPU, 1, eventoRequisicaoCPU.T_ocorrencia)
                    # atualiza o status do job para 'pronto' nesse caso
                    job.atualizarStatus('pronto')

                if e.msg == 'alocado com sucesso':
                    job.segmentos_ativos.add(nome_seg)
                    print('{0:<10}<RequisitarMemoria>{1:>8}\tjob ganhou {2} bytes de memoria para o segmento \'{3}\''.format(agora, job.nome, tamamanhoSegmento, nome_seg))
                else:
                    print('{0:<10}<RequisitarMemoria>{1:>8}\tjob ja tinha estava com segmento \'{2}\' alocado'.format(agora, job.nome, nome_seg))

            # elif mensagemRetorno == 'inserido na fila da memoria':

    def LiberarMemoria(self, job, nome_seg):
        try:
            self.memoria.liberar(nome_seg)
        except Mensagem as e:
            if e.msg == 'processo desempilhado':
                job.segmentos_ativos.remove(nome_seg)
                nome, tamamanhoSegmento, job_desempilhado = e.value
                eventoRequisicaoMem = Evento('<RequisitarMemoria>', self.agora + self.memoria.T_relocacao, job_desempilhado)
                self.simulador.addTask(eventoRequisicaoMem, 1, eventoRequisicaoMem.T_ocorrencia)
                print('{0:<10}<LiberarMemoria>\tjob {1} liberou o segmento \'{2}\''.format(self.agora, job.nome, nome_seg))
            elif e.msg == 'espaco liberado':
                job.segmentos_ativos.remove(nome_seg)
                print('{0:<10}<LiberarMemoria>\tjob {1} liberou o segmento \'{2}\''.format(self.agora, job.nome, nome_seg))
            elif e.msg == 'segmento nao encontrado':
                print('{0:<10}<LiberarMemoria>\tfalta de segmento (job {1})'.format(self.agora, job.nome))
            job.atualizarStatus('pronto')
    ## ---------------- FIM MEMORIA CM ---------------- ##

    ## ---------------- ARQUIVO ---------------- ##
    def AbrirArquivo(self, job, nome_arquivo):
        try:
            self.disco.abrir(nome_arquivo, job)
        except Mensagem as e:
            if e.msg == "arquivo nao especificado":
                print("{0:<8}<AbrirArquivo>{1:13}\tjob tentou abrir arquivo '{2}' nao especificado".format(self.agora, job.nome, nome_arquivo))
                job.atualizarStatus('erro')
                eventoFinalizaJob = Evento('<FinalizarJob>', self.agora, job)
                self.simulador.addTask(eventoFinalizaJob, 1, eventoFinalizaJob.T_ocorrencia)

            elif e.msg == "inserido na fila do arquivo":
                print("{0:<8}<AbrirArquivo>{1:13}\tjob entrou na fila do arquivo {2}".format(self.agora, job.nome, nome_arquivo))

            elif e.msg == "arquivo aberto com sucesso":
                print("{0:<8}<AbrirArquivo>{1:13}\tjob abriu o arquivo '{2}' com sucesso".format(self.agora, job.nome, nome_arquivo))
                # a funcao 'abrir' do disco retorna uma referencia para o arquivo aberto (caso haja)
                arquivo_aberto = e.value
                # inserimo-lo na lista de arquivos abertos do job em questao
                job.arquivosAbertos.append(arquivo_aberto)
                # um job so prossegue sua execucao caso TODOS os recursos que pedir forem dados a ele
                # isso quer dizer que, enquanto todos os arquivos que ele quiser abrir nao o forem, ele simplesmente nao segue adiante
                if job.todosArquivosAbertos():
                    eventoRequisicaoCPU = Evento('<RequisitarCPU>', self.agora + self.gerenciador_arquivos_tempo_abertura, job)
                    self.simulador.addTask(eventoRequisicaoCPU, 1, eventoRequisicaoCPU.T_ocorrencia)

            elif e.msg == "inserido na fila dos que esperam particao livre":
                print("{0:<8}<AbrirArquivo>{1:>13}\tjob nao conseguiu abrir o arquivo '{2}'. Job inserido na fila dos que esperam por liberacao de particao.".format(self.agora, job.nome, nome_arquivo))

            elif e.msg == "acesso negado":
                print("{0:<8}<AbrirArquivo>{1:>13}\tjob nao tem permissao para acessar o arquivo {2}".format(self.agora, job.nome, nome_arquivo))
                job.atualizarStatus('erro')
                eventoFinalizaJob = Evento('<FinalizarJob>', self.agora, job)
                self.simulador.addTask(eventoFinalizaJob, 1, eventoFinalizaJob.T_ocorrencia)

            print('{0:40}Tabela de Particoes do Disco'.format(''))
            self.disco.log_tabelaParticoes()

    def AcessarArquivo(self, job, nome_arquivo):
        job.atualizarStatus('espera e/s')

        # libera CPU "na marra"
        try:
            self.CPU.libera()
        except Mensagem as e:
            if e.msg == 'job desempilhado':
                job_desempilhado, tempoEntradaFila = e.value
                job_desempilhado.tempo_espera_CPU += self.agora - tempoEntradaFila
                eventoRequisicaoCPU = Evento('<RequisitarCPU>', self.agora, job=job_desempilhado)
                self.simulador.addTask(eventoRequisicaoCPU, 1, eventoRequisicaoCPU.T_ocorrencia)

        try:
            self.disco.requisita(job, nome_arquivo)
        except Mensagem as e:
            if e.msg == 'alocado com sucesso':
                print("{0:<8}<AcessarArquivo>{1:>11}\tjob '{1}' iniciou operacao de E/S no arquivo '{3}' (tempo de CPU transcorrido = {2})".format(self.agora, job.nome, job.tempo_transcorrido, nome_arquivo))
                # agenda a liberacao do disco
                eventoLiberaDisco = Evento('<LiberarDisco>', self.agora + self.disco.T_leitura + self.disco.T_escrita, job)
                self.simulador.addTask(eventoLiberaDisco, 1, eventoLiberaDisco.T_ocorrencia)
            elif e.msg == 'disco ocupado':
                print("{0:<8}<AcessarArquivo>{1:>11}\tjob '{1}' entrou na fila de E/S do disco".format(self.agora, job.nome))
            elif e.msg == 'acesso negado':
                print("{0:<8}<AcessarArquivo>{1:>11}\tjob '{1}' teve acesso negado ao arquivo '{2}'".format(self.agora, job.nome, nome_arquivo))
                job.atualizarStatus('pronto')
                eventoRequisicaoCPU = Evento('<RequisitarCPU>', self.agora)
                self.simulador.addTask(eventoRequisicaoCPU, 1, eventoRequisicaoCPU.T_ocorrencia)

    def LiberarDisco(self, job):
        try:
            self.disco.libera()
        except Mensagem as e:
            if e.msg == 'job desempilhado':
                task, tempoEntradaFila = e.value
                job_requisitante, nome_arquivo = task
                job_requisitante.tempo_espera_Disco += self.agora - tempoEntradaFila
                eventoRequisicaoDisco = Evento('<AcessarArquivo>', self.agora, job=job_requisitante, recurso=nome_arquivo)
                self.simulador.addTask(eventoRequisicaoDisco, 1, eventoRequisicaoDisco.T_ocorrencia)
                print("{0:<8}<LiberarDisco>{1:>13}\toperacao de E/S do job '{1}' terminada. Job {2} saiu da fila".format(self.agora, job.nome, job_requisitante.nome))
            elif e.msg == 'disco livre':
                print("{0:<8}<LiberarDisco>{1:>13}\toperacao de E/S do job '{1}' terminada".format(self.agora, job.nome))

            # em ambos os casos, o job liberado entra no round robin novamente
            eventoRequisicaoCPU = Evento('<RequisitarCPU>', self.agora, job=job)
            self.simulador.addTask(eventoRequisicaoCPU, 1, eventoRequisicaoCPU.T_ocorrencia)

    ## ---------------- ESCALONAMENTO CPU ---------------- ##
    def RequisitarCPU(self, job):
        try:
            self.CPU.reserva(job, 1)
        except Mensagem as e:
            if e.msg == 'alocado com sucesso':
                job.atualizarStatus('em execucao')
                timeSlice = self.CPU.timeSlice
                if job.tempo_transcorrido + timeSlice >= job.T_MaxCPU:
                    delta = job.T_MaxCPU - job.tempo_transcorrido
                else:
                    delta = timeSlice
                print('{0:<10}<RequisitarCPU>{1:>12}\tjob ganhou  CPU por ate {2} ms'.format(self.agora, job.nome, delta))
                # tenta executar o job
                try:
                    job.run(delta)
                except Mensagem as e:
                    if e.msg == 'time slice completado':
                        if job.tempo_transcorrido >= job.T_MaxCPU:
                            eventoFinalizaJob = Evento('<FinalizarJob>', self.agora, job)
                            self.simulador.addTask(eventoFinalizaJob, 0, self.agora + delta)
                        else:
                            eventoLiberaCPU = Evento('<LiberarCPU>', self.agora + delta, job)
                            self.simulador.addTask(eventoLiberaCPU, 1, eventoLiberaCPU.T_ocorrencia)
                    elif e.msg == 'evento solicitado':
                        evento, delta = e.value
                        eventoNovo = Evento(evento.tipo, self.agora + delta, evento.job, evento.recurso)
                        self.simulador.addTask(eventoNovo, 1, eventoNovo.T_ocorrencia)

            elif e.msg == 'inserido na fila da CPU':
                print('{0:<10}<RequisitarCPU>{1:>12}\tjob inserido na fila da CPU'.format(self.agora, job.nome))

    def LiberarCPU(self, job):
        try:
            job.atualizarStatus('pronto')
            # Round Robin
            if job not in self.CPU.fila:
                self.CPU.fila.push(job, 1, self.agora)
            self.CPU.libera()
        except Mensagem as e:
            print('{0:<10}<LiberarCPU>{1:>15}\tjob liberou CPU (tempo transcorrido = {2} ms)'.format(self.agora, job.nome, job.tempo_transcorrido))
            if e.msg == 'job desempilhado':
                job_desempilhado, tempoEntradaFila = e.value
                job_desempilhado.tempo_espera_CPU += self.agora - tempoEntradaFila
                eventoRequisicaoCPU = Evento('<RequisitarCPU>', self.agora, job=job_desempilhado)
            # elif e.msg == 'CPU livre':
            #     eventoRequisicaoCPU = Evento('<RequisitarCPU>', self.agora, job=job)

            self.simulador.addTask(eventoRequisicaoCPU, 1, eventoRequisicaoCPU.T_ocorrencia)
    ## ---------------- FIM ESCALONAMENTO CPU ---------------- ##

    ## ---------------- IMPRESSORA ---------------- ##
    def Imprimir(self, job, impressora):
        impressora = self.impressorasID[impressora]
        job.atualizarStatus('espera e/s')

        # libera CPU "na marra"
        try:
            self.CPU.libera()
        except Mensagem as e:
            if e.msg == 'job desempilhado':
                job_desempilhado, tempoEntradaFila = e.value
                job_desempilhado.tempo_espera_CPU += self.agora - tempoEntradaFila
                eventoRequisicaoCPU = Evento('<RequisitarCPU>', self.agora, job=job_desempilhado)
                self.simulador.addTask(eventoRequisicaoCPU, 1, eventoRequisicaoCPU.T_ocorrencia)

        try:
            impressora.requisita(job)
        except Mensagem as e:
            if e.msg == 'alocado com sucesso':
                eventoLiberarImpressora = Evento('<LiberarImpressora>', self.agora + impressora.T_impressao, job, impressora)
                self.simulador.addTask(eventoLiberarImpressora, 1, eventoLiberarImpressora.T_ocorrencia)
                print("{0:<8}<Imprimir>{1:>17}\tjob '{1}' iniciou impressao na impressora {2} (tempo de CPU transcorrido = {3})".format(self.agora, job.nome, impressora.label, job.tempo_transcorrido))
            elif e.msg == 'impressora ocupada':
                print("{0:<8}<Imprimir>{1:>17}\tjob '{1}' entrou na fila de impressao (tempo de CPU transcorrido = {2})".format(self.agora, job.nome, job.tempo_transcorrido))

    def LiberarImpressora(self, job, impressora):
        try:
            impressora.libera()
        except Mensagem as e:
            if e.msg == 'job desempilhado':
                job_desempilhado, tempoEntradaFila = e.value
                job_desempilhado.tempo_espera_Impressoras += self.agora - tempoEntradaFila
                eventoRequisicaoImpressao('<Imprimir>', self.agora, job=job_desempilhado, recurso=impressora.label)
                self.simulador.addTask(eventoRequisicaoImpressao, 1, eventoRequisicaoImpressao.T_ocorrencia)
                print('{0:<10}<LiberarImpressora>{3:>8}\timpressora {1} terminou execucao. Job {2} saiu da fila'.format(self.agora, impressora.label, e.value.nome, job.nome))
            elif e.msg == 'impressora livre':
                print('{0:<10}<LiberarImpressora>{2:>8}\timpressora {1} terminou execucao'.format(self.agora, impressora.label, job.nome))

            # em ambos os casos, o job liberado entra no round robin novamente
            eventoRequisicaoCPU = Evento('<RequisitarCPU>', self.agora, job=job)
            self.simulador.addTask(eventoRequisicaoCPU, 1, eventoRequisicaoCPU.T_ocorrencia)

    ## ---------------- FIM IMPRESSORA ---------------- ##

    ## ---------------- LEITORA ---------------- ##
    def Leitura(self, job, leitora):
        leitora = self.leitorasID[leitora]
        job.atualizarStatus('espera e/s')

        # libera CPU "na marra"
        try:
            self.CPU.libera()
        except Mensagem as e:
            if e.msg == 'job desempilhado':
                job_desempilhado, tempoEntradaFila = e.value
                job_desempilhado.tempo_espera_CPU += self.agora - tempoEntradaFila
                eventoRequisicaoCPU = Evento('<RequisitarCPU>', self.agora, job=job_desempilhado)
                self.simulador.addTask(eventoRequisicaoCPU, 1, eventoRequisicaoCPU.T_ocorrencia)

        try:
            leitora.requisita(job)
        except Mensagem as e:
            if e.msg == 'alocado com sucesso':
                eventoLiberarLeitora = Evento('<LiberarLeitora>', self.agora + leitora.T_leitura, job, leitora)
                self.simulador.addTask(eventoLiberarLeitora, 1, eventoLiberarLeitora.T_ocorrencia)
                print('{0:<10}<Leitura>{1:>18}\tiniciou leitura na leitora {2} (tempo de CPU transcorrido = {3})'.format(self.agora, job.nome, leitora.label, job.tempo_transcorrido))
            elif e.msg == 'leitora ocupada':
                print('{0:<10}<Leitura>{1:>18}\tentrou na fila de leitura (tempo de CPU transcorrido = {2})'.format(self.agora, job.nome, job.tempo_transcorrido))

    def LiberarLeitora(self, job, leitora):
        try:
            leitora.libera()
        except Mensagem as e:
            if e.msg == 'job desempilhado':
                job_desempilhado, tempoEntradaFila = e.value
                job_desempilhado.tempo_espera_Leitoras += self.agora - tempoEntradaFila
                eventoRequisicaoLeitora('<Leitura>', self.agora, job=job_desempilhado, recurso=leitora.label)
                self.simulador.addTask(eventoRequisicaoLeitora, 1, eventoRequisicaoLeitora.T_ocorrencia)
                print('{0:<10}<LiberarLeitora>{1:>11}\tleitora {2} terminou execucao. Job {3} saiu da fila'.format(self.agora, job.nome, leitora.label, job_desempilhado.nome))
            elif e.msg == 'leitora livre':
                print('{0:<10}<LiberarLeitora>{1:>11}\tleitora {2} terminou execucao'.format(self.agora, job.nome, leitora.label))

            # em ambos os casos, o job liberado entra no round robin novamente
            eventoRequisicaoCPU = Evento('<RequisitarCPU>', self.agora, job=job)
            self.simulador.addTask(eventoRequisicaoCPU, 1, eventoRequisicaoCPU.T_ocorrencia)

    ## ---------------- FIM LEITORA ---------------- ##
    #### FIM Rotinas de tratamento de INTERRUPCOES ####

    ## Demais rotinas
    def setSimulador(self, simulador):
        if isinstance(simulador, Simulador):
            self.simulador = simulador
            self.simulador._agora = self.T_acionamento_clk
            self.simulador.addTask(Evento('<EncerrarSimulacao>', self.T_final), 1, self.T_final)
        else:
            self.simulador = None

    def sincRelogio(self, tempoAtual):
        self.agora = tempoAtual
        self.CPU.agora = tempoAtual
        self.memoria.agora = tempoAtual
        self.disco.agora = tempoAtual
        # impressoras
        self.impressora1.agora = tempoAtual
        self.impressora2.agora = tempoAtual
        # leitoras
        self.leitora1.agora = tempoAtual
        self.leitora2.agora = tempoAtual

    def fim(self, task):
        if task.tipo == '<EncerrarSimulacao>':
            return True
        return False
