import threading

class ResourcesManager:
    def __init__(self):
        """
        gerencia a disponibilidade dos recursos de e/s
        recursos disponiveis: 1 scanner, 2 impressoras, 1 modem, 2 SATAs
        """
        self.printers = [None, None]
        self.scanner = None
        self.modem = None
        self.sata = [None, None]
        self.lock = threading.Lock()

    def allocate(self, process):
        """
        Tenta alocar um recurso usando um lock para garantir a exclusão mútua
        Caso o recurso esteja disponível, atribuímos o pid do processo para o recurso
        """
        with self.lock:
            if process.printer in [1, 2]:
                if self.printers[process.printer-1] is not None:
                    return False
            if process.scanner == 1:
                if self.scanner is not None:
                    return False
            if process.modem == 1:
                if self.modem is not None:
                    return False
            if process.disk in [1, 2]:
                if self.sata[process.disk-1] is not None:
                    return False

            if process.printer in [1, 2]:
                self.printers[process.printer-1] = process.pid
            if process.scanner == 1:
                self.scanner = process.pid
            if process.modem == 1:
                self.modem = process.pid
            if process.disk in [1, 2]:
                self.sata[process.disk-1] = process.pid

            return True

    def release(self, pid):
        """
        Libera o recurso usado pelo processo
        """
        with self.lock:
            if self.scanner == pid:
                self.scanner = None
            if self.modem == pid:
                self.modem = None
            for i in range(2):
                if self.printers[i] == pid:
                    self.printers[i] = None
                if self.sata[i] == pid:
                    self.sata[i] = None
