from main_parser import Parser
from record import Record


class AnswerParser:
    def __init__(self):
        self.parser = Parser()

    def parse_answer(self, answer, storage):
        questions = int(answer[8:12], 16)
        answer_rrs = int(answer[12:16], 16)
        authority_rrs = int(answer[16:20], 16)
        additional_rrs = int(answer[20:24], 16)
        start_pos = 24
        domains = []
        i = questions
        domain = []
        while i > 0:
            start_pos, domains, i, domain, _ = self.parser\
                .find_domain_names(answer, start_pos, domains, i, domain, True)
        stop = False
        domains = []
        j = answer_rrs
        start_pos += 14

        answers = []
        while j > 0:
            pos = (int(answer[start_pos - 4:start_pos], 16) - 49152) * 2
            while not stop:
                pos, domains, i, domain, stop = self.parser\
                    .find_domain_names(answer, pos,domains, 1, domain, stop)
            name = self.parser.format_name(domains)[0]
            _type = answer[start_pos:start_pos + 4]
            ttl = int(answer[start_pos + 12:start_pos + 16], 16)
            rd_length = int(answer[start_pos + 16:start_pos + 20], 16) * 2
            data = answer[start_pos + 16:start_pos + 20 + rd_length]
            answ = Record(_type, ttl, data)
            storage.put((name, _type), answ)
            answers.append(Record(_type, ttl, data))
            start_pos += 24 + rd_length
            j -= 1
        j = authority_rrs
        stop = False
        domains = []

        while j > 0:
            pos = (int(answer[start_pos - 4:start_pos], 16) - 49152) * 2
            while not stop:
                pos, domains, i, domain, stop = self.parser\
                    .find_domain_names(answer, pos, domains, 1, domain, stop)

            name = self.parser.format_name(domains)[0]
            _type = answer[start_pos:start_pos + 4]
            ttl = int(answer[start_pos + 12:start_pos + 16], 16)
            data_length = int(answer[start_pos + 16:start_pos + 20], 16) * 2
            data = answer[start_pos + 16:start_pos + 20 + data_length]
            ans = Record(_type, ttl, data)
            storage.put((name, _type), ans)
            j -= 1

            start_pos += 24 + data_length
        j = additional_rrs
        while j > 0:
            result, start_pos = self.find_mailbox_or_name_server(answer,
                                                            start_pos - 4)
            name = self.parser.format_name([result[0]])[0]
            _type = answer[start_pos:start_pos + 4]
            ttl = int(answer[start_pos + 8:start_pos + 16], 16)
            data_length = int(answer[start_pos + 16:start_pos + 20], 16) * 2
            data = answer[start_pos + 16:start_pos + 20 + data_length]
            ar = Record(_type, ttl, data)
            storage.put((name, _type), ar)
            start_pos += 24 + data_length
            j -= 1

    def find_mailbox_or_name_server(self, answer, start_pos):
        result = []
        domain = []
        domains = []
        stop = False
        while True:
            domain_len = int(answer[start_pos:start_pos + 2], 16)
            if 64 > domain_len > 0:
                domain.append(
                    self.parser.take_standard_mark(domain_len, answer,
                                                   start_pos))
                j = start_pos + 2 + domain_len * 2
                result.append(domain)
                start_pos = start_pos + 2 + domain_len * 2
                if answer[j:j + 2] == "00":
                    start_pos += 2
                    break
            elif domain_len >= 64:
                pos = (int(answer[start_pos:start_pos + 4], 16) - 49152) * 2
                while answer[pos:pos + 2] != "00" and not stop:
                    pos, domains, _, domain, stop = self.parser\
                        .find_domain_names(answer, pos, domains, 1, domain,
                                           stop)
                for d in domains:
                    result.append(d)
                start_pos += 4
                break
        return result, start_pos
