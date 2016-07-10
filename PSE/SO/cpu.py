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

    def reserva(self, job):
        if self.busy:
            self.fila.push(job)
            raise Mensagem('inserido na fila da CPU')
        else:
            self.job_em_execucao = job
            self.busy = True
            raise Mensagem('alocado com sucesso')


    def libera(self):
        self.busy = False
        if len(self.fila) > 0:
            raise Mensagem('job desempilhado', self.fila.pop())
        else:
            raise Mensagem('CPU livre')
