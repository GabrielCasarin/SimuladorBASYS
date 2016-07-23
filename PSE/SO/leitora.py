from PSE.SO import Mensagem

class Leitora(object):
    """docstring for Leitora"""
    def __init__(self, label, T_leitura):
        super(Leitora, self).__init__()
        self.label = label
        self.T_leitura = T_leitura
        self.busy = False
        self.processo_atual = None
        self.fila = list()
        self.agora = 0

    def requisita(self, job_requisitante):
        if not self.busy:
            self.processo_atual = job_requisitante
            self.busy = True
            raise Mensagem('alocado com sucesso')
        else:
            self.fila.insert(0, job_requisitante)
            raise Mensagem('leitora ocupada')

    def libera(self):
        self.busy = False
        self.processo_atual = None
        if len(self.fila) > 0:
            raise Mensagem('job desempilhado', self.fila.pop())
        else:
            raise Mensagem('leitora livre')
