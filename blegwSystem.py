import subprocess

def uptime():
    raw = subprocess.check_output('uptime').decode("utf8").replace(',', '')
    days = int(raw.split()[2])
    if 'min' in raw:
        hours = 0
        minutes = int(raw[4])
    else:
        hours, minutes = map(int, raw.split()[4].split(':'))
    #print(days, hours, minutes)
    totalsecs = ((days * 24 + hours) * 60 + minutes) * 60
    return days, hours, minutes, totalsecs


if __name__ == '__main__':
    av = uptime()
    print(av)