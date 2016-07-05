pilha = [('S', 'q0'), ('E', 'q1')]

def printPilha(pilha):
    pilhaStrs = []
    for el in pilha:
        pilhaStrs.append(" {SubMaq}/{EstRet} |".format(SubMaq=el[0], EstRet=el[1]))

    print('-', end='')
    for elStr in pilhaStrs:
        print('{0:-<{1}}'.format('', len(elStr)), end='')
    print()
    print('|', end='')
    for elStr in pilhaStrs:
        print(elStr, end='')
    print()
    print('-', end='')
    for elStr in pilhaStrs:
        print('{0:-<{1}}'.format('', len(elStr)), end='')
    print()


printPilha(pilha)
