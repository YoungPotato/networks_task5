from record import *


class Storage:
    def __init__(self):
        self.cache = {}

    def get(self, key: tuple):
        return self.cache.get(key, None)

    def put(self, key: tuple, value: Record):
        if self.cache.get(key, None) is None:
            self.cache[key] = [value]
        else:
            self.cache[key].append(value)

    def keys(self):
        return list(self.cache.keys())
