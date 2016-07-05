class Job(object):
    """docstring for Job"""
    def __init__(self, Ti, Ttotal, tamMem, IOcount):
        super(Job, self).__init__()

        if Ti >= 0:
            self._Ti = Ti
        else:
            self._Ti = 0

        if Ttotal >= 0:
            self.Ttotal = Ttotal
        else:
            self._Ttotal = 0

        if tamMem >= 0:
            self.tamMem = tamMem
        else:
            self._tamMem = 0

        if IOcount >= 0:
            self.IOcount = IOcount
        else:
            self._IOcount = 0
