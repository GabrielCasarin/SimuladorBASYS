class Evento(object):
    """docstring for Evento"""
    def __init__(self, tipo, T_ocorrencia, job=None, recurso=None):
        super(Evento, self).__init__()
        self.tipo = tipo
        self.T_ocorrencia = T_ocorrencia
        self.job = job
        self.recurso = recurso

    def __str__(self):
        if self.recurso is not None:
            return "{0:>5}:\t{1:<20}\trecurso utilizado -> {2}".format(self.T_ocorrencia, self.tipo, self.recurso)
        else:
            return "{0:<5}:{1:<20}".format(self.T_ocorrencia, self.tipo)
