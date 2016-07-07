class Job(object):
    """docstring for Job"""
    def __init__(self, nome, tChegada, tMaxCPU, tamMem, IOcount, printCount):
        super(Job, self).__init__()

        self.nome = nome

        if tChegada >= 0:
            self.tChegada = tChegada
        else:
            self.tChegada = 0

        if tMaxCPU >= 0:
            self.tMaxCPU = tMaxCPU
        else:
            self.tMaxCPU = 0

        if tamMem >= 0:
            self.tamMem = tamMem
        else:
            self.tamMem = 0

        if IOcount >= 0:
            self.IOcount = IOcount
        else:
            self.IOcount = 0

        if printCount >= 0:
            self.printCount = printCount
        else:
            self.printCount = 0
