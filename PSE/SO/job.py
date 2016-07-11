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

        random.seed(T_MaxCPU)
        # programa uma serie de eventos
        self.eventos_programados = list()

        qtde_eventos = len(segmentos)

        times = [i*T_MaxCPU/(qtde_eventos + 1) for i in range(1, qtde_eventos + 1)]
        m = map(lambda e : e + random.gauss(0.0, T_MaxCPU*.05), times)
        times = [int(e) for e in m]
        random.shuffle(times)
        while len(times) > 0:
            novo_evento = Evento('<RequisitarMemoria>', times.pop(), self)
            self.eventos_programados.append(novo_evento)
        random.shuffle(self.segmentos)

        self.status = None

    def atualizar_status(self, novo_status):
        self.status = novo_status

    def _sinc(self, tempo_avanco):
        self.tempo_transcorrido += tempo_avanco

    def run(self, tempo_avanco):
        # last_time = self.tempo_transcorrido
        # for evento in eventos_programados:
        #     if self.tempo_transcorrido <= evento.t_ocorrencia < self.tempo_transcorrido + tempo_avanco:
        #         self._sinc(evento.t_ocorrencia - self.tempo_transcorrido)
        #         raise Mensagem('evento solicitado', evento)
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
        print('Eventos programados:')
        for evento in self.eventos_programados:
            print('\t\ttipo: {0}\tinstante previsto: {1}'.format(evento.tipo, evento.T_ocorrencia))

    def prox_segmento(self):
        seg = self.segmentos.pop()
        self.segmentos.insert(0, seg)
        return seg

    def __eq__(self, job):
        if isinstance(job, Job):
            return self.nome == job.nome
        else:
            return self.nome == job
