class Job(object):
    """docstring for Job"""
    def __init__(self, nome, tChegada, tMaxCPU, segmentos, IOcount, printCount):
        super(Job, self).__init__()

        self.nome = nome

        self.tChegada = tChegada
        self.tMaxCPU = tMaxCPU
        self.tempo_restante = tMaxCPU
        self.segmentos = segmentos
        self.IOcount = IOcount
        self.printCount = printCount
