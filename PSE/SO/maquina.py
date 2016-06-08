from PSE.ProjetoBase.maquinaBase import MaquinaBase

class Maquina(MaquinaBase):
    """docstring for Maquina"""
    def __init__(self, Ti, Tf):
        super(Maquina, self).__init__()
        if Ti >= 0:
            self._Ti = Ti
        else:
            self._Ti = 0

        if Tf >= 0:
            self.Tf = Tf
        else:
            self._Tf = 0
    
