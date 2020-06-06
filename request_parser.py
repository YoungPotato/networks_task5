from main_parser import Parser
from socket import *
import binascii
from answer_parser import AnswerParser
from time import time


class RequestParser:
    def __init__(self, storage):
        self.parser = Parser()
        self.storage = storage
        self.answer_parser = AnswerParser()

    def parse_request(self, request):
        if request is None:
            return None

        header = request[0:24]
        question = request[24:]

        name = self.parser.get_name(question, 0, [])[0]
        _type = question[-8:-4]
        if self.storage.get((name, _type)) is not None:
            answer, count = self.get_data_from_cache((name, _type))
            if answer == "":
                answer_on_request = self.make_udp_request(request)
                if answer_on_request is not None:
                    self.answer_parser.parse_answer(answer_on_request,
                                                    self.storage)
                return answer_on_request
            _id = header[0:4]
            flags = "8180"
            questions_count = header[8:12]
            answers_count = hex(count)[2:].rjust(4, '0')
            ns_count = header[16:20]
            ar_count = header[20:24]
            new_header = _id + flags + questions_count + answers_count + \
                         ns_count + ar_count
            return new_header + question + answer
        answer_on_request = self.make_udp_request(request)
        if answer_on_request is not None:
            self.answer_parser.parse_answer(answer_on_request, self.storage)
            return answer_on_request
        return ""

    def get_data_from_cache(self, key):
        data = self.storage.get(key)
        result = []
        count = 0
        for element in data:
            if element.death_time > round(time()):
                result.append(element.__str__())
                count += 1
        return "".join(result), count

    @staticmethod
    def make_udp_request(request):
        message = request.replace(" ", "").replace("\n", "")
        sock = socket(AF_INET, SOCK_DGRAM)
        address = "8.8.8.8", 53
        try:
            sock.sendto(binascii.unhexlify(message), address)
            response, _ = sock.recvfrom(4096)
        except TimeoutError:
            return None
        finally:
            sock.close()
        return binascii.hexlify(response).decode("utf-8")
