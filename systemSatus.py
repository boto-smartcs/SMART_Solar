import psutil

def cpu():
    return str(psutil.cpu_percent()) + ' %'

def memory():
    memory = psutil.virtual_memory()
    # Divide from Bytes -> KB -> MB
    available = str(round(memory.available / 1024.0 / 1024.0, 1)) + 'MB free'
    total = str(round(memory.total/1024.0/1024.0,1)) + 'Mb total'
    return available, total, (str(memory.percent) + ' %')


def disk():
    disk = psutil.disk_usage('/')
    disk_used = 100 - disk.percent
    # Divide from Bytes -> KB -> MB -> GB
    free = str(round(disk.free/1024.0/1024.0/1024.0,1)) + 'GB free'
    total = str(round(disk.total/1024.0/1024.0/1024.0,1)) + 'GB total'
    return free, total, str(disk.percent) + ' %', str(disk_used) + ' %'
#print(str(free) + 'GB free / ' + str(total) + 'GB total ( ' + str(disk.percent) + '% )')

if __name__ == '__main__':
    av, tot, mem, disk_used  = disk()
    print(mem,disk_used)