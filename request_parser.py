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

            self.REQUEST_METHOD = request_lines[0].split(' ')[0]
            self.REQUEST_PATH = request_lines[0].split(' ')[1]
            self.REQUEST_FILE = self.REQUEST_PATH.split('/')[-1].split('?')[0]
            self.REQUEST_HOST = request_lines[1].split(':')[1]
            try:
                # Check if the port is present
                self.REQUEST_PORT = request_lines[1].split(':')[2]
            except IndexError:
                # Implied port
                self.REQUEST_PORT = 80

            self.REQUEST_HEADERS = {}
            for header in request_lines[2:]:
                key, value = header.split(": ", 1)
                self.REQUEST_HEADERS[key] = value
        except:
            raise ValueError("Unable to parse request")

    @staticmethod
    def parse_value_by_sep(value: str, include_key: False, key_separator='=', value_separator=',') -> list | dict | str:
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
