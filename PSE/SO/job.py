class Job(object):
    """docstring for Job"""
    def __init__(self, nome, T_chegada, T_MaxCPU, segmentos, DiscoCount, LeitoraCount, ImpressoraCount, eventos_programados):
        super(Job, self).__init__()

        self.nome = nome
        self.T_chegada = T_chegada
        self.T_MaxCPU = T_MaxCPU
        self.tempo_restante = tMaxCPU
        self.tempo_transcorrido = 0
        self.segmentos = segmentos
        self.DiscoCount = DiscoCount
        self.LeitoraCount = LeitoraCount
        self.ImpressoraCount = ImpressoraCount

        self.eventos_programados = eventos_programados

    def __eq__(self, job):
        if isinstance(job, Job):
            return self.nome == job.nome
        else:
            return self.nome == job

    def sinc(self, timeSlice):
        self.tempoTranscorrido += tempoTranscorrido
