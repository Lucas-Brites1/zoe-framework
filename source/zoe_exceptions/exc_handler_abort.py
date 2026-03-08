from zoe_http.response import Response
class HandlerAbortException(Exception):
    def __init__(self, response: Response):
        self.response = response
