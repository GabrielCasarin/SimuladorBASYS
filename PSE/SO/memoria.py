from PSE.Base import ListaPrioritaria
from PSE.SO import Segmento, Mensagem


class Memoria(object):
    def __init__(self, T_relocacao, T_acesso, tamanho):
        super(Memoria, self).__init__()
        self.tamanho = tamanho
        self.mem_disponivel = tamanho
        self.T_relocacao = T_relocacao
        self.segmentos = dict()
        self.fila = ListaPrioritaria()

    def requisitar(self, nome, tamamanhoSegmento, job, tempoAtual):
        # verificam se o segmento ja foi alocado ao job
        for seg in self.segmentos:
            if self.segmentos[seg].nome == nome and \
                self.segmentos[seg].job == job:
                    raise Mensagem('segmento ja alocado')

        # caso nao haja espaco suficiente
        if tamamanhoSegmento > self.mem_disponivel:
            self.fila.push((nome, tamamanhoSegmento, job), 1, tempoAtual)
            raise Mensagem('inserido na fila da memoria')
        else:
        # caso haja
            self.mem_disponivel -= tamamanhoSegmento
            novoSegmento = Segmento(nome, tamamanhoSegmento, job)
            self.segmentos[nome] = novoSegmento
            raise Mensagem('alocado com sucesso')


    def liberar(self, nome):
        if nome in self.segmentos:
            self.mem_disponivel += self.segmentos[nome].tamamanhoSegmento
            self.segmentos.pop(nome)
            if len(self.fila) > 0:
                temp, _ = self.fila.pop()
                raise Mensagem('processo desempilhado', temp)
            else:
                raise Mensagem('espaco liberado')
        else:
            raise Mensagem('segmento nao encontrado')
