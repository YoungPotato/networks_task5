from time import time


class Record:
    def __init__(self, _type, ttl, data):
        self.name = "c00c"
        self._type = _type
        self.death_time = ttl + round(time())
        self.data = data
        self._class = "0001"

    def __str__(self):
        return self.name + \
               self._type + \
               self._class + \
               hex(self.death_time - round(time()))[2:].rjust(8, '0') + \
               self.data
