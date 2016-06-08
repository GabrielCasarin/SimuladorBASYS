from PSE.ProjetoBase.maquinaBase import MaquinaBase
import impressora
import memoria
import leitora
import disco
import cpu

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

        # dispositivos que a maquina deve conter
        self._cpu = cpu.CPU()
        self._disco = disco.Disco()
        self._memoria = memoria.Memoria()
        self._impressora1 = impressora.Impressora()
        self._impressora2 = impressora.Impressora()
        self._leitora1 = leitora.Leitora()
        self._leitora2 = leitora.Leitora() 
