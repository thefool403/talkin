import logging
from typing import Any, Dict, List

from ..http.session import TalkinSession
from ..exceptions   import AuthenticationError

log = logging.getLogger(__name__)


def _ok(res: Dict[str, Any]) -> bool:
    return res.get("code") in (0, "0", 200, "200", "ok", "OK")

def _err(res: Dict[str, Any]) -> str:
    for k in ("message", "msg", "error", "errmsg", "err_msg"):
        v = res.get(k)
        if v and isinstance(v, str):
            return v
    return f"code={res.get('code', '?')} body={res}"


class AuthAPI:
    """Authentication endpoints — email OTP flow."""

    def __init__(self, session: TalkinSession):
        self._s = session

    def send_email(self, email: str) -> Dict[str, Any]:
        """POST /api/user/v1/sessions/email — send OTP to email."""
        res = self._s.post("/api/user/v1/sessions/email", {"email": email})
        if not _ok(res):
            raise AuthenticationError(f"OTP send failed: {_err(res)}")
        return res

    def login(self, email: str, code: str) -> str:
        """
        POST /api/user/v1/sessions — verify OTP and get bearer token.
        Returns the JWT token string on success.
        """
        cfg = self._s.config
        candidates: List[Dict[str, Any]] = [
            {"auth_type": "EMAIL", "email": {"email": email, "code": code}},
            {
                "auth_type": "EMAIL",
                "email":      {"email": email, "code": code},
                "device_id":   cfg.device_id,
                "device_name": cfg.device_name,
                "app_version": cfg.app_version,
                "platform":    "android",
            },
            {
                "email": email, "code": code,
                "device_id": cfg.device_id, "device_name": cfg.device_name,
                "app_version": cfg.app_version, "platform": "android",
            },
            {"email": email, "code": code},
        ]
        last: Dict[str, Any] = {}
        for i, payload in enumerate(candidates, 1):
            log.debug("login attempt %d: %s", i, payload)
            res = self._s.post("/api/user/v1/sessions", payload, encrypted=True)
            log.debug("login attempt %d response: %s", i, res)
            if _ok(res):
                token: str = res.get("data", {}).get("token", "")
                if token:
                    self._s.token = token
                    return token
            last = res
            if str(res.get("code", "")) not in ("BAD_PARAMETER", "BAD_REQUEST", "400", ""):
                break
        raise AuthenticationError(_err(last))

    def logout(self) -> Dict[str, Any]:
        """POST /api/user/v1/sessions/logout — invalidate current token."""
        res = self._s.post("/api/user/v1/sessions/logout", {})
        self._s.token = None
        return res
