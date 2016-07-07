from PSE.Base.maquinaBase import MaquinaBase
import PSE.Base.lista as lista
import PSE.SO.impressora as impressora
import PSE.SO.memoria as memoria
import PSE.SO.leitora as leitora
import PSE.SO.disco as disco
import PSE.SO.cpu as cpu

class Maquina(MaquinaBase):
    """docstring for Maquina"""
    def __init__(self, T_acionamento_clk, T_final, jobs):
        super(Maquina, self).__init__()
        if T_acionamento_clk >= 0:
            self.T_acionamento_clk = T_acionamento_clk
        else:
            self.T_acionamento_clk = 0

        if T_final >= 0:
            self.T_final = T_final
        else:
            self.T_final = 0

        # dispositivos que a maquina deve conter
        # self.cpu = cpu.CPU()
        # self.disco = disco.Disco()
        # self.memoria = memoria.Memoria()
        # self.impressora1 = impressora.Impressora()
        # self.impressora2 = impressora.Impressora()
        # self.leitora1 = leitora.Leitora()
        # self.leitora2 = leitora.Leitora()

        # Filas de recursos
        self.cm_q = lista.ListaPrioritaria()
        self.cpu_q = lista.ListaPrioritaria()
        self.disk_q = lista.ListaPrioritaria()

        # Job table
        self.job_table = {
            job.nome: job for job in jobs
        }

    def trataEvento(self, evento):
        if evento.tipo() == '<Event1>':
            pass

        elif evento.tipo() == '<Event2>':
            pass

        elif evento.tipo() == '<Event3>':
            pass

        elif evento.tipo() == '<Event4>':
            pass

        elif evento.tipo() == '<Event5>':
            pass

        elif evento.tipo() == '<Event6>':
            pass

        elif evento.tipo() == '<Event7>':
            pass


    # rotinas de tratamento de interrupcoes

    def Event1(self):


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
        '<Event1>': Event1,
        '<Event2>': Event2,
        '<Event3>': Event3,
        '<Event4>': Event4,
        '<Event5>': Event5,
        '<Event6>': Event6,
        '<Event7>': Event7,
    }
