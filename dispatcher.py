import sys
from processes_module import Processes
from queues_module import Queues
from files_module import FileSystem
from memory_module import MemoryManager
from resources_module import ResourcesManager

if len(sys.argv) != 3:
  sys.exit(1)

files_path = sys.argv[1]
processes_path = sys.argv[2]

def ler_processos(path):
  processos = []
  with open(path) as f:
    for linha in f:
      if not linha.strip():
        continue
      valores = [int(x.strip()) for x in linha.strip().split(',')]
      p = Processes(*valores)
      processos.append(p)
  return processos

def ler_files(path):
  with open(path) as f:
    linhas = [l.strip() for l in f if l.strip()]
  total_blocos = int(linhas[0])
  qtd_existentes = int(linhas[1])
  arquivos_existentes = []
  for i in range(qtd_existentes):
    nome, start, size = [x.strip() for x in linhas[2+i].split(',')]
    arquivos_existentes.append((nome, int(start), int(size)))
  operacoes = []
  for l in linhas[2+qtd_existentes:]:
    partes = [x.strip() for x in l.split(',')]
    if partes[1] == '0':
      pid, cod, nome, size = int(partes[0]), int(partes[1]), partes[2], int(partes[3])
      operacoes.append({'pid': pid, 'op': 'create', 'nome': nome, 'size': size})
    elif partes[1] == '1':
      pid, cod, nome = int(partes[0]), int(partes[1]), partes[2]
      operacoes.append({'pid': pid, 'op': 'delete', 'nome': nome})
  return total_blocos, arquivos_existentes, operacoes

Processes.all_processes = ler_processos(processes_path)

queues = Queues()
memory_manager = MemoryManager()
resource_manager = ResourcesManager()

total_blocos, arquivos_existentes, operacoes_arquivo = ler_files(files_path)
filesystem = FileSystem(total_blocos)
filesystem.load_existing_files(arquivos_existentes)

pid_to_process = {}
for p in Processes.all_processes:
  pid_to_process[p.pid] = p

cpu_total_quantums = 0
processing_time = 0
current_process_in_cpu = False
first = False
queues = Queues()

while len(Processes.all_processes) > 0 or Queues.count > 0:
  if len(Processes.all_processes) > 0:
    Processes.processes_that_arrived = [process for process in Processes.all_processes if process.arrival_time <= cpu_total_quantums]
    Processes.all_processes = [process for process in Processes.all_processes if process.arrival_time > cpu_total_quantums]

  if len(Processes.processes_that_arrived) > 0:
    for process in Processes.processes_that_arrived:
      offset = memory_manager.allocate(process)
      if offset == -1:
        print(f"[{cpu_total_quantums}] Falha ao alocar memória para P{process.pid}")
        continue  # não adiciona à fila de prontos
      process.offset = offset

      if not queues.add_process(process, True):
        print("Fila de processos está cheia!")
        break
    Processes.processes_that_arrived = []

  if processing_time <= 0:
    if current_process_in_cpu:
      if current_process_in_cpu.processing_time < current_process_in_cpu.total_time:
        queues.add_process(current_process_in_cpu, False)
      else:
        current_process_in_cpu.close_process(memory_manager, resource_manager, queues)

    current_process_in_cpu = queues.get_next_process()

    if current_process_in_cpu:
      print("\ndispatcher =>  ")
      print(f"    PID: {current_process_in_cpu.pid}")
      print(f"    offset: {current_process_in_cpu.offset}")
      print(f"    blocks: {current_process_in_cpu.memory_blocks}")
      print(f"    priority: {current_process_in_cpu.priority}")
      print(f"    time: {current_process_in_cpu.total_time}")
      print(f"    printers: {current_process_in_cpu.printer}")
      print(f"    scanners: {current_process_in_cpu.scanner}")
      print(f"    modems: {current_process_in_cpu.modem}")
      print(f"    drives: {current_process_in_cpu.disk}")

      current_process_in_cpu.wait_time = 0

      #Caso o processo não tenha todos os recursos
      if (not current_process_in_cpu.has_resources and not current_process_in_cpu.get_all_resources(queues, resource_manager)):
        queues.update_user_process_queue()
        processing_time = 0
        cpu_total_quantums += Processes.quantum
        continue

      # current_process_in_cpu.get_process_status()
      first = True

      if current_process_in_cpu.queue == 0:
        processing_time = current_process_in_cpu.total_time
      else:
        if (current_process_in_cpu.total_time - current_process_in_cpu.processing_time < current_process_in_cpu.queue * Processes.quantum):
          processing_time = current_process_in_cpu.total_time - current_process_in_cpu.processing_time
        else:
          processing_time = current_process_in_cpu.queue * Processes.quantum
        if current_process_in_cpu.queue < 3:
          current_process_in_cpu.queue += 1
        else:
          current_process_in_cpu.priority += 1

  if current_process_in_cpu:
    current_process_in_cpu.processing_time += Processes.quantum

    if (processing_time - 1 <= 0):
      current_process_in_cpu.get_instructions_status(first, True, cpu_total_quantums + 1)
    else:
      current_process_in_cpu.get_instructions_status(first, False)
    first = False

  queues.update_user_process_queue()
  processing_time -= 1
  cpu_total_quantums += Processes.quantum

def blocos_humanos(bloco):
    inicio, fim = bloco
    if fim-inicio == 0:
        return f"{inicio}"
    elif fim-inicio == 1:
        return f"{inicio} e {fim}"
    else:
        nums = [str(i) for i in range(inicio, fim)]
        return ', '.join(nums) + f" e {fim}"

print("\nSistema de arquivos =>\n")
for idx, op in enumerate(operacoes_arquivo):
    pid = op['pid']
    process = pid_to_process.get(pid)
    is_real_time = process and process.priority == 0

    if op['op'] == 'create':
        if process is None:
            print(f"Operação {idx+1} => Falha\nO processo {pid} não existe.\n")
        else:
            success, bloco = filesystem.create_file(op['nome'], op['size'], pid)
            if success:
                if bloco:
                    print(f"Operação {idx+1} => Sucesso\nO processo {pid} criou o arquivo {op['nome']} (blocos {blocos_humanos(bloco)}).\n")
                else:
                    print(f"Operação {idx+1} => Sucesso\nO processo {pid} criou o arquivo {op['nome']}.\n")
            else:
                print(f"Operação {idx+1} => Falha\nO processo {pid} não pode criar o arquivo {op['nome']} (falta de espaço).\n")
    elif op['op'] == 'delete':
        if process is None:
            print(f"Operação {idx+1} => Falha\nO processo {pid} não existe.\n")
        else:
            deleted = filesystem.delete_file(op['nome'], pid, is_real_time)
            if deleted:
                print(f"Operação {idx+1} => Sucesso\nO processo {pid} deletou o arquivo {op['nome']}.\n")
            else:
                if op['nome'] not in filesystem.files:
                    print(f"Operação {idx+1} => Falha\nO processo {pid} não pode deletar o arquivo {op['nome']} porque ele não existe.\n")
                else:
                    print(f"Operação {idx+1} => Falha\nO processo {pid} não pode deletar o arquivo {op['nome']}.\n")

filesystem.print_disk_map()
