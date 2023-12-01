class RequestParser:

    def __init__(self) -> None:
        self.REQUEST_METHOD = None
        self.REQUEST_PATH = None
        self.REQUEST_HOST = None
        self.REQUEST_PORT = None
        self.REQUEST_HEADERS = None

    def parse_request(self, request: str) -> None:
        request_lines = request.strip().splitlines()

        self.REQUEST_METHOD = request_lines[0].split(' ')[0]
        self.REQUEST_PATH = request_lines[0].split(' ')[1]
        self.REQUEST_HOST = request_lines[1].split(':')[1]
        self.REQUEST_PORT = request_lines[1].split(':')[2]

        self.REQUEST_HEADERS = {}
        for header in request_lines[2:]:
            key, value = header.split(": ", 1)
            self.REQUEST_HEADERS[key] = value

    def parse_value_by_sep(self, value: str, include_key: False, key_separator='=', value_separator=',') -> list | dict | str:
        if include_key:
            if key_separator not in value:
                raise ValueError("Key separator not found in value")
            else:
                values = {}
                if value.count(key_separator) > 1:
                    for value in value.split(value_separator):
                        values[value.split(key_separator)[0].strip()] = value.split(key_separator)[1].strip()
                    return values
                else:
                    return {value.split(key_separator)[0].strip(): value.split(key_separator)[1].strip()}
        else:
            values = []
            if value.count(value_separator) > 0:
                for item in value.split(value_separator):
                    values.append(item.strip())
                return values
            else:
                return value.strip()

test_request = """GET / HTTP/1.1
Host: 127.0.0.1:8080
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
Accept-Language: en-GB,cy;q=0.7,en;q=0.3
Accept-Encoding: gzip, deflate, br
DNT: 1
Connection: keep-alive
Cookie: csrftoken=zAvYiLq2T8g8vAkDQw630ES3ayA13BCc, sessionid=1363659534.1632269825.1.163
Upgrade-Insecure-Requests: 1
Sec-Fetch-Dest: document
Sec-Fetch-Mode: navigate
Sec-Fetch-Site: none
Sec-Fetch-User: ?1"""

rp = RequestParser()
rp.parse_request(test_request)
print(rp.REQUEST_HEADERS['Connection'])
print(rp.parse_value_by_sep(rp.REQUEST_HEADERS['Cookie'], True, '='))