class Estado(object):
    """docstring for Estado"""
    def __init__(self, nome, final=False):
        super(Estado, self).__init__()
        self._nome = nome
        self._transicoes = {}
        self._final = final

    def setFinal(self):
        self._final = True

    def unsetFinal(self):
        self._final = False

    def isFinal(self):
        return self._final

    def __setitem__(self, symbol, prox):
        self._transicoes[symbol] = prox

    def __getitem__(self, symbol):
    	return self._transicoes[symbol]

    def __eq__(self, estado):
    	if isinstance(estado, Estado):
    		return self == estado._nome
    	else:
    		return self._nome == estado

    def __contains__(self, item):
        return item in self._transicoes.keys()

    def __str__(self):
        return self._nome
