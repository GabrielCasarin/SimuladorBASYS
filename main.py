from PSE.Base.simulador import Simulador
from PSE.Logica.automatoFinito import AutomatoFinito
from PSE.Logica.automatoPilhaEstruturado import AutomatoPilhaEstruturado
from PSE.Logica.maquinaTuring import MaquinaTuring
import PSE.Logica.analisador as analisador

def main():
    nomearq = input('Nome do arquivo: ')
    with open(nomearq, 'r') as input_file:
        tipo = input('Qual o tipo de maquina: ')
        cadeia = input('Digite a cadeia: ')
        if tipo == 'MT':
            d = analisador.parseMT(input_file.read())
            maq = MaquinaTuring(**d, cadeia= '#'+cadeia)
        elif tipo == 'AP':
            d = analisador.parseAP(input_file.read())
            # for key in d:
            #     if key != 'sub-maquinas':
            #         print(key, '<-->', d[key])
            #     else:
            #         for el in d[key]:
            #             for key_el in el:
            #                 print('\t', key_el, '<-->', el[key_el])
            maq = AutomatoPilhaEstruturado(**d, cadeia=cadeia)
        elif tipo == 'AF':
            d = analisador.parseAF(input_file.read())
            maq = AutomatoFinito(**d, cadeia=cadeia)

        sim = Simulador(maq)
        sim.addTask('<PartidaInicial>', 1, sim._agora)
        sim.simulate()

if __name__ == '__main__':
    main()
