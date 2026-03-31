from zoe_jwt.jwt_exceptions import (
    InvalidTokenError,
    InvalidSignatureError,
    ExpiredTokenError,
    InvalidAlgorithmError,
    TokenNotYetValidError,
    MissingIssuerError, UntrustedIssuerError,
    UnauthorizedAudienceError
)

from zoe_schema.schema_generators.date_generator import Date, DateFormat
from zoe_schema.schema_generators.uuid_generator import UUID
from zoe_jwt.token_validator import TokenValidator
from typing import Callable, Any, Optional
from hashlib import sha256
from json import dumps, loads
import hmac
import base64


def b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")

def b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


ValueValidator = Callable[[Any], bool]

class JWT_Claim:
    def __init__(self,
                 key: str,
                 value: Any,
                 value_validator: Optional[ValueValidator] = None,
                ):
        self._key = key
        self._value = value
        self._validator = value_validator

    def validate(self, payload: dict):
        if self._key not in payload:
            raise InvalidTokenError(f"Missing claim: {self._key}")

        if self._validator is not None:
            if not self._validator(payload[self._key]):
                raise InvalidTokenError(f"Claim '{self._key}' not pass after validation call")

        elif payload[self._key] != self._value:
            raise InvalidTokenError(f"Invalid claim '{self._key}'")

    @staticmethod
    def from_claims(claims: list["JWT_Claim"]) -> dict:
        claims_dict = {}
        for claim in claims:
            claims_dict[claim._key] = claim._value

        return claims_dict

class JWT_HS256(TokenValidator):
    def __init__(
        self,
        secret: str,
        issued_by: str,
        expires_min: int,
        claims: list[JWT_Claim] | None = None,
        audience: list[str] | None = None
    ) -> None:
        self._secret: str = secret
        self._expires_min: int = expires_min
        self._issued_by: str = issued_by
        self._audience: list[str] | None = audience
        self._claims: list[JWT_Claim] = claims or []

    def __build_payload(self, payload: dict) -> tuple[dict, dict]:
        header = {
            "alg": "HS256",
            "typ": "JWT",
        }

        date = Date.Now(as_=DateFormat.UNIX_TIMESTAMP)
        formatted_now = date.generate()

        all_claims: dict = JWT_Claim.from_claims(self._claims)
        full_payload = {
            **all_claims,
            **payload,
            "iat": formatted_now,
            "iss": self._issued_by,
            **( {"aud": self._audience} if self._audience is not None else {} )
        }

        if "exp" not in full_payload:
            full_payload["exp"] = Date.After(
                minutes=self._expires_min,
                as_=DateFormat.UNIX_TIMESTAMP,
                from_datetime=date.now
            ).generate()

        if "jti" not in full_payload:
            full_payload["jti"] = UUID().generate()

        return header, full_payload

    def _validate_header(self, header: dict) -> None:
        if header.get("alg") != "HS256":
            raise InvalidAlgorithmError(
                f"Expected HS256, got {header.get('alg')}"
            )

        if header.get("typ") != "JWT":
            raise InvalidTokenError(
                f"Invalid typ: expected JWT, got {header.get('typ')}"
            )

    def encode(self, payload: dict | None = None) -> str:
        header, full_payload = self.__build_payload(payload or {})

        header_b64 = b64url_encode(
            dumps(header, separators=(",", ":")).encode("utf-8")
        )

        payload_b64 = b64url_encode(
            dumps(full_payload, separators=(",", ":")).encode("utf-8")
        )

        signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")

        signature = hmac.new(
            self._secret.encode("utf-8"),
            signing_input,
            sha256,
        ).digest()

        signature_b64 = b64url_encode(signature)

        return f"{header_b64}.{payload_b64}.{signature_b64}"

    def decode(self, token: str) -> dict:
        parts = token.split(".")
        if len(parts) != 3:
            raise InvalidTokenError("JWT must have 3 parts")

        header_b64, payload_b64, signature_b64 = parts

        try:
            header = loads(b64url_decode(header_b64).decode("utf-8"))
        except Exception:
            raise InvalidTokenError("Invalid header encoding")

        self._validate_header(header)

        signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")

        expected_signature = hmac.new(
            self._secret.encode("utf-8"),
            signing_input,
            sha256,
        ).digest()

        expected_b64 = b64url_encode(expected_signature)

        if not hmac.compare_digest(signature_b64, expected_b64):
            raise InvalidSignatureError("Invalid token")

        try:
            payload = loads(b64url_decode(payload_b64).decode("utf-8"))  # FIX: faltava .decode("utf-8")
        except Exception:
            raise InvalidTokenError("Invalid payload encoding")

        iss: str | None = payload.get("iss", None)

        if iss is None:
            raise MissingIssuerError()
        elif iss != self._issued_by:
            raise UntrustedIssuerError()

        if self._audience is not None:
            aud = payload.get("aud", [])

            # FIX: normaliza aud para lista (JWT spec permite string ou lista)
            if isinstance(aud, str):
                aud = [aud]

            if not any(service in self._audience for service in aud):
                raise UnauthorizedAudienceError()

        return payload

    def validate(self, token: str) -> dict:
        payload = self.decode(token)

        now = Date.Now(as_=DateFormat.UNIX_TIMESTAMP).generate()

        if "exp" not in payload:
            raise InvalidTokenError("Missing exp claim")

        if payload["exp"] < now:
            raise ExpiredTokenError(f"Token expired at {payload['exp']}")

        if "nbf" in payload and payload["nbf"] > now:
            raise TokenNotYetValidError(
                f"Token valid only after {payload['nbf']}"
            )

        if "iat" in payload and payload["iat"] > now:
            raise InvalidTokenError("Token issued in the future")

        for claim in self._claims:
            claim.validate(payload)

        return payload
