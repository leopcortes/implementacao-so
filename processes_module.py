import time
import threading


class Processes:
  quantum = 1 #milissegundos
  pid = 0
  processes_that_arrived = []
  all_processes = []
  blocked_processes = []

  def __init__(self, arrival_time, priority, total_time, memory_blocks, printer, scanner, modem, disk):
    self.pid = Processes.pid
    Processes.pid += 1
    self.arrival_time = arrival_time
    self.offset = None # será atribuido depois de alocar o espaço na memoria
    self.priority = priority
    self.total_time = total_time
    self.processing_time = 0
    self.memory_blocks = memory_blocks
    self.printer = printer
    self.scanner = scanner
    self.modem = modem
    self.disk = disk
    self.wait_time = 0
    self.has_resources = False
    if (priority == 0):
      self.queue = 0
    else:
      self.queue = 1

  def get_instructions_status(self, first, last, cpu_total_quantums=0):
    if (first):
      print(f"""\nprocess {self.pid} =>""")
      print(f"""    P{self.pid} STARTED""")
      
    print(f"""    P{self.pid} instruction {self.processing_time}""")
      
    if (last):
      print(f"""    P{self.pid} return SIGINT\n""")
      print(f"""    Current quantum in CPU: {cpu_total_quantums}""")
      
  def get_process_status(self):
    print(self) 

  def __str__(self):
    return f"""
      dispatcher =>
      PID: {self.pid} 
      offset: {self.offset}
      blocks: {self.memory_blocks} 
      queue: {self.queue} 
      priority: {self.priority} 
      total time: {self.total_time} 
      processing time: {self.processing_time} 
      printers : {self.printer} 
      scanners : {self.scanner} 
      modems : {self.modem}
    """
  
  def get_all_resources(self, queues, resource_manager):
    # Tenta obter o recurso. Caso não consiga, coloca o processo na lista de bloqueados (Processes.blocked_processes) e cria a thread 
    # que vai chamar a função para tentar obter o recurso. Quando conseguir, chamar a função queues.add_process(*processo) para colocar 
    # o processo de volta a lista de prontos e remover da lista de bloqueados.    
    if self.modem > 1 or self.scanner > 1 or self.printer > 2 or self.disk > 2:
      return False
    
    if resource_manager.allocate(self):
      self.has_resources = True
      return True
    Processes.blocked_processes.append(self)

    def try_allocate():
      while True:
        time.sleep(0.01)  # aguarda 10ms
        if resource_manager.allocate(self):
          try:
            Processes.blocked_processes.remove(self)
          except ValueError:
            pass
          self.has_resources = True
          queues.add_process(self, False)
          break

    # cria e inicia a thread que vai tentar alocar os recursos futuramente
    t = threading.Thread(target=try_allocate, daemon=True)
    t.start()

    return False

  def close_process(self, memory_manager, resource_manager, queues):
    resource_manager.release(self.pid)
    memory_manager.deallocate(self.pid)
    from queues_module import Queues
    Queues.count -= 1
    
