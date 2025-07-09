from processes_module import Processes

class Queues:
  first_wait_time_limit = 3 * Processes.quantum
  second_wait_time_limit = 4 * Processes.quantum
  third_wait_time_limit = 5 * Processes.quantum
  real_time = []
  user_first_priority = []
  user_second_priority = []
  user_third_priority = []
  count = 0 #quantidade de processos no sistema

  def add_process(self, process, new_process):
    if not isinstance(process, Processes) or Queues.count >= 1000:
      return False
    
    if (process.queue == 0):
      Queues.real_time.append(process)
    elif (process.queue == 1):
      Queues.user_first_priority.append(process)
      Queues.user_first_priority.sort(key=lambda process: (process.priority, process.arrival_time))
    elif (process.queue == 2):
      Queues.user_second_priority.append(process)
      Queues.user_second_priority.sort(key=lambda process: (process.priority, process.arrival_time))
    else:
      Queues.user_third_priority.append(process)
      Queues.user_third_priority.sort(key=lambda process: (process.priority, process.arrival_time))

    if (new_process):
      Queues.count += 1

    return True

  def get_next_process(self):
      if len(Queues.real_time) > 0:
        return Queues.real_time.pop(0)
      
      elif len(Queues.user_first_priority) > 0:
        return Queues.user_first_priority.pop(0)
      
      elif len(Queues.user_second_priority) > 0:
        return Queues.user_second_priority.pop(0)
      
      elif len(Queues.user_third_priority) > 0:
        return Queues.user_third_priority.pop(0)

      else:
        return False
  
  def update_user_process_queue(self):
    #Primeira fila
    for process in Queues.user_first_priority:
      if process.wait_time >= Queues.first_wait_time_limit:
        if process.priority == 0:
          process.wait_time = 0
        else:
          process.priority -= 1
          process.wait_time = 0
      else:
        process.wait_time += Processes.quantum

    #Segunda fila
    for process in Queues.user_second_priority:
      if process.wait_time >= Queues.second_wait_time_limit:
        if process.priority == 0:
          Queues.user_second_priority.remove(process)

          if (len(Queues.user_first_priority) > 0):
            last_priority = max(Queues.user_first_priority, key=lambda process: process.priority).priority
          else: 
            last_priority = 0

          process.priority = last_priority + 1
          process.wait_time = 0
          process.queue = 1

          Queues.user_first_priority.append(process)
        else:
          process.priority -= 1
          process.wait_time = 0
      else:
        process.wait_time += Processes.quantum

    #Terceira fila
    for process in Queues.user_third_priority:
      if process.wait_time >= Queues.third_wait_time_limit:
        if process.priority == 0:
          Queues.user_third_priority.remove(process)

          if (len(Queues.user_second_priority) > 0):
            last_priority = max(Queues.user_second_priority, key=lambda process: process.priority).priority
          else: 
            last_priority = 0
          process.priority = last_priority + 1
          process.wait_time = 0
          process.queue = 2

          Queues.user_second_priority.append(process)
        else:
          process.priority -= 1
          process.wait_time = 0
      else:
        process.wait_time += Processes.quantum

    Queues.user_first_priority.sort(key=lambda process: (process.priority, process.arrival_time))
    Queues.user_second_priority.sort(key=lambda process: (process.priority, process.arrival_time))
    Queues.user_third_priority.sort(key=lambda process: (process.priority, process.arrival_time))

  def remove_process(self):
    Queues.count -= 1