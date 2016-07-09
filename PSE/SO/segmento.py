class Segmento(object):
    def __init__(self, nome, tamamanhoSegmento, job):
        super(Segmento, self).__init__()
        # self.disponivel = False
        self.nome = nome
        self.tamamanhoSegmento = tamamanhoSegmento
        self.job = job

    def __str__(self):
        return self.nome
