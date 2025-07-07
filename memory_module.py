class MemoryManager:
    def __init__(self):
        """
        gerencia a memoria principal de 1024 blocos
        - 64 blocos para processos de tempo real
        - 960 blocos para processos de usuário
        a alocacao é contigua
        """
        self.total_blocks = 1024
        self.real_time_blocks = 64
        self.bitmap = [0] * self.total_blocks
        self.table = {}

    def allocate(self, process):
        """
        Tenta alocar blocos contíguos para o processo
        Caso haja espaço disponível, atualizamos o bitmap e a tabela com o pid e o 
        número de blocos do processo
        """
        if(process.priority == 0):
            start = 0
            end = self.real_time_blocks
        else:
            start = self.real_time_blocks
            end = self.total_blocks
        for i in range(start, end - process.memory_blocks + 1):
            if all(self.bitmap[j] == 0 for j in range(i, i + process.memory_blocks)):
            # Aloca
                for j in range(i, i + process.memory_blocks):
                    self.bitmap[j] = 1
                self.table[process.pid] = (i, process.memory_blocks)
                return i  # retorna o offset
        return -1  # falha na alocação
        

    def deallocate(self, process):
        """
        Libera os blocos de memória usados pelo processo atualizando a tabela e o bitmap
        """
        if process.pid not in self.table:
            return False

        offset, size = self.table[process.pid]
        for i in range(offset, offset + size):
            self.bitmap[i] = 0
        del self.table[process.pid]
        return True
