from enum import Enum

class HttpMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"

    @staticmethod
    def str_to_method(method_str: str) -> "HttpMethod":  
        try:
            return HttpMethod(value=method_str)
        except ValueError:
            raise ValueError("f'{method_str}' is not a valid HTTP method")