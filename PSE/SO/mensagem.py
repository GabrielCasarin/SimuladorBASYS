class Mensagem(Exception):
    def __init__(self, msg, value=None):
        super(Mensagem, self).__init__()
        self.msg = msg
        self.value = value
    def __str__(self):
        return self.msg
