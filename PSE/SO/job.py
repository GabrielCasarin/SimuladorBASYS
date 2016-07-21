import random
from PSE.SO import Mensagem, Evento

class Job(object):
    """docstring for Job"""
    def __init__(self, nome, T_chegada, T_MaxCPU, segmentos, DiscoCount, LeitoraCount, ImpressoraCount):
        super(Job, self).__init__()

        self.nome = nome
        self.T_chegada = T_chegada
        self.T_MaxCPU = T_MaxCPU
        self.tempo_restante = T_MaxCPU
        self.tempo_transcorrido = 0
        self.segmentos = segmentos
        self.segmentos_ativos = set()
        self.DiscoCount = DiscoCount  # qtde de acessos ao disco
        self.LeitoraCount = LeitoraCount  # qtde de leituras de cartao
        self.ImpressoraCount = ImpressoraCount   # qtde de impressoes

        random.seed(T_MaxCPU + ImpressoraCount + LeitoraCount)
        # programa uma serie de eventos
        self.eventos_programados = list()

        qtde_eventos = ImpressoraCount + LeitoraCount #+ len(segmentos)

        times = [i*T_MaxCPU/(qtde_eventos + 1) for i in range(1, qtde_eventos + 1)]
        m = map(lambda e : e + random.gauss(0.0, T_MaxCPU*.05), times)
        times = [int(e) for e in m]
        # embaralha os instantes de interrupcao
        random.shuffle(times)

        # programa as mudancas de segmento
        # for _ in range(len(self.segmentos)):
        #     novo_evento = Evento('<RequisitarMemoria>', times.pop(), self)
        #     self.eventos_programados.append(novo_evento)
        # embaralha a ordem em que os segmentos sao chamados
        random.shuffle(self.segmentos)

        # programa as impressoes
        for _ in range(self.ImpressoraCount):
            eventoImpressao = Evento('<Imprimir>', times.pop(), self, random.choice(['P1', 'P2']))
            self.eventos_programados.append([eventoImpressao, False])

        # programa as leituras
        for _ in range(self.LeitoraCount):
            eventoLeitura = Evento('<Leitura>', times.pop(), self, random.choice(['L1', 'L2']))
            self.eventos_programados.append(eventoLeitura)

        # status do job que varia durante o seu curso de vida
        self.status = None

        ## Tempo de espera em fila
        self.tempo_espera_CPU = 0
        self.tempo_espera_Memoria = 0
        self.tempo_espera_Impressoras = 0
        self.tempo_espera_Leitoras = 0


    def atualizar_status(self, novo_status):
        self.status = novo_status

    def _sinc(self, tempo_avanco):
        self.tempo_transcorrido += tempo_avanco

    def run(self, tempo_avanco):
        last_time = self.tempo_transcorrido
        for evento in self.eventos_programados:
            if last_time <= evento[0].T_ocorrencia < last_time + tempo_avanco and not evento[1]:
                evento[1] = True
                self.tempo_transcorrido = evento[0].T_ocorrencia
                raise Mensagem('evento solicitado', (evento[0], evento[0].T_ocorrencia - last_time))
        # caso nenhum evento tenha sido solicitado
        self._sinc(tempo_avanco)
        raise Mensagem('time slice completado')

    def gera_log(self):
        print('Job:', self.nome)
        print('\tinstante de chegada:', self.T_chegada)
        print('\ttempo maximo de CPU:', self.T_MaxCPU)
        # print('\tsegmentos:', self.segmentos)
        print('\tQuantidade de acessos ao Disco:', self.DiscoCount)
        print('\tQuantidade de acessos aa Leitora:', self.LeitoraCount)
        print('\tQuantidade de acessos aa Impressora:', self.ImpressoraCount)
        print('\tEventos programados (tempos a partir do inicio da execucao do processo):')
        if len(self.eventos_programados) > 0:
            for evento in sorted(self.eventos_programados, key = lambda t : t[0].T_ocorrencia):
                print('\t\ttipo: {0}\tinstante previsto: {1}'.format(evento[0].tipo, evento[0].T_ocorrencia))
        print('\tTempo de espera em fila de CPU:', self.tempo_espera_CPU)
        print('\tTempo de espera em fila de Memoria:', self.tempo_espera_Memoria)
        print('\tTempo de espera em fila de Impressoras:', self.tempo_espera_Impressoras)
        print('\tTempo de espera em fila de Leitoras:', self.tempo_espera_Leitoras)

    def prox_segmento(self):
        seg = self.segmentos.pop()
        self.segmentos.insert(0, seg)
        return seg

    def __eq__(self, job):
        if isinstance(job, Job):
            return self.nome == job.nome
        else:
            return self.nome == job
