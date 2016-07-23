from PSE.Base import ListaPrioritaria
from PSE.SO import Mensagem

class CPU(object):
    """docstring for CPU"""
    def __init__(self, timeSlice):
        super(CPU, self).__init__()
        self.timeSlice = timeSlice
        self.busy = False
        self.fila = ListaPrioritaria()
        self.job_em_execucao = None
        self.agora = 0

    def reserva(self, job, prioridade):
        if self.busy:
            if job not in self.fila:
                self.fila.push(job, 1, self.agora)
            raise Mensagem('inserido na fila da CPU')
        else:
            self.job_em_execucao = job
            self.busy = True
            raise Mensagem('alocado com sucesso')

    def libera(self):
        self.busy = False
        self.job_em_execucao = None
        if self.fila:
            raise Mensagem('job desempilhado', self.fila.pop())
        else:
            raise Mensagem('CPU livre')
