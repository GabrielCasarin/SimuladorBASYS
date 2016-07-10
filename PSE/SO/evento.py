class Evento(object):
    """docstring for Evento"""
    def __init__(self, tipo, T_ocorrencia, job):
        super(Evento, self).__init__()
        self.tipo = tipo
        self.T_ocorrencia = T_ocorrencia
        self.job = job

    def tipo(self):
        return self.tipo

    def __str__(self):
        return str(self.T_ocorrencia) + ' ' + self.tipo + ' ' + str(self.job)
