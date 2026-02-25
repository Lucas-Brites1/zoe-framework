import base64

class Auth:
    def __init__(self: "Auth", authorization_header: str | None) -> None:
        self.__raw = authorization_header

    @property
    def raw(self: "Auth") -> str | None:
        return self.__raw

    @property
    def bearer_token(self: "Auth") -> str | None:
        """Extract bearer token from request auth header"""
        bearer_prefix: str = "Bearer "
        if self.__raw and self.__raw.startswith(bearer_prefix):
            return self.__raw.removeprefix(bearer_prefix)
        return None

    @property
    def basic_credentials(self: "Auth") -> tuple[str, str] | None:
        """Extract basic credentials (user & password) from request authorization header"""
        basic_prefix: str = "Basic "
        if self.__raw and self.__raw.startswith(basic_prefix):
            try:
                decoded_basic: str = base64.b64decode(
                    self.__raw.removeprefix(basic_prefix)
                    ).decode("utf-8")

                username, _, password = decoded_basic.partition(":")
                return (username, password)
            except Exception as exc:
                raise exc
        return None
            
    @property
    def api_key(self: "Auth") -> str | None:
        api_key_prefix: str = "ApiKey "
        if self.__raw and self.__raw.startswith(api_key_prefix):
            return self.__raw.removeprefix(api_key_prefix)
        return None

    @property
    def scheme(self: "Auth") -> str | None:
        """Returns the auth scheme - 'Bearer', 'Basic', 'ApiKey', etc..."""
        if self.__raw:
            return self.__raw.split(" ")[0]
        return None
    
    def __bool__(self: "Auth") -> bool:
        return self.__raw is not None