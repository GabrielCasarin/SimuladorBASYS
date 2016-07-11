from PSE.Base import MaquinaBase, Simulador, ListaPrioritaria
from PSE.SO import CPU, Disco, Evento, Impressora, Job, Leitora, Memoria, Mensagem, Segmento

class Maquina(MaquinaBase):
    """docstring for Maquina"""
    def __init__(self, T_acionamento_clk, T_final, time_slice_size, max_processos, disco_tempo_leitura, disco_tempo_escrita, disco_tamanho, memoria_tempo_relocacao, memoria_tempo_transferencia, memoria_tamanho):#, jobs):
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
        self.disco = Disco(disco_tempo_leitura, disco_tempo_escrita, disco_tamanho)
        self.memoria = Memoria(memoria_tempo_relocacao, memoria_tempo_transferencia, memoria_tamanho)
        # self.impressora1 = Impressora()
        # self.impressora2 = Impressora()
        # self.leitora1 = Leitora()
        # self.leitora2 = Leitora()

        ## tabela com todos os jobs a serem simulados
        # self.jobs_inativos = {
        #     job.nome: job for job in jobs
        # }
        # for job in jobs:
        #     eventoChegadaJob = Evento('<Iniciar>', job.T_chegada, job)
        ## Job table
        self.job_table = list()
        # self.job_atual_ptr = 0

    def trataEvento(self, evento):
        if evento.tipo == '<Iniciar>':
            # pega o job que foi carregado durante o carregamento do arquivo de jobs
            # e chama a rotina de inicialização
            self.Iniciar(evento.job)

        elif evento.tipo == '<RequisitarMemoria>':
            job = evento.job
            nome, tamamanhoSegmento = job.prox_segmento()
            self.RequisitarMemoria(nome, tamamanhoSegmento, job)

        elif evento.tipo == '<RequisitarCPU>':
            self.RequisitarCPU(evento.job)

        elif evento.tipo == '<AcessarArquivo>':
            self.AcessarArquivo(evento.job)

        elif evento.tipo == '<LiberarCPU>':
            self.LiberarCPU(evento.job)

        elif evento.tipo == '<LiberarMemoria>':
            self.LiberarMemoria(evento.job)

        elif evento.tipo == '<FinilizarJob>':
            self.FinilizarJob(evento.job)


    # rotinas de tratamento de interrupcoes

    def Iniciar(self, novo_job):
        novo_job.atualizar_status('chegou')
        # insere o job na tabela de jobs ativos
        self.job_table.append(novo_job)
        # agenda uma requisição de memória
        eventoRequisicaoMem = Evento('<RequisitarMemoria>', novo_job.T_chegada, novo_job)
        self.simulador.addTask(eventoRequisicaoMem, 1, novo_job.T_chegada)
        novo_job.atualizar_status('aguardando memoria')
        print('\n{0}\t<Iniciar>: job {1} inserido na tabela\n'.format(self.simulador._agora, novo_job.nome))


    def RequisitarMemoria(self, nome_seg, tamamanhoSegmento, job):
        agora = self.simulador._agora
        try:
            self.memoria.requisitar(nome_seg, tamamanhoSegmento, job, agora)
        except Mensagem as e:
            if e.msg == 'alocado com sucesso':
                job.segmentos_ativos.add(nome_seg)
                eventoRequisicaoCPU = Evento('<RequisitarCPU>', agora + self.memoria.T_relocacao, job)
                self.simulador.addTask(eventoRequisicaoCPU, 1, eventoRequisicaoCPU.T_ocorrencia)
                job.atualizar_status('pronto')
                print('{0}\t<RequisitarMemoria>: job {1} ganhou {2} bytes de memoria para o segmento \'{3}\''.format(agora, job.nome, tamamanhoSegmento, nome_seg))
            if e.msg == 'segmento ja alocado':
                eventoRequisicaoCPU = Evento('<RequisitarCPU>', agora + self.memoria.T_relocacao, job)
                self.simulador.addTask(eventoRequisicaoCPU, 1, eventoRequisicaoCPU.T_ocorrencia)
                job.atualizar_status('pronto')
                print('{0}\t<RequisitarMemoria>: job {1} ja tinha estava com segmento \'{2}\' alocado'.format(agora, job.nome, nome_seg))
            # elif mensagemRetorno == 'inserido na fila da memoria':

    def RequisitarCPU(self, job):
        agora = self.simulador._agora
        try:
            self.CPU.reserva(job, 1, agora)
        except Mensagem as e:
            if e.msg == 'alocado com sucesso':
                job.atualizar_status('em execucao')
                timeSlice = self.CPU.timeSlice
                if job.tempo_transcorrido + timeSlice > job.T_MaxCPU:
                    delta = T_MaxCPU - job.tempo_transcorrido
                else:
                    delta = timeSlice
                print('{0}\t<RequisitarCPU>: job {1} ganhou CPU por ate {2} u.t.'.format(agora, job.nome, delta))
                # tenta executar o job
                try:
                    job.run(delta)
                except Mensagem as e:
                    if e.msg == 'time slice completado':
                        if job.tempo_transcorrido >= job.T_MaxCPU:
                            eventoFinalizaJob = Evento('<FinilizarJob>', agora, job)
                            self.simulador.addTask(eventoFinalizaJob, 0, agora)
                        else:
                            eventoLiberaCPU = Evento('<LiberarCPU>', agora+delta, job)
                            self.simulador.addTask(eventoLiberaCPU, 1, eventoLiberaCPU.T_ocorrencia)

    def AcessarArquivo(self, job):
        pass

    def LiberarCPU(self, job):
        try:
            self.CPU.libera()
        except Mensagem as e:
            if e.msg == 'job desempilhado':
                pass
            # elif e == 'CPU livre':
            #     pass

    def LiberarMemoria(self, job, nome_seg):
        try:
            self.memoria.liberar(nome_seg)

        except Mensagem as e:
            if e.msg == 'processo desempilhado':
                job.segmentos_ativos.remove(nome_seg)
                nome, tamamanhoSegmento, job_desempilhado = e.value
                eventoRequisicaoMem = Evento('<RequisitarMemoria>', self.simulador._agora + self.memoria.T_relocacao, job_desempilhado)
                self.simulador.addTask(eventoRequisicaoMem, 1, eventoRequisicaoMem.T_ocorrencia)
                print('{0}\t<LiberarMemoria>: job {1} liberou o segmento \'{2}\''.format(self.simulador._agora, job.nome, nome_seg))
            elif e.msg == 'espaco liberado':
                job.segmentos_ativos.remove(nome_seg)
                print('{0}\t<LiberarMemoria>: job {1} liberou o segmento \'{2}\''.format(self.simulador._agora, job.nome, nome_seg))
            elif e.msg == 'segmento nao encontrado':
                print('{0}\t<LiberarMemoria>: falta de segmento (job {1})'.format(self.simulador._agora, job.nome))
            job.atualizar_status('pronto')

    def FinilizarJob(self, job):
        job.atualizar_status('completo')


    def addSimulador(self, simulador):
        if isinstance(simulador, Simulador):
            self.simulador = simulador
            self.simulador._agora = self.T_acionamento_clk
        else:
            self.simulador = None
