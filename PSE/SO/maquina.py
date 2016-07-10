from PSE.Base import MaquinaBase, Simulador, ListaPrioritaria
from PSE.SO import CPU, Disco, Evento, Impressora, Job, Leitora, Memoria, Mensagem, Segmento

class Maquina(MaquinaBase):
    """docstring for Maquina"""
    def __init__(self, T_acionamento_clk, T_final, jobs, time_slice_size, max_processos, disco_tempo_leitura, disco_tempo_escrita, disco_tamanho, memoria_tempo_relocacao, memoria_tempo_transferencia, memoria_tamanho):
        super(Maquina, self).__init__()

        self.simulador = None

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
        self.cpu = CPU(time_slice_size)
        self.disco = disco.Disco(disco_tempo_leitura, disco_tempo_escrita, disco_tamanho)
        self.memoria = Memoria(memoria_tempo_relocacao, memoria_tempo_transferencia, memoria_tamanho)
        # self.impressora1 = impressora.Impressora()
        # self.impressora2 = impressora.Impressora()
        # self.leitora1 = leitora.Leitora()
        # self.leitora2 = leitora.Leitora()

        ## tabela com todos os jobs a serem simulados
        self.jobs_inativos = {
            job.nome: job for job in jobs
        }
        ## Job table
        self.job_table = list()
        # self.job_atual_ptr = 0

    def trataEvento(self, evento):
        if evento.tipo() == '<Iniciar>':
            # pega o job que foi carregado durante o carregamento do arquivo de jobs
            job = self.jobs_inativos[evento.nome_job]
            # e chama a rotina de inicialização
            self.Iniciar(job)

        elif evento.tipo() == '<RequisitarMemoria>':
            self.RequisitarMemoria()

        elif evento.tipo() == '<RequisitarCPU>':
            self.RequisitarCPU()

        # elif evento.tipo() == '<AcessarArquivo>':
        #     self.AcessarArquivo()

        elif evento.tipo() == '<LiberarCPU>':
            self.LiberarCPU()

        elif evento.tipo() == '<LiberarMemoria>':
            self.LiberarMemoria()

        elif evento.tipo() == '<FinilizarJob>':
            self.FinilizarJob()


    # rotinas de tratamento de interrupcoes

    def Iniciar(self, novo_job):
        # insere o job na tabela de jobs ativos
        self.job_table[novo_job.nome] = novo_job
        # agenda uma requisição de memória
        eventoRequisicaoMem = Evento('<RequisitarMemoria>', novo_job.tChegada, novo_job)
        self.simulador.addTask(eventoRequisicaoMem, 1, eventoRequisicaoMem.t_ocorrencia)


    def RequisitarMemoria(self, job):
        agora = self.simulador._agora
        try:
            self.memoria.requisitar(nome, tamamanhoSegmento, job, agora)
        except Mensagem as e:
            if e == 'alocado com sucesso' or \
                e == 'segmento ja alocado':
                    eventoRequisicaoCPU = Evento('<RequisitarCPU>', agora + self.memoria.T_relocacao, job)
                    self.simulador.addTask(eventoRequisicaoCPU, 1, eventoRequisicaoCPU.t_ocorrencia)
            # elif mensagemRetorno == 'inserido na fila da memoria':

    def RequisitarCPU(self, job):
        try:
            self.CPU.reserva(job)
        except Mensagem as e:
            if e == 'alocado com sucesso':
                timeSlice = self.CPU.timeSlice
                if job.tempo_transcorrido + timeSlice > job.T_MaxCPU:
                    job.sinc(job.T_MaxCPU - job.tempo_transcorrido)
                else:
                    job.sinc(timeSlice)

                job.run()
                #TODO: inserir desaloca

    # def AcessarArquivo(self, job):
    #     pass

    def LiberarCPU(self, job):
        try:
            self.CPU.libera()
        except Mensagem as e:
            if e == 'job desempilhado':
                pass
            # elif e == 'CPU livre':
            #     pass

    def LiberarMemoria(self, job):
        try:

            self.memoria.liberar(nome)

        except Mensagem as e:

            if e == 'processo desempilhado':
                nome, tamamanhoSegmento, job = e.value


    def FinilizarJob(self, job):
        pass


    def addSimulador(self, simulador):
        if isinstance(simulador, Simulador):
            self.simulador = simulador
        else:
            self.simulador = None
