import logging


class RequestParser:
    """Deals with parsing requests"""

    def __init__(self) -> None:
        self.REQUEST_METHOD = None
        self.REQUEST_PATH = None
        self.REQUEST_FILE = None
        self.REQUEST_HOST = None
        self.REQUEST_PORT = None
        self.REQUEST_HEADERS = None

    def parse_request(self, request: str) -> None:
        """Parse the request and store the relevant information"""
        try:
            request_lines = request.strip().splitlines()
        except Exception as e:
            logging.error(f"Error processing request: {e}")
            return

        if not request_lines:
            logging.info("Empty request received")
            return

        first_line = request_lines[0].split()
        if len(first_line) < 3:
            logging.info("Malformed request line")
            return

        self.REQUEST_METHOD = first_line[0]
        self.REQUEST_PATH = first_line[1]
        self.REQUEST_FILE = self.REQUEST_PATH.split('/')[-1].split('?')[0]

        self.REQUEST_HEADERS = {}
        host_value = None
        for header in request_lines[1:]:
            if not header:
                continue
            if ':' not in header:
                logging.info(f"Malformed header line: {header}")
                continue
            key, value = header.split(':', 1)
            value = value.lstrip()
            if key.lower() == 'host':
                host_value = value
            else:
                self.REQUEST_HEADERS[key] = value

        if host_value is not None:
            if ':' in host_value:
                host, port = host_value.split(':', 1)
                self.REQUEST_HOST = host.strip()
                self.REQUEST_PORT = port.strip()
            else:
                self.REQUEST_HOST = host_value.strip()
                self.REQUEST_PORT = 80
        else:
            logging.info("Host header missing")
            self.REQUEST_PORT = 80

    @staticmethod
    def parse_value_by_sep(value: str, include_key: bool = False, key_separator='=', value_separator=',') -> list | dict | str:
        """Parse a value by a given separator"""
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

class HTTP(RequestParser):
    """Contains the HTTP request information"""

    def __init__(self, request: str) -> None:
        super().__init__()
        self.parse_request(request)

    @property
    def get(self) -> dict:
        """Return the GET parameters"""
        if '?' in self.REQUEST_PATH:
            return self.parse_value_by_sep(self.REQUEST_PATH.split('?')[1], True, value_separator='&')
        else:
            return {}
