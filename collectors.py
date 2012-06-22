from subprocess import Popen, PIPE
import re

def uptime(*args):
    with open('/proc/uptime') as fh:
        uptime = int(float(fh.read().split(' ')[0]))
    return uptime

class hd:

    @staticmethod
    def __row_left(device):
        output = [l for l in Popen('df', stdout=PIPE).communicate()[0].splitlines() if l.startswith('/dev/%s' % device)][0]
        output = re.sub('\s+', ' ', output)
        return output.split(' ')

    @staticmethod
    def space_left(device, *args):
        return hd.__row_left(device)[3]

    @staticmethod
    def percentage_left(device, *args):
        return int(hd.__row_left(device)[4][:-1])


