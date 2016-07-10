class Disco(object):
    """docstring for Disco"""
    def __init__(self, T_leitura, T_escrita, tamanho):
        super(Disco, self).__init__()
        self.T_leitura = T_leitura
        self.T_escrita = T_escrita
        self.tamanho = tamanho
