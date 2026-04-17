class TalkinError(Exception):
    """Base exception for the Talkin SDK."""


class AuthenticationError(TalkinError):
    """Raised when login or OTP authentication fails."""


class APIRequestError(TalkinError):
    """Raised when the Talkin API returns an error response."""

    def __init__(self, code, message: str):
        self.code = code
        self.message = message
        super().__init__(f"[{code}] {message}")


class CryptoError(TalkinError):
    """Raised when the crypto API returns an error or is unreachable."""


class NetworkError(TalkinError):
    """Raised when an HTTP request fails at the network level."""


class RateLimitError(TalkinError):
    """Raised when the crypto API rate limit is exceeded."""

    def __init__(self, plan: str = "unknown", limit: int = 0):
        self.plan  = plan
        self.limit = limit
        msg = f"Rate limit exceeded (plan={plan}, limit={limit}/min)" if limit else \
              "Crypto API rate limit exceeded"
        super().__init__(msg)
