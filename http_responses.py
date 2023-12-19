from string import Template

class Responses:
    def __call__(self) -> None:
        raise RuntimeError(f"Do not call {self.__name__} directly")

    def __init__(self) -> None:
        self.responses = {
            200: "OK",
            301: "Moved Permanently",
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            405: "Method Not Allowed",
            406: "Not Acceptable",
            408: "Request Timeout",
            409: "Conflict",
            410: "Gone",
            411: "Length Required",
            412: "Precondition Failed",
            413: "Payload Too Large",
            414: "URI Too Long",
            415: "Unsupported Media Type",
            000: "Unknown Status",
        }

    def __strnumeric(self, string: str) -> int:
        if isinstance(string, str) and string.isnumeric():
            return int(string)
        elif isinstance(string, int):
            return string
        else:
            return 000
        
    def get_response(self, code: str | int) -> str:
        code = self.__strnumeric(code)
        return self.responses[code]
    
    def get_response_header(self, code: str | int) -> str:
        code = self.__strnumeric(code)
        return f"HTTP/1.1 {code} {self.responses[code]}\r\n"

    def get_response_body(self, code: str | int) -> str:
        code = self.__strnumeric(code)

        template = open("responses/response.html.template", 'r')
        template_content = Template(template.read(-1))
        template.close()

        return template_content.substitute({"code": code, "code_text": self.responses[code]})

class Headers:
    def __call__(self):
        raise RuntimeError(f"Do not call {self.__name__} directly")

    