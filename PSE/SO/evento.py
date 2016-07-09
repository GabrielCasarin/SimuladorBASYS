class Evento(object):
    """docstring for Evento"""
    def __init__(self, tipo, t_ocorrencia, job):
        super(Evento, self).__init__()
        self.tipo = tipo
        self.t_ocorrencia = t_ocorrencia
        self.nome_job = job

    def tipo(self):
        return self.tipo

    def __str__(self):
        return str(self.t_ocorrencia) + ' ' + self.tipo + ' ' + str(self.job)
