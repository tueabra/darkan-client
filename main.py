from ConfigParser import ConfigParser
from types import StringType
from time import sleep

import zmq

import collectors

# Ideas:
#  Autoreload on config file update
#  Use gevent to run collectors concurrently

CONFIG_FILE = 'darkan.ini'

class DarkanClient(object):

    def __init__(self):
        self.hostname = None
        self.interval = None
        self.server   = None
        self.key      = None

        self.zmq_context = zmq.Context()
        self.zmq_socket = None

        self.read_config()

        self.connect()

    def connect(self):
        self.zmq_socket = self.zmq_context.socket(zmq.REQ)
        self.zmq_socket.connect("tcp://%s:12345" % self.server)

    def read_config(self):
        self.cfp = ConfigParser()
        self.cfp.read(CONFIG_FILE)

        self.hostname = self.cfp.get('darkan', 'hostname')
        self.interval = int(self.cfp.get('darkan', 'interval'))
        self.server   = self.cfp.get('darkan', 'server')
        self.key      = self.cfp.get('darkan', 'key')

    def collect(self):
        values = []
        for fullname,args in self.cfp.items('collectors'):

            name = fullname

            subname = None
            if '.' in name:
                name, subname = name.split('.')

            for arg in args.split(','):

                if hasattr(collectors, name):
                    func = getattr(collectors, name)
                    if subname:
                        func = getattr(func, subname)
                    val = func(arg)
                else:
                    val = ''

                if isinstance(val, StringType) and val.isdigit():
                    val = int(val)

                values.append({
                    'key': fullname,
                    'arg': arg,
                    'val': val,
                })

        return values

    def send_package(self, package):
        print package
        self.zmq_socket.send_json(package)
        res = self.zmq_socket.recv_json()
        if not res['status'] == 'OK':
            print "zmq error:", res['error']

    def run_loop(self):

        while True:
            values = self.collect()
            pack = {
                'hostname': self.hostname,
                'key': self.key,
                'interval': self.interval,
                'values': values,
            }
            self.send_package(pack)
            sleep(self.interval)

if __name__ == '__main__':
    client = DarkanClient()
    client.run_loop()
