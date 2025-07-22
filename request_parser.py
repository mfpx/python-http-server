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

            request_line_parts = request_lines[0].split()
            if len(request_line_parts) < 3:
                raise ValueError("Invalid request line")
            self.REQUEST_METHOD = request_line_parts[0]
            self.REQUEST_PATH = request_line_parts[1]
            self.REQUEST_FILE = self.REQUEST_PATH.split('/')[-1].split('?')[0]

            self.REQUEST_HEADERS = {}
            for header in request_lines[1:]:
                if header == '':
                    continue
                key, _, value = header.partition(':')
                if not _:
                    raise ValueError("Unable to parse header")
                self.REQUEST_HEADERS[key] = value.strip()

            host_header = self.REQUEST_HEADERS.get('Host', '')
            host, port = self._parse_host(host_header)
            self.REQUEST_HOST = host
            self.REQUEST_PORT = port
        except Exception:
            raise ValueError("Unable to parse request")

    def _parse_host(self, host_header: str) -> tuple[str, int]:
        """Parse host and port from Host header"""
        if not host_header:
            return '', 80
        if host_header.startswith('['):
            host_part, sep, port_part = host_header.rpartition(']')
            host = host_part + ']' if sep else host_header
            remainder = port_part
        else:
            host, sep, remainder = host_header.rpartition(':')
            if not sep:
                host = host_header
                remainder = ''

        if remainder.startswith(':'):
            remainder = remainder[1:]

        if remainder.isdigit():
            port = int(remainder)
            if 0 <= port <= 65535:
                return host.strip('[]'), port
            else:
                raise ValueError(f"Port number out of range: {remainder}")
        return host.strip('[]'), 80

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
