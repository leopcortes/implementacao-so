from processes_module import Processes
from queues_module import Queues

cpu_total_quantums = 0 #Número de quantums que a CPU já passou
processing_time = 0 #tempo (em quantums) que o processo tem de CPU
current_process_in_cpu = False #Atual processo na CPU ou False
first = False #Usado para marcar quando há a troca de processos na CPU

queues = Queues()

#TODO
#Tem que substituir essa parte para obter as informações dos arquivos
process1 = Processes(0, 0, 2, 64, 0, 0, 0, 0) 
process2 = Processes(2, 0, 5, 64, 0, 0, 0, 0) 
process3 = Processes(3, 0, 3, 64, 0, 0, 0, 0) 
process4 = Processes(2, 1, 6, 128, 0, 0, 0, 0) 
process5 = Processes(4, 3, 8, 264, 0, 0, 0, 0) 
process6 = Processes(5, 2, 8, 264, 0, 0, 0, 0) 

Processes.all_processes = [process1, process2, process3, process4, process5, process6]

while len(Processes.all_processes) > 0 or Queues.count > 0:
  if (len(Processes.all_processes) > 0):
    Processes.processes_that_arrived = [process for process in Processes.all_processes if process.arrival_time <= cpu_total_quantums]
    Processes.all_processes = [process for process in Processes.all_processes if process.arrival_time > cpu_total_quantums]

  #Coloca na fila de prontos os processos que chegaram com base no cpu_total_quantums
  if len(Processes.processes_that_arrived) > 0:
    for process in Processes.processes_that_arrived:
      if not queues.add_process(process, True):
        print("Fila de processos está cheia!")
        break
    Processes.processes_that_arrived = []

  #Executado sempre que acaba o tempo de CPU de um processo (processing_time) ou quando não tem recursos ou quando não tem processos em execução
  if (processing_time <= 0):
    if (current_process_in_cpu):
      if (current_process_in_cpu.processing_time < current_process_in_cpu.total_time):
        queues.add_process(current_process_in_cpu, False)
      else:
        current_process_in_cpu.close_process()
        Queues.count -= 1

    current_process_in_cpu = queues.get_next_process()

    if (current_process_in_cpu):
      current_process_in_cpu.wait_time = 0

      #Caso o processo não tenha todos os recursos
      if (not current_process_in_cpu.get_all_resources()):
        queues.update_user_process_queue()
        processing_time = 0
        cpu_total_quantums += Processes.quantum
        continue

      current_process_in_cpu.get_process_status()
      first = True

      #Altera a fila ou a prioridade do processo e define o tempo de CPU (processing_time)
      if (current_process_in_cpu.queue == 0):
        processing_time = current_process_in_cpu.total_time
      else:
        #Tempo de processamento é o número da fila (1,2 ou 3) x quantum
        processing_time = current_process_in_cpu.queue * Processes.quantum 

        if (current_process_in_cpu.queue < 3):
          current_process_in_cpu.queue += 1 
        else:
          current_process_in_cpu.priority += 1

  if (current_process_in_cpu):
    current_process_in_cpu.processing_time += Processes.quantum
    
    if (processing_time - 1 <= 0):
      current_process_in_cpu.get_instructions_status(first, True, cpu_total_quantums + 1)
    else:
      current_process_in_cpu.get_instructions_status(first, False)
    
    first = False
      
  queues.update_user_process_queue()
  processing_time -= 1
  cpu_total_quantums += Processes.quantum
