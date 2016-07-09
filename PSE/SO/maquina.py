from PSE.Base import MaquinaBase, Simulador, ListaPrioritaria
from PSE.SO import CPU, Disco, Evento, Impressora, Job, Leitora, Memoria, Mensagem, Segmento

class Maquina(MaquinaBase):
    """docstring for Maquina"""
    def __init__(self, T_acionamento_clk, T_final, jobs, T_relocacao_mem, tamanho_mem):
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

        ## dispositivos que a maquina deve conter
        # self.cpu = cpu.CPU()
        # self.disco = disco.Disco()
        self.memoria = Memoria(T_relocacao_mem, tamanho_mem)
        # self.impressora1 = impressora.Impressora()
        # self.impressora2 = impressora.Impressora()
        # self.leitora1 = leitora.Leitora()
        # self.leitora2 = leitora.Leitora()

        # Filas de recursos
        # self.cm_q = lista.ListaPrioritaria()
        # self.cpu_q = lista.ListaPrioritaria()
        # self.disk_q = lista.ListaPrioritaria()

        # Job table
        self.jobs_inativos = {
            job.nome: job for job in jobs
        }
        self.job_table = list()
        self.job_atual_ptr = 0

    def trataEvento(self, evento):
        if evento.tipo() == '<Iniciar>':
            # pega o job que foi carregado durante o carregamento do arquivo de jobs
            job = self.jobs_inativos[evento.nome_job]
            # e chama a rotina de inicialização
            self.Iniciar(job)

        elif evento.tipo() == '<RequisitarMemoria>':
            self.RequisitarMemoria()

        elif evento.tipo() == '<RequisitarCPU>':
            pass

        elif evento.tipo() == '<AcessarArquivo>':
            pass

        elif evento.tipo() == '<Event5>':
            pass

        elif evento.tipo() == '<LiberarMemoria>':
            pass

        elif evento.tipo() == '<FinilizarJob>':
            pass


    # rotinas de tratamento de interrupcoes

    def Iniciar(self, novo_job):
        # insere o job na tabela de jobs ativos
        self.job_table[novo_job.nome] = novo_job
        # agenda uma requisição de memória
        eventoRequisicaoMem = Evento('<RequisitarMemoria>', novo_job.tChegada, novo_job)
        self.simulador.addTask(eventoRequisicaoMem, 1, eventoRequisicaoMem.t_ocorrencia)


    def RequisitarMemoria(self, job):
        try:
            self.memoria.requisitar(job)
        except Mensagem as mensagemRetorno:
            if mensagemRetorno == 'alocado':
                eventoRequisicaoCPU = Evento('<RequisitarCPU>', self.simulador._agora + self.memoria.T_relocacao, job)
                self.simulador.addTask(eventoRequisicaoCPU, 1, eventoRequisicaoCPU.t_ocorrencia)
            # elif mensagemRetorno == 'enfileirado':

    def RequisitarCPU(self):
        pass

    def AcessarArquivo(self):
        pass

    def Event5(self):
        pass

    def LiberarMemoria(self):
        pass

    def FinilizarJob(self):
        pass


    # dicionario de eventos
    Eventos = {
        '<Iniciar>': Iniciar,
        '<RequisitarMemoria>': RequisitarMemoria,
        '<RequisitarCPU>': RequisitarCPU,
        '<AcessarArquivo>': AcessarArquivo,
        '<Event5>': Event5,
        '<LiberarMemoria>': LiberarMemoria,
        '<FinilizarJob>': FinilizarJob,
    }

    def addSimulador(self, simulador):
        if isinstance(simulador, Simulador):
            self.simulador = simulador
        else:
            self.simulador = None
