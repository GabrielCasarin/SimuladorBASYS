from PSE.Base import ListaPrioritaria
from PSE.SO import Mensagem

class Leitora(object):
    """docstring for Leitora"""
    def __init__(self, label, T_leitura):
        super(Leitora, self).__init__()
        self.label = label
        self.T_leitura = T_leitura
        self.busy = False
        self.processo_atual = None
        self.fila = ListaPrioritaria()
        self.agora = 0

    def requisita(self, job_requisitante):
        if not self.busy:
            self.processo_atual = job_requisitante
            self.busy = True
            raise Mensagem('alocado com sucesso')
        else:
            self.fila.push(job_requisitante, 1, self.agora)
            raise Mensagem('leitora ocupada')

    def libera(self):
        self.busy = False
        self.processo_atual = None
        if self.fila:
            raise Mensagem('job desempilhado', self.fila.pop())
        else:
            raise Mensagem('leitora livre')
