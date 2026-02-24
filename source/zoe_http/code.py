from enum import Enum

class HttpCode(Enum):
    OK = (200, "OK")
    CREATED = (201, "Created")
    NO_CONTENT = (204, "No Content")
    BAD_REQUEST = (400, "Bad Request")
    UNAUTHORIZED = (401, "Unauthorized")
    FORBIDDEN = (403, "Forbidden")
    NOT_FOUND = (404, "Not Found")
    UNPROCESSABLE_ENTITY = (422, "Unprocessable Entity")
    TOO_MANY_REQUESTS = (429, "Too Many Requests")
    INTERNAL_SERVER_ERROR = (500, "Internal Server Error")

    @property
    def code(self) -> int:
        return self.value[0]

    @property
    def message(self) -> str:
        return self.value[1]