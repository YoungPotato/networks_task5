class Parser:
    def get_name(self, answer, start_pos, domains):
        domain = []
        stop = False
        while not stop:
            start_pos, domains, i, domain, stop = self\
                .find_domain_names(answer, start_pos, domains, 1, domain, stop)
        return self.format_name(domains)

    def find_domain_names(self, answer, start_pos, domains, counter, domain,
                          stop):
        domain_len = int(answer[start_pos:start_pos + 2], 16)
        if 64 > domain_len > 0:
            domain.append(self.take_standard_mark(domain_len, answer,
                                                  start_pos))
            j = start_pos + 2 + domain_len * 2
            if answer[j:j + 2] == "00":
                counter -= 1
                domains.append(domain)
                domain = []
                stop = True
            start_pos = start_pos + 2 + domain_len * 2
        elif domain_len >= 64:
            pos = (int(answer[start_pos:start_pos + 4], 16) - 49152) * 2
            while pos < start_pos - 2:
                domain_len = int(answer[pos:pos + 2], 16)
                a = self.take_standard_mark(domain_len, answer, pos)
                if a != "":
                    domain.append(a)
                else:
                    stop = True
                    break
                pos += domain_len * 2 + 2
            counter -= 1
            domains.append(domain)
            domain = []
            start_pos += 4
        else:
            start_pos += 2
        return start_pos, domains, counter, domain, stop

    @staticmethod
    def take_standard_mark(domain_len, answer, start_pos):
        domain = ""
        for i in range(domain_len * 2):
            domain += answer[start_pos + 2 + i]
        return domain

    @staticmethod
    def format_name(domains):
        results = []
        for d in domains:
            res = []
            for domain in d:
                pairs = [int(domain[i:i + 2], 16) for i in
                         range(0, len(domain), 2)]
                res.append("".join([chr(i) for i in pairs]))
            results.append(".".join(res))
        return results
