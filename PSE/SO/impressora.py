from PSE.SO import Mensagem

class Impressora(object):
    """docstring for Impressora"""
    def __init__(self, label, T_impressao):
        super(Impressora, self).__init__()
        self.T_impressao = T_impressao
        self.label = label
        self.busy = False
        self.processo_atual = None
        self.fila = list()

    def requisita(self, job_requisitante):
        if not self.busy:
            self.processo_atual = job_requisitante
            self.busy = True
            raise Mensagem('alocado com sucesso')
        else:
            self.fila.insert(0, job_requisitante)
            raise Mensagem('impressora ocupada')

    def libera(self):
        self.busy = False
        self.processo_atual = None
        if len(self.fila) > 0:
            raise Mensagem('job desempilhado', self.fila.pop())
        else:
            raise Mensagem('impressora livre')
