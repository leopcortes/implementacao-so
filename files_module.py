class FileEntry:
  def __init__(self, name, start_block, size, creator_pid):
    self.name = name
    self.start_block = start_block
    self.size = size
    self.creator_pid = creator_pid

class FileSystem:
  def __init__(self, total_blocks):
    self.total_blocks = total_blocks
    self.disk = [None] * total_blocks
    self.files = {}

  def load_existing_files(self, file_descriptions):
    for desc in file_descriptions:
      name, start, size = desc
      start, size = int(start), int(size)
      self.files[name] = FileEntry(name, start, size, creator_pid=None)
      for i in range(start, start + size):
        self.disk[i] = name

  def create_file(self, filename, size, pid):
    size = int(size)
    start = self._find_contiguous_space(size)
    if start is None:
      return False, None
    for i in range(start, start + size):
      self.disk[i] = filename
    self.files[filename] = FileEntry(filename, start, size, creator_pid=pid)
    return True, (start, start+size-1)

  def _find_contiguous_space(self, size):
    free = 0
    for i in range(self.total_blocks):
      if self.disk[i] is None:
        free += 1
        if free == size:
          return i - size + 1
      else:
        free = 0
    return None

  def delete_file(self, filename, pid, is_real_time_process):
    entry = self.files.get(filename)
    if entry is None:
      return False
    if not is_real_time_process and entry.creator_pid != pid:
      return False
    for i in range(entry.start_block, entry.start_block + entry.size):
      self.disk[i] = None
    del self.files[filename]
    return True

  def print_disk_map(self):
    print("\nMapa de ocupação do disco:")
    result = []
    for block in self.disk:
      result.append(block if block else '0')
    print(' '.join(result))
