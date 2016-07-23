from PSE.Base import MaquinaBase, Simulador, ListaPrioritaria
from PSE.SO import CPU, Disco, Evento, Impressora, Job, Leitora, Memoria, Mensagem, Segmento

class Maquina(MaquinaBase):
    def __init__(self, T_acionamento_clk, T_final, arquivos_conf_dict, time_slice_size, max_processos, disco_tempo_leitura, disco_tempo_escrita, gerenciador_arquivos_tempo_abertura, disco_tamanho, memoria_tempo_relocacao, memoria_tempo_transferencia, memoria_tamanho, impressora_tempo_impressao, leitora_tempo_leitura):#, jobs):
        super(Maquina, self).__init__()

        ## Seta o tempo de acionamento do RTC
        if T_acionamento_clk >= 0:
            self.T_acionamento_clk = T_acionamento_clk
        else:
            self.T_acionamento_clk = 0

        ## Seta o tempo final de máquina
        if T_final >= 0:
            self.T_final = T_final
        else:
            self.T_final = 0

        ## seta os valores das configuracoes globais
        self.max_processos = max_processos

        self.gerenciador_arquivos_tempo_abertura = gerenciador_arquivos_tempo_abertura

        ## dispositivos que a maquina deve conter
        self.CPU = CPU(time_slice_size)
        self.memoria = Memoria(memoria_tempo_relocacao, memoria_tempo_transferencia, memoria_tamanho)
        self.disco = Disco(disco_tempo_leitura, disco_tempo_escrita, disco_tamanho, arquivos_conf_dict)
        # impressoras
        self.impressora1 = Impressora('P1', impressora_tempo_impressao)
        self.impressora2 = Impressora('P2', impressora_tempo_impressao)
        self.impressorasID = {
            'P1': self.impressora1,
            'P2': self.impressora2,
        }
        # leitoras
        self.leitora1 = Leitora('L1', leitora_tempo_leitura)
        self.leitora2 = Leitora('L2', leitora_tempo_leitura)
        self.leitorasID = {
            'L1': self.leitora1,
            'L2': self.leitora2,
        }

        ## Job table
        self.job_table = list()

        self.agora = 0

    def trataEvento(self, evento):
        self.sincRelogio(self.simulador._agora)

        if self.agora <= self.T_final:
            if evento.tipo == '<Iniciar>':
                # pega o job que foi carregado durante o carregamento do arquivo de jobs
                # e chama a rotina de inicialização
                self.Iniciar(evento.job)

            elif evento.tipo == '<RequisitarMemoria>':
                job = evento.job
                nome, tamamanhoSegmento = job.prox_segmento()
                self.RequisitarMemoria(nome, tamamanhoSegmento, job, evento.T_ocorrencia)

            elif evento.tipo == '<RequisitarCPU>':
                self.RequisitarCPU(evento.job)

            elif evento.tipo == '<AbrirArquivo>':
                self.AbrirArquivo(evento.job, nome_arquivo=evento.recurso)

            elif evento.tipo == '<AcessarArquivo>':
                print(evento)
                self.AcessarArquivo(evento.job, nome_arquivo=evento.recurso)

            elif evento.tipo == '<LiberarDisco>':
                self.LiberarDisco(evento.job)

            elif evento.tipo == '<Imprimir>':
                self.Imprimir(evento.job, evento.recurso)

            elif evento.tipo == '<LiberarImpressora>':
                self.LiberarImpressora(job=evento.job, impressora=evento.recurso)

            elif evento.tipo == '<LiberarCPU>':
                self.LiberarCPU(evento.job)

            elif evento.tipo == '<LiberarMemoria>':
                self.LiberarMemoria(evento.job)

            elif evento.tipo == '<FinalizarJob>':
                self.FinalizarJob(evento.job)

            elif evento.tipo == '<EncerrarSimulacao>':
                self.EncerrarSimulacao()

    #### Rotinas de tratamento de INTERRUPCOES ####
    ## ---------------- ROTINAS DO JOB --------------- ##
    def Iniciar(self, novo_job):
        # seguindo o modelo de estados proposto no enunciado, todo job ao chegar no sistema entra no estado de 'chegada'
        novo_job.atualizarStatus('chegada')
        # insere o job na tabela de jobs ativos
        self.job_table.append(novo_job)
        # agenda uma requisição de memória
        eventoRequisicaoMem = Evento('<RequisitarMemoria>', novo_job.T_chegada, novo_job)
        self.simulador.addTask(eventoRequisicaoMem, 1, novo_job.T_chegada)
        novo_job.atualizarStatus('aguardando memoria')
        print('{0}\t<Iniciar>:\n\tjob {1} inserido na tabela\n'.format(self.agora, novo_job.nome))

    def FinalizarJob(self, job):
        # libera a CPU
        try:
            self.CPU.libera()
        except Mensagem as e:
            job.atualizarStatus('completo')
            print('{0}\t<FinalizarJob>:\n\tjob {1} concluiu-se\n'.format(self.agora, job.nome))
            if e.msg == 'job desempilhado':
                print('\tjob {0} foi desempilhado da fila da CPU\n'.format(job.nome))
                eventoRequisicaoCPU = Evento('<RequisitarCPU>', self.agora, job=e.value)
                self.simulador.addTask(eventoRequisicaoCPU, 1, eventoRequisicaoCPU.T_ocorrencia)

        # libera a memoria
        for seg in list(job.segmentos_ativos):
            try:
                self.memoria.liberar(seg)
            except Mensagem as e:
                # remove da lista de segmentos ativos aquele que acabou de ser retirado da memoria
                job.segmentos_ativos.remove(seg)
                if e.msg == 'processo desempilhado':
                    # pega o job que estava pedindo memoria e marca uma requisicao de memoria para ele
                    nome, tamamanhoSegmento, job_desempilhado = e.value
                    eventoRequisicaoMem = Evento('<RequisitarMemoria>', self.agora + self.memoria.T_relocacao, job_desempilhado)
                    print("\tjob {1} liberou o segmento '{2}'\n".format(self.agora, job.nome, seg))
                    self.simulador.addTask(eventoRequisicaoMem, 1, eventoRequisicaoMem.T_ocorrencia)
                elif e.msg == 'espaco liberado':
                    print("\tjob {1} liberou o segmento '{2}'\n".format(self.agora, job.nome, seg))
                elif e.msg == 'segmento nao encontrado':
                    print("\tfalta de segmento {2} (job {1})\n".format(self.agora, job.nome, e.value))

        # fecha os arquivos
        for arquivo in job.arquivosAbertos:
            try:
                self.disco.fechar(arquivo.nome)
            except Mensagem as e:
                if e.msg == 'arquivo fechado com sucesso':
                    print("\tarquivo {0} foi fechado com sucesso pelo job '{1}'\n".format(arquivo.nome, job.nome))
                elif e.msg == 'job desempilhado':
                    print("\tarquivo {0} foi fechado com sucesso pelo job '{1}'. Job {2} saiu da fila\n".format(arquivo.nome, job.nome, e.value.nome))
                    eventoRequisicaoArquivo = Evento('<AbrirArquivo>', self.agora, job=e.value, recurso=arquivo.nome)
                    self.simulador.addTask(eventoRequisicaoArquivo, 1, eventoRequisicaoArquivo.T_ocorrencia)
        print('\tTabela de Particoes do Disco')
        self.disco.log_tabelaParticoes()

    def EncerrarSimulacao(self):
        print('{0}\t<EncerrarSimulacao>:\n\tSimulacao acabou-se\n'.format(self.agora))
    ## ---------------- FIM ROTINAS DO JOB --------------- ##

    ## ---------------- MEMORIA CM ---------------- ##
    def RequisitarMemoria(self, nome_seg, tamamanhoSegmento, job, T_ocorrencia):
        agora = self.agora
        try:
            self.memoria.requisitar(nome_seg, tamamanhoSegmento, job, agora)
        except Mensagem as e:
            if e.msg == 'alocado com sucesso' or e.msg == 'segmento ja alocado':
                # caso o job tenha que fazer acesso a arquivo(s)
                if job.arquivos:
                    for arquivo in job.arquivos:
                        eventoRequisicaoArquivo = Evento('<AbrirArquivo>', T_ocorrencia + self.memoria.T_relocacao, job, recurso=arquivo)
                        self.simulador.addTask(eventoRequisicaoArquivo, 1, eventoRequisicaoArquivo.T_ocorrencia)
                    # atualiza o status do job para 'aguardando arquivo'
                    job.atualizarStatus('espera arquivos')
                # caso o job não faça acesso a arquivo, passa direto para requisição de CPU
                else:
                    eventoRequisicaoCPU = Evento('<RequisitarCPU>', T_ocorrencia + self.memoria.T_relocacao, job)
                    self.simulador.addTask(eventoRequisicaoCPU, 1, eventoRequisicaoArquivo.T_ocorrencia)
                    # atualiza o status do job para 'pronto' nesse caso
                    job.atualizarStatus('pronto')

                if e.msg == 'alocado com sucesso':
                    job.segmentos_ativos.add(nome_seg)
                    print('{0}\t<RequisitarMemoria>:\n\tjob {1} ganhou {2} bytes de memoria para o segmento \'{3}\'\n'.format(agora, job.nome, tamamanhoSegmento, nome_seg))
                else:
                    print('{0}\t<RequisitarMemoria>:\n\tjob {1} ja tinha estava com segmento \'{2}\' alocado\n'.format(agora, job.nome, nome_seg))

            # elif mensagemRetorno == 'inserido na fila da memoria':

    def LiberarMemoria(self, job, nome_seg):
        try:
            self.memoria.liberar(nome_seg)
        except Mensagem as e:
            if e.msg == 'processo desempilhado':
                job.segmentos_ativos.remove(nome_seg)
                nome, tamamanhoSegmento, job_desempilhado = e.value
                eventoRequisicaoMem = Evento('<RequisitarMemoria>', self.agora + self.memoria.T_relocacao, job_desempilhado)
                self.simulador.addTask(eventoRequisicaoMem, 1, eventoRequisicaoMem.T_ocorrencia)
                print('{0}\t<LiberarMemoria>:\n\tjob {1} liberou o segmento \'{2}\'\n'.format(self.agora, job.nome, nome_seg))
            elif e.msg == 'espaco liberado':
                job.segmentos_ativos.remove(nome_seg)
                print('{0}\t<LiberarMemoria>:\n\tjob {1} liberou o segmento \'{2}\'\n'.format(self.agora, job.nome, nome_seg))
            elif e.msg == 'segmento nao encontrado':
                print('{0}\t<LiberarMemoria>:\n\tfalta de segmento (job {1})\n'.format(self.agora, job.nome))
            job.atualizarStatus('pronto')
    ## ---------------- FIM MEMORIA CM ---------------- ##

    ## ---------------- ARQUIVO ---------------- ##
    def AbrirArquivo(self, job, nome_arquivo):
        try:
            self.disco.abrir(nome_arquivo, job)
        except Mensagem as e:
            if e.msg == "arquivo nao especificado":
                print("{0}\t<AbrirArquivo>:\n\tjob {1} tentou abrir arquivo '{2}' nao especificado\n".format(self.agora, job.nome, nome_arquivo))
                job.atualizarStatus('erro')
                eventoFinalizaJob = Evento('<FinalizarJob>', self.agora, job)
                self.simulador.addTask(eventoFinalizaJob, 1, eventoFinalizaJob.T_ocorrencia)

            elif e.msg == "inserido na fila do arquivo":
                print("{0}\t<AbrirArquivo>:\n\tjob {1} entrou na fila do arquivo {2}\n".format(self.agora, job.nome, nome_arquivo))

            elif e.msg == "arquivo aberto com sucesso":
                print("{0}\t<AbrirArquivo>:\n\tjob {1} abriu o arquivo '{2}' com sucesso\n".format(self.agora, job.nome, nome_arquivo))
                # a funcao 'abrir' do disco retorna uma referencia para o arquivo aberto (caso haja)
                arquivo_aberto = e.value
                # inserimo-lo na lista de arquivos abertos do job em questao
                job.arquivosAbertos.append(arquivo_aberto)
                # um job so prossegue sua execucao caso TODOS os recursos que pedir forem dados a ele
                # isso quer dizer que, enquanto todos os arquivos que ele quiser abrir nao o forem, ele simplesmente nao segue adiante
                if job.todosArquivosAbertos():
                    eventoRequisicaoCPU = Evento('<RequisitarCPU>', self.agora + self.gerenciador_arquivos_tempo_abertura, job)
                    self.simulador.addTask(eventoRequisicaoCPU, 1, eventoRequisicaoCPU.T_ocorrencia)

            elif e.msg == "inserido na fila dos que esperam particao livre":
                print("{0}\t<AbrirArquivo>:\n\tjob {1} nao conseguiu abrir o arquivo '{2}'. Job inserido na fila dos que esperam por liberacao de particao.\n".format(self.agora, job.nome, nome_arquivo))

            elif e.msg == "acesso negado":
                print("{0}\t<AbrirArquivo>:\n\tjob {1} nao tem permissao para acessar o arquivo {2}\n".format(self.agora, job.nome, nome_arquivo))
                job.atualizarStatus('erro')
                eventoFinalizaJob = Evento('<FinalizarJob>', self.agora, job)
                self.simulador.addTask(eventoFinalizaJob, 1, eventoFinalizaJob.T_ocorrencia)

            print('\tTabela de Particoes do Disco')
            self.disco.log_tabelaParticoes()

    def AcessarArquivo(self, job, nome_arquivo):
        job.atualizarStatus('espera e/s')

        # libera CPU "na marra"
        try:
            self.CPU.libera()
        except Mensagem as e:
            if e.msg == 'job desempilhado':
                eventoRequisicaoCPU = Evento('<RequisitarCPU>', self.agora, job=e.value)
                self.simulador.addTask(eventoRequisicaoCPU, 1, eventoRequisicaoCPU.T_ocorrencia)

        try:
            self.disco.requisita(job, nome_arquivo)
        except Mensagem as e:
            if e.msg == 'alocado com sucesso':
                print("{0}\t<AcessarArquivo>:\n\tjob '{1}' iniciou operacao de E/S no arquivo '{3}' (tempo de CPU transcorrido = {2})\n".format(self.agora, job.nome, job.tempo_transcorrido, nome_arquivo))
                # agenda a liberacao do disco
                eventoLiberaDisco = Evento('<LiberarDisco>', self.agora + self.disco.T_leitura + self.disco.T_escrita, job)
                self.simulador.addTask(eventoLiberaDisco, 1, eventoLiberaDisco.T_ocorrencia)
            elif e.msg == 'disco ocupado':
                print("{0}\t<AcessarArquivo>:\n\tjob '{1}' entrou na fila de E/S do disco\n".format(self.agora, job.nome))
            elif e.msg == 'acesso negado':
                print("{0}\t<AcessarArquivo>:\n\tjob '{1}' teve acesso negado ao arquivo '{2}'\n".format(self.agora, job.nome, nome_arquivo))
                job.atualizarStatus('pronto')
                eventoRequisicaoCPU = Evento('<RequisitarCPU>', self.agora)
                self.simulador.addTask(eventoRequisicaoCPU, 1, eventoRequisicaoCPU.T_ocorrencia)

    def LiberarDisco(self, job):
        try:
            self.disco.libera()
        except Mensagem as e:
            if e.msg == 'job desempilhado':
                task, tempoEntradaFila = e.value
                job_requisitante, nome_arquivo = task
                # atualiza a estatistica do job
                job_requisitante.tempo_espera_Disco += self.agora - tempoEntradaFila
                eventoRequisicaoDisco = Evento('<AcessarArquivo>', self.agora, job=job_requisitante, recurso=nome_arquivo)
                self.simulador.addTask(eventoRequisicaoDisco, 1, eventoRequisicaoDisco.T_ocorrencia)
                print("{0}\t<LiberarDisco>:\n\tOperacao de E/S do job '{1}' terminada. Job {2} saiu da fila\n".format(self.agora, job.nome, job_requisitante.nome))
            elif e.msg == 'disco livre':
                print("{0}\t<LiberarDisco>:\n\tOperacao de E/S do job '{1}' terminada\n".format(self.agora, job.nome))

            # em ambos os casos, o job liberado entra no round robin novamente
            eventoRequisicaoCPU = Evento('<RequisitarCPU>', self.agora, job=job)
            self.simulador.addTask(eventoRequisicaoCPU, 1, eventoRequisicaoCPU.T_ocorrencia)

    ## ---------------- ESCALONAMENTO CPU ---------------- ##
    def RequisitarCPU(self, job):
        try:
            self.CPU.reserva(job, 1)
        except Mensagem as e:
            if e.msg == 'alocado com sucesso':
                job.atualizarStatus('em execucao')
                timeSlice = self.CPU.timeSlice
                if job.tempo_transcorrido + timeSlice >= job.T_MaxCPU:
                    delta = job.T_MaxCPU - job.tempo_transcorrido
                else:
                    delta = timeSlice
                print('{0}\t<RequisitarCPU>:\n\tjob {1} ganhou CPU por ate {2} u.t.\n'.format(self.agora, job.nome, delta))
                # tenta executar o job
                try:
                    job.run(delta)
                except Mensagem as e:
                    if e.msg == 'time slice completado':
                        if job.tempo_transcorrido >= job.T_MaxCPU:
                            eventoFinalizaJob = Evento('<FinalizarJob>', self.agora, job)
                            self.simulador.addTask(eventoFinalizaJob, 0, self.agora + delta)
                        else:
                            eventoLiberaCPU = Evento('<LiberarCPU>', self.agora + delta, job)
                            self.simulador.addTask(eventoLiberaCPU, 1, eventoLiberaCPU.T_ocorrencia)
                    elif e.msg == 'evento solicitado':
                        evento, delta = e.value
                        eventoNovo = Evento(evento.tipo, self.agora + delta, evento.job, evento.recurso)
                        self.simulador.addTask(eventoNovo, 1, eventoNovo.T_ocorrencia)

            elif e.msg == 'inserido na fila da CPU':
                print('{0}\t<RequisitarCPU>:\n\tjob {1} inserido na fila da CPU\n'.format(self.agora, job.nome))

    def LiberarCPU(self, job):
        try:
            job_antigo = self.CPU.job_em_execucao
            # Round Robin
            if job_antigo not in self.CPU.fila:
                self.CPU.fila.insert(0, job_antigo)
            self.CPU.libera()
        except Mensagem as e:
            job.atualizarStatus('pronto')
            print('{0}\t<LiberarCPU>:\n\tjob {1} liberou CPU (tempo trascorrido = {2})\n'.format(self.agora, job.nome, job.tempo_transcorrido))
            if e.msg == 'job desempilhado':
                eventoRequisicaoCPU = Evento('<RequisitarCPU>', self.agora, job=e.value)
            elif e.msg == 'CPU livre':
                eventoRequisicaoCPU = Evento('<RequisitarCPU>', self.agora, job=job_antigo)

            self.simulador.addTask(eventoRequisicaoCPU, 1, eventoRequisicaoCPU.T_ocorrencia)
    ## ---------------- FIM ESCALONAMENTO CPU ---------------- ##

    ## ---------------- IMPRESSORA ---------------- ##
    def Imprimir(self, job, impressora):
        impressora = self.impressorasID[impressora]
        job.atualizarStatus('espera e/s')

        # libera CPU "na marra"
        try:
            self.CPU.libera()
        except Mensagem as e:
            if e.msg == 'job desempilhado':
                eventoRequisicaoCPU = Evento('<RequisitarCPU>', self.agora, job=e.value)
                self.simulador.addTask(eventoRequisicaoCPU, 1, eventoRequisicaoCPU.T_ocorrencia)

        try:
            impressora.requisita(job)
        except Mensagem as e:
            if e.msg == 'alocado com sucesso':
                eventoLiberarImpressora = Evento('<LiberarImpressora>', self.agora + impressora.T_impressao, job, impressora)
                self.simulador.addTask(eventoLiberarImpressora, 1, eventoLiberarImpressora.T_ocorrencia)
                print('{0}\t<Imprimir>:\n\tjob {1} iniciou impressao na impressora {2} (tempo de CPU transcorrido = {3})\n'.format(self.agora, job.nome, impressora.label, job.tempo_transcorrido))
            elif e.msg == 'impressora ocupada':
                print('{0}\t<Imprimir>:\n\tjob {1} entrou na fila de impressao (tempo de CPU transcorrido = {2})\n'.format(self.agora, job.nome, job.tempo_transcorrido))

    def LiberarImpressora(self, job, impressora):
        try:
            impressora.libera()
        except Mensagem as e:
            if e.msg == 'job desempilhado':
                eventoRequisicaoImpressao('<Imprimir>', self.agora, job=e.value)
                self.simulador.addTask(eventoRequisicaoImpressao, 1, eventoRequisicaoImpressao.T_ocorrencia)
                print('{0}\t<LiberarImpressora>:\n\tImpressora {1} terminou execucao. Job {2} saiu da fila\n'.format(self.agora, impressora.label, e.value.nome))
            elif e.msg == 'impressora livre':
                print('{0}\t<LiberarImpressora>:\n\tImpressora {1} terminou execucao\n'.format(self.agora, impressora.label))

            # em ambos os casos, o job liberado entra no round robin novamente
            eventoRequisicaoCPU = Evento('<RequisitarCPU>', self.agora, job=job)
            self.simulador.addTask(eventoRequisicaoCPU, 1, eventoRequisicaoCPU.T_ocorrencia)

    ## ---------------- FIM IMPRESSORA ---------------- ##

    ## ---------------- LEITORA ---------------- ##
    def Leitura(self, job, leitora):
        leitora = self.leitorasID[leitora]
        job.atualizarStatus('espera e/s')

        # libera CPU "na marra"
        try:
            self.CPU.libera()
        except Mensagem as e:
            if e.msg == 'job desempilhado':
                eventoRequisicaoCPU = Evento('<RequisitarCPU>', self.agora, job=e.value)
                self.simulador.addTask(eventoRequisicaoCPU, 1, eventoRequisicaoCPU.T_ocorrencia)

        try:
            leitora.requisita(job)
        except Mensagem as e:
            if e.msg == 'alocado com sucesso':
                eventoLiberarLeitora = Evento('<LiberarLeitora>', self.agora + leitora.T_leitura, job, leitora)
                self.simulador.addTask(eventoLiberarLeitora, 1, eventoLiberarLeitora.T_ocorrencia)
                print('{0}\t<Leitura>:\n\tjob {1} iniciou leitura na leitora {2} (tempo de CPU transcorrido = {3})\n'.format(self.agora, job.nome, leitora.label, job.tempo_transcorrido))
            elif e.msg == 'leitora ocupada':
                print('{0}\t<Leitura>:\n\tjob {1} entrou na fila de leitura (tempo de CPU transcorrido = {2})\n'.format(self.agora, job.nome, job.tempo_transcorrido))

    def LiberarLeitora(self, job, leitora):
        try:
            leitora.libera()
        except Mensagem as e:
            if e.msg == 'job desempilhado':
                eventoRequisicaoImpressao('<Imprimir>', self.agora, job=e.value)
                self.simulador.addTask(eventoRequisicaoImpressao, 1, eventoRequisicaoImpressao.T_ocorrencia)
                print('{0}\t<LiberarImpressora>:\n\tImpressora {1} terminou execucao. Job {2} saiu da fila\n'.format(self.agora, impressora.label, e.value.nome))
            elif e.msg == 'leitora livre':
                print('{0}\t<LiberarImpressora>:\n\tImpressora {1} terminou execucao\n'.format(self.agora, impressora.label))

            # em ambos os casos, o job liberado entra no round robin novamente
            eventoRequisicaoCPU = Evento('<RequisitarCPU>', self.agora, job=job)
            self.simulador.addTask(eventoRequisicaoCPU, 1, eventoRequisicaoCPU.T_ocorrencia)

    ## ---------------- FIM LEITORA ---------------- ##
    #### FIM Rotinas de tratamento de INTERRUPCOES ####

    ## Demais rotinas
    def setSimulator(self, simulador):
        if isinstance(simulador, Simulador):
            self.simulador = simulador
            self.simulador._agora = self.T_acionamento_clk
            self.simulador.addTask(Evento('<EncerrarSimulacao>', self.T_final), 1, self.T_final)
        else:
            self.simulador = None

    def sincRelogio(self, tempoAtual):
        self.agora = tempoAtual
        self.CPU.agora = tempoAtual
        self.memoria.agora = tempoAtual
        self.disco.agora = tempoAtual
        # impressoras
        self.impressora1.agora = tempoAtual
        self.impressora2.agora = tempoAtual
        # leitoras
        self.leitora1.agora = tempoAtual
        self.leitora2.agora = tempoAtual

    def fim(self, task):
        if task.tipo == '<EncerrarSimulacao>':
            return True
        return False
