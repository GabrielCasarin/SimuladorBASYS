from PSE.Base.lista import ListaPrioritaria

class CPU(object):
    """docstring for CPU"""
    def __init__(self):
        super(CPU, self).__init__()
        self.busy = False
        self.fila = ListaPrioritaria()

    def reserva(self):
        self.busy = True

    def libera(self):
        self.busy = False
        self.fila.pop()
