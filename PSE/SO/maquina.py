from PSE.Base import MaquinaBase, Simulador, ListaPrioritaria
from PSE.SO import CPU, Disco, Evento, Impressora, Job, Leitora, Memoria, Mensagem, Segmento

class Maquina(MaquinaBase):
    """docstring for Maquina"""
    def __init__(self, T_acionamento_clk, T_final, time_slice_size, max_processos, disco_tempo_leitura, disco_tempo_escrita, disco_tamanho, memoria_tempo_relocacao, memoria_tempo_transferencia, memoria_tamanho, impressora_tempo_impressao, leitora_tempo_leitura):#, jobs):
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

        ## dispositivos que a maquina deve conter
        self.CPU = CPU(time_slice_size)
        self.memoria = Memoria(memoria_tempo_relocacao, memoria_tempo_transferencia, memoria_tamanho)
        self.disco = Disco(disco_tempo_leitura, disco_tempo_escrita, disco_tamanho)
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

        ## tabela com todos os jobs a serem simulados
        # self.jobs_inativos = {
        #     job.nome: job for job in jobs
        # }
        # for job in jobs:
        #     eventoChegadaJob = Evento('<Iniciar>', job.T_chegada, job)
        ## Job table
        self.job_table = list()

    def trataEvento(self, evento):
        if self.simulador._agora <= self.T_final:
            if evento.tipo == '<Iniciar>':
                # pega o job que foi carregado durante o carregamento do arquivo de jobs
                # e chama a rotina de inicialização
                self.Iniciar(evento.job)

            elif evento.tipo == '<RequisitarMemoria>':
                job = evento.job
                nome, tamamanhoSegmento = job.prox_segmento()
                self.RequisitarMemoria(nome, tamamanhoSegmento, job, evento.T_ocorrencia)

            elif evento.tipo == '<RequisitarCPU>':
                self.RequisitarCPU(evento.job)

            # elif evento.tipo == '<AcessarArquivo>':
            #     self.AcessarArquivo(evento.job)

            elif evento.tipo == '<Imprimir>':
                self.Imprimir(evento.job, evento.recurso)

            elif evento.tipo == '<LiberarImpressora>':
                self.LiberarImpressora(job=evento.job, impressora=evento.recurso)

            elif evento.tipo == '<LiberarCPU>':
                self.LiberarCPU(evento.job)

            elif evento.tipo == '<LiberarMemoria>':
                self.LiberarMemoria(evento.job)

            elif evento.tipo == '<FinalizarJob>':
                self.FinalizarJob(evento.job)

            elif evento.tipo == '<EncerrarSimulacao>':
                self.EncerrarSimulacao()


    # Rotinas de tratamento de interrupcoes

    ## ---------------- ROTINAS DO JOB --------------- ##
    def Iniciar(self, novo_job):
        novo_job.atualizar_status('chegou')
        # insere o job na tabela de jobs ativos
        self.job_table.append(novo_job)
        # agenda uma requisição de memória
        eventoRequisicaoMem = Evento('<RequisitarMemoria>', novo_job.T_chegada, novo_job)
        self.simulador.addTask(eventoRequisicaoMem, 1, novo_job.T_chegada)
        novo_job.atualizar_status('aguardando memoria')
        print('{0}\t<Iniciar>:\n\tjob {1} inserido na tabela\n'.format(self.simulador._agora, novo_job.nome))

    def FinalizarJob(self, job):
        print('fila:', self.CPU.fila)
        # libera a CPU
        try:
            self.CPU.libera()
        except Mensagem as e:
            job.atualizar_status('completo')
            print('{0}\t<FinalizarJob>:\n\tjob {1} concluiu-se\n'.format(self.simulador._agora, job.nome))
            if e.msg == 'job desempilhado':
                print('\tjob {0} foi desempilhado da fila da CPU\n'.format(job.nome))
                eventoRequisicaoCPU = Evento('<RequisitarCPU>', self.simulador._agora, job=e.value)
                self.simulador.addTask(eventoRequisicaoCPU, 1, eventoRequisicaoCPU.T_ocorrencia)

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
                    eventoRequisicaoMem = Evento('<RequisitarMemoria>', self.simulador._agora + self.memoria.T_relocacao, job_desempilhado)
                    print('\tjob {1} liberou o segmento \'{2}\'\n'.format(self.simulador._agora, job.nome, seg))
                    self.simulador.addTask(eventoRequisicaoMem, 1, eventoRequisicaoMem.T_ocorrencia)
                elif e.msg == 'espaco liberado':
                    print('\tjob {1} liberou o segmento \'{2}\'\n'.format(self.simulador._agora, job.nome, seg))
                elif e.msg == 'segmento nao encontrado':
                    print('\tfalta de segmento {2} (job {1})\n'.format(self.simulador._agora, job.nome, e.value))
                job.atualizar_status('pronto')

    def EncerrarSimulacao(self):
        print('{0}\t<EncerrarSimulacao>:\n\tSimulacao acabou-se\n'.format(self.simulador._agora))
    ## ---------------- FIM ROTINAS DO JOB --------------- ##

    ## ---------------- MEMORIA CM ---------------- ##
    def RequisitarMemoria(self, nome_seg, tamamanhoSegmento, job, T_ocorrencia):
        agora = self.simulador._agora
        try:
            self.memoria.requisitar(nome_seg, tamamanhoSegmento, job, agora)
        except Mensagem as e:
            if e.msg == 'alocado com sucesso':
                job.segmentos_ativos.add(nome_seg)
                eventoRequisicaoCPU = Evento('<RequisitarCPU>', T_ocorrencia + self.memoria.T_relocacao, job)
                self.simulador.addTask(eventoRequisicaoCPU, 1, eventoRequisicaoCPU.T_ocorrencia)
                job.atualizar_status('pronto')
                print('{0}\t<RequisitarMemoria>:\n\tjob {1} ganhou {2} bytes de memoria para o segmento \'{3}\'\n'.format(agora, job.nome, tamamanhoSegmento, nome_seg))
            if e.msg == 'segmento ja alocado':
                eventoRequisicaoCPU = Evento('<RequisitarCPU>', T_ocorrencia + self.memoria.T_relocacao, job)
                self.simulador.addTask(eventoRequisicaoCPU, 1, eventoRequisicaoCPU.T_ocorrencia)
                job.atualizar_status('pronto')
                print('{0}\t<RequisitarMemoria>:\n\tjob {1} ja tinha estava com segmento \'{2}\' alocado\n'.format(agora, job.nome, nome_seg))
            # elif mensagemRetorno == 'inserido na fila da memoria':

    def LiberarMemoria(self, job, nome_seg):
        try:
            self.memoria.liberar(nome_seg)
        except Mensagem as e:
            if e.msg == 'processo desempilhado':
                job.segmentos_ativos.remove(nome_seg)
                nome, tamamanhoSegmento, job_desempilhado = e.value
                eventoRequisicaoMem = Evento('<RequisitarMemoria>', self.simulador._agora + self.memoria.T_relocacao, job_desempilhado)
                self.simulador.addTask(eventoRequisicaoMem, 1, eventoRequisicaoMem.T_ocorrencia)
                print('{0}\t<LiberarMemoria>:\n\tjob {1} liberou o segmento \'{2}\'\n'.format(self.simulador._agora, job.nome, nome_seg))
            elif e.msg == 'espaco liberado':
                job.segmentos_ativos.remove(nome_seg)
                print('{0}\t<LiberarMemoria>:\n\tjob {1} liberou o segmento \'{2}\'\n'.format(self.simulador._agora, job.nome, nome_seg))
            elif e.msg == 'segmento nao encontrado':
                print('{0}\t<LiberarMemoria>:\n\tfalta de segmento (job {1})\n'.format(self.simulador._agora, job.nome))
            job.atualizar_status('pronto')
    ## ---------------- FIM MEMORIA CM ---------------- ##

    ## ---------------- ARQUIVO ---------------- ##
    def AcessarArquivo(self, job):
        pass

    ## ---------------- ESCALONAMENTO CPU ---------------- ##
    def RequisitarCPU(self, job):
        print('fila:', self.CPU.fila)
        agora = self.simulador._agora
        try:
            self.CPU.reserva(job, 1)
        except Mensagem as e:
            if e.msg == 'alocado com sucesso':
                job.atualizar_status('em execucao')
                timeSlice = self.CPU.timeSlice
                if job.tempo_transcorrido + timeSlice >= job.T_MaxCPU:
                    delta = job.T_MaxCPU - job.tempo_transcorrido
                else:
                    delta = timeSlice
                print('{0}\t<RequisitarCPU>:\n\tjob {1} ganhou CPU por ate {2} u.t.\n'.format(agora, job.nome, delta))
                # tenta executar o job
                try:
                    job.run(delta)
                except Mensagem as e:
                    if e.msg == 'time slice completado':
                        if job.tempo_transcorrido >= job.T_MaxCPU:
                            eventoFinalizaJob = Evento('<FinalizarJob>', agora, job)
                            self.simulador.addTask(eventoFinalizaJob, 0, agora+delta)
                        else:
                            eventoLiberaCPU = Evento('<LiberarCPU>', agora+delta, job)
                            self.simulador.addTask(eventoLiberaCPU, 1, eventoLiberaCPU.T_ocorrencia)
                    elif e.msg == 'evento solicitado':
                        evento, delta = e.value
                        eventoNovo = Evento(evento.tipo, agora+delta, job, evento.recurso)
                        self.simulador.addTask(eventoNovo, 1, eventoNovo.T_ocorrencia)

            elif e.msg == 'inserido na fila da CPU':
                print('{0}\t<RequisitarCPU>:\n\tjob {1} inserido na fila da CPU\n'.format(agora, job.nome))

    def LiberarCPU(self, job):
        print('fila:', self.CPU.fila)
        try:
            job_antigo = self.CPU.job_em_execucao
            # Round Robin
            if job_antigo not in self.CPU.fila:
                self.CPU.fila.insert(0, job_antigo)
            self.CPU.libera()
        except Mensagem as e:
            job.atualizar_status('pronto')
            print('{0}\t<LiberarCPU>:\n\tjob {1} liberou CPU\n'.format(self.simulador._agora, job.nome))
            if e.msg == 'job desempilhado':
                eventoRequisicaoCPU = Evento('<RequisitarCPU>', self.simulador._agora, job=e.value)
            elif e.msg == 'CPU livre':
                eventoRequisicaoCPU = Evento('<RequisitarCPU>', self.simulador._agora, job=job_antigo)

            self.simulador.addTask(eventoRequisicaoCPU, 1, eventoRequisicaoCPU.T_ocorrencia)
    ## ---------------- FIM ESCALONAMENTO CPU ---------------- ##

    ## ---------------- IMPRESSORA ---------------- ##
    def Imprimir(self, job, impressora):
        agora = self.simulador._agora
        impressora = self.impressorasID[impressora]
        job.atualizar_status('espera e/s')

        # tenta liberar CPU "na marra"
        try:
            self.CPU.libera()
        except Mensagem as e:
            if e.msg == 'job desempilhado':
                eventoRequisicaoCPU = Evento('<RequisitarCPU>', self.simulador._agora, job=e.value)
                self.simulador.addTask(eventoRequisicaoCPU, 1, eventoRequisicaoCPU.T_ocorrencia)

        try:
            impressora.requisita(job)
        except Mensagem as e:
            if e.msg == 'alocado com sucesso':
                eventoLiberarImpressora = Evento('<LiberarImpressora>', agora + impressora.T_impressao, job, impressora)
                self.simulador.addTask(eventoLiberarImpressora, 1, eventoLiberarImpressora.T_ocorrencia)
                print('{0}\t<Imprimir>:\n\tjob {1} iniciou impressao na impressora {2}\n'.format(self.simulador._agora, job.nome, impressora.label))
            elif e.msg == 'impressora ocupada':
                print('{0}\t<Imprimir>:\n\tjob {1} entrou na fila de impressao\n'.format(self.simulador._agora, job.nome))

    def LiberarImpressora(self, job, impressora):
        try:
            impressora.libera()
        except Mensagem as e:
            if e.msg == 'job desempilhado':
                eventoRequisicaoImpressao('<Imprimir>', self.simulador._agora, job=e.value)
                self.simulador.addTask(eventoRequisicaoImpressao, 1, eventoRequisicaoImpressao.T_ocorrencia)
                print('{0}\t<LiberarImpressora>:\n\tImpressora {1} terminou execucao. Job {2} saiu da fila\n'.format(self.simulador._agora, impressora.label, e.value.nome))
            elif e.msg == 'impressora livre':
                print('{0}\t<LiberarImpressora>:\n\tImpressora {1} terminou execucao\n'.format(self.simulador._agora, impressora.label))

            # em ambos os casos, o job liberado entra no round robin novamente
            eventoRequisicaoCPU = Evento('<RequisitarCPU>', self.simulador._agora, job=job)
            self.simulador.addTask(eventoRequisicaoCPU, 1, eventoRequisicaoCPU.T_ocorrencia)
            if job not in self.CPU.fila:
                self.CPU.fila.insert(0, job)
    ## ---------------- FIM IMPRESSORA ---------------- ##

    ## ---------------- LEITORA ---------------- ##
    def Leitura(self, job, leitora):
        agora = self.simulador._agora
        leitora = self.leitorasID[leitora]
        job.atualizar_status('espera e/s')

        # libera CPU "na marra"
        try:
            self.CPU.libera()
        except Mensagem as e:
            if e.msg == 'job desempilhado':
                eventoRequisicaoCPU = Evento('<RequisitarCPU>', self.simulador._agora, job=e.value)
                self.simulador.addTask(eventoRequisicaoCPU, 1, eventoRequisicaoCPU.T_ocorrencia)

        try:
            leitora.requisita(job)
        except Mensagem as e:
            if e.msg == 'alocado com sucesso':
                eventoLiberarLeitora = Evento('<LiberarLeitora>', agora + leitora.T_leitura, job, leitora)
                self.simulador.addTask(eventoLiberarLeitora, 1, eventoLiberarLeitora.T_ocorrencia)
                print('{0}\t<Leitura>:\n\tjob {1} iniciou leitura na leitora {2}\n'.format(self.simulador._agora, job.nome, leitora.label))
            elif e.msg == 'leitora ocupada':
                print('{0}\t<Leitura>:\n\tjob {1} entrou na fila de leitura\n'.format(self.simulador._agora, job.nome))

    def LiberarLeitora(self, job, impressora):
        try:
            impressora.libera()
        except Mensagem as e:
            if e.msg == 'job desempilhado':
                eventoRequisicaoImpressao('<Imprimir>', self.simulador._agora, job=e.value)
                self.simulador.addTask(eventoRequisicaoImpressao, 1, eventoRequisicaoImpressao.T_ocorrencia)
                print('{0}\t<LiberarImpressora>:\n\tImpressora {1} terminou execucao. Job {2} saiu da fila\n'.format(self.simulador._agora, impressora.label, e.value.nome))
            elif e.msg == 'leitora livre':
                print('{0}\t<LiberarImpressora>:\n\tImpressora {1} terminou execucao\n'.format(self.simulador._agora, impressora.label))

            # em ambos os casos, o job liberado entra no round robin novamente
            eventoRequisicaoCPU = Evento('<RequisitarCPU>', self.simulador._agora, job=job)
            self.simulador.addTask(eventoRequisicaoCPU, 1, eventoRequisicaoCPU.T_ocorrencia)
            if job not in self.CPU.fila:
                self.CPU.fila.insert(0, job)
    ## ---------------- FIM LEITORA ---------------- ##

    ## Demais rotinas
    def setSimulator(self, simulador):
        if isinstance(simulador, Simulador):
            self.simulador = simulador
            self.simulador._agora = self.T_acionamento_clk
            self.simulador.addTask(Evento('<EncerrarSimulacao>', self.T_final), 1, self.T_final)
        else:
            self.simulador = None

    def fim(self, task):
        if task.tipo == '<EncerrarSimulacao>':
            return True
        return False
