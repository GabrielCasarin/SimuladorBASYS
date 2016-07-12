class Evento(object):
    """docstring for Evento"""
    def __init__(self, tipo, T_ocorrencia, job=None, recurso=None):
        super(Evento, self).__init__()
        self.tipo = tipo
        self.T_ocorrencia = T_ocorrencia
        self.job = job
        self.recurso = recurso

    def __str__(self):
        return str(self.T_ocorrencia) + ' ' + self.tipo + ' ' + str(self.job)
