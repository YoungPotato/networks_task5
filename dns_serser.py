from storage import Storage
import pickle
from request_parser import *


class Server:
    def __init__(self):
        self.cache_check_time = round(time())
        self.storage = Storage()

    def run(self):
        try:
            with open("cache", "rb") as file:
                self.storage.cache = pickle.load(file)
        except FileNotFoundError:
            self.storage.cache = {}
        self.check_cache()
        udp_socket = socket(AF_INET, SOCK_DGRAM)
        udp_socket.bind(('127.0.0.1', 53))
        request_parser = RequestParser(self.storage)
        while True:
            try:
                received, address = udp_socket.recvfrom(1024)
                request = binascii.hexlify(received).decode("utf-8")
                request = request_parser.parse_request(request)
                if request is not None:
                    udp_socket.sendto(binascii.unhexlify(request), address)
                self.check_cache()
            finally:
                self.change_cache()

    def check_cache(self):
        if round(time()) - self.cache_check_time > 60:
            for name, _type in self.storage.keys():
                for item in self.storage.get((name, _type)):
                    if not item.death_time > round(time()):
                        self.storage.get((name, _type)).remove(item)
            self.change_cache()

    def change_cache(self):
        with open("cache", "wb+") as file:
            pickle.dump(self.storage.cache, file)
