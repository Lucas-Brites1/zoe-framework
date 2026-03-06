from zoe_exceptions.http_exceptions.exc_http_base import ZoeHttpException
from zoe_exceptions.exc_non_http_internal_error import ZoeNonHttpError
from zoe_http.code import HttpCode
from zoe_http.request import Request
import sys
import traceback
from datetime import datetime

class InternalServerException(ZoeHttpException):
    def __init__(
        self: "InternalServerException", 
        detail: str = "An unexpected error occurred."
    ) -> None:
        super().__init__(
            message=detail,
            status_code=HttpCode.INTERNAL_SERVER_ERROR
        )
    
    @classmethod
    def from_non_http_error(
        cls, 
        error: ZoeNonHttpError, 
        request: Request | None = None,
        show_in_terminal: bool = True
    ) -> "InternalServerException":
        if show_in_terminal:
            cls._log_internal_error(error, request)
        
        return cls(detail="Internal server error. Check server logs for details.")
    
    @classmethod
    def from_unexpected_error(
        cls, 
        error: Exception, 
        request: Request | None = None,
        show_in_terminal: bool = True
    ) -> "InternalServerException":
        if show_in_terminal:
            cls._log_unexpected_error(error, request)
        
        return cls(detail="Unexpected error occurred. Check server logs.")
    
    @staticmethod
    def _log_internal_error(error: ZoeNonHttpError, request: Request | None) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        RED = "\033[91m"
        YELLOW = "\033[93m"
        RESET = "\033[0m"
        BOLD = "\033[1m"
        
        print(f"\n{RED}{BOLD}{'='*70}", file=sys.stderr)
        print(f"INTERNAL ERROR - {timestamp}", file=sys.stderr)
        print(f"{'='*70}{RESET}", file=sys.stderr)
        
        if request:
            print(f"{YELLOW}Request: {request.method.value} {request.route}{RESET}", file=sys.stderr)
            print(f"{YELLOW}Client IP: {request.client_ip}{RESET}", file=sys.stderr)
            print(f"{RED}{'-'*70}{RESET}", file=sys.stderr)
        
        print(error.exception_message, file=sys.stderr)
        print(f"{RED}{'='*70}{RESET}\n", file=sys.stderr)
    
    @staticmethod
    def _log_unexpected_error(error: Exception, request: Request | None) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        RED = "\033[91m"
        YELLOW = "\033[93m"
        RESET = "\033[0m"
        BOLD = "\033[1m"
        
        print(f"UNEXPECTED ERROR - {timestamp}\n", file=sys.stderr)
        
        if request:
            print(f"{YELLOW}Request: {request.method.value} {request.route}{RESET}", file=sys.stderr)
            print(f"{YELLOW}Client IP: {request.client_ip}{RESET}\n", file=sys.stderr)
        
        print(f"{RED}Error Type: {type(error).__name__}{RESET}", file=sys.stderr)
        print(f"{RED}Error Message: {str(error)}{RESET}", file=sys.stderr)
        print(f"{RED}{'-'*70}{RESET}", file=sys.stderr)
        
        traceback.print_exc(file=sys.stderr)
        