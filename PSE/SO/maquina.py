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


    # rotinas de tratamento de interrupcoes

    def Event1(self):
        pass

    def Event2(self):
        pass

    def Event3(self):
        pass

    def Event4(self):
        pass

    def Event5(self):
        pass

    def Event6(self):
        pass

    def Event7(self):
        pass


    # dicionario de eventos
    Eventos = {
        '<Event1>' = Event1,
        '<Event2>' = Event2,
        '<Event3>' = Event3,
        '<Event4>' = Event4,
        '<Event5>' = Event5,
        '<Event6>' = Event6,
        '<Event7>' = Event7,
    }
