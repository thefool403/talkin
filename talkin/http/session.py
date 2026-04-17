import json
import time
import requests
from typing import Any, Dict, Optional, TYPE_CHECKING

from ..config     import TalkinConfig
from ..crypto     import CryptoClient
from ..exceptions import NetworkError, APIRequestError, CryptoError, RateLimitError
from ..constants  import CONTENT_TYPE_TIENC, CONTENT_TYPE_JSON

if TYPE_CHECKING:
    from ..console import Console


class TalkinSession:
    """
    Sync HTTP session for the Talkin social API.

    All encryption/decryption is delegated to CryptoClient.
    Optionally records every request to a Console instance.
    """

    def __init__(
        self,
        config:  TalkinConfig,
        crypto:  CryptoClient,
        console: Optional["Console"] = None,
    ):
        self.config  = config
        self.crypto  = crypto
        self._con    = console
        self.token:  Optional[str] = None

        self._session = requests.Session()
        self._session.headers.update(self._base_headers())

    # ── headers ───────────────────────────────────────────────────

    def _base_headers(self) -> Dict[str, str]:
        return {
            "User-Agent":       self.config.user_agent,
            "x-ti-device":      self.config.device_type,
            "x-ti-device-id":   self.config.device_id,
            "x-ti-device-name": self.config.device_name,
            "x-app-lang":       self.config.language,
            "x-app-ver":        self.config.app_version,
            "X-App-SOURCE":     self.config.app_source,
        }

    def _headers(self, content_type: str) -> Dict[str, str]:
        h = {"Content-Type": content_type}
        if self.token:
            h["Authorization"] = f"Bearer {self.token}"
        return h

    # ── POST ──────────────────────────────────────────────────────

    def post(
        self,
        endpoint:  str,
        payload:   Dict[str, Any],
        encrypted: bool = True,
    ) -> Dict[str, Any]:
        url = self.config.base_url + endpoint
        t0  = time.perf_counter()
        try:
            if encrypted:
                cipher_hex   = self.crypto.encrypt_tienc(payload)
                cipher_bytes = bytes.fromhex(cipher_hex)
                r = self._session.post(
                    url,
                    data=cipher_bytes,
                    headers=self._headers(CONTENT_TYPE_TIENC),
                    timeout=self.config.timeout,
                )
            else:
                r = self._session.post(
                    url,
                    json=payload,
                    headers=self._headers(CONTENT_TYPE_JSON),
                    timeout=self.config.timeout,
                )
            ms     = (time.perf_counter() - t0) * 1000
            result = self._decode(r)
            if self._con:
                self._con.record_request("POST", endpoint, r.status_code, ms, encrypted)
            return result

        except (CryptoError, RateLimitError, NetworkError, APIRequestError):
            raise
        except requests.RequestException as exc:
            ms = (time.perf_counter() - t0) * 1000
            if self._con:
                self._con.record_request("POST", endpoint, 0, ms, encrypted, error=str(exc))
            raise NetworkError(str(exc)) from exc
        except Exception as exc:
            ms = (time.perf_counter() - t0) * 1000
            if self._con:
                self._con.record_request("POST", endpoint, 0, ms, encrypted, error=str(exc))
            raise NetworkError(str(exc)) from exc

    # ── GET ───────────────────────────────────────────────────────

    def get(self, endpoint: str) -> Dict[str, Any]:
        url = self.config.base_url + endpoint
        t0  = time.perf_counter()
        try:
            r  = self._session.get(
                url,
                headers=self._headers(CONTENT_TYPE_TIENC),
                timeout=self.config.timeout,
            )
            ms     = (time.perf_counter() - t0) * 1000
            result = self._decode(r)
            if self._con:
                self._con.record_request("GET", endpoint, r.status_code, ms, False)
            return result

        except (CryptoError, RateLimitError, NetworkError, APIRequestError):
            raise
        except requests.RequestException as exc:
            ms = (time.perf_counter() - t0) * 1000
            if self._con:
                self._con.record_request("GET", endpoint, 0, ms, False, error=str(exc))
            raise NetworkError(str(exc)) from exc
        except Exception as exc:
            ms = (time.perf_counter() - t0) * 1000
            if self._con:
                self._con.record_request("GET", endpoint, 0, ms, False, error=str(exc))
            raise NetworkError(str(exc)) from exc

    # ── response decoding ─────────────────────────────────────────

    def _decode(self, r: requests.Response) -> Dict[str, Any]:
        raw = r.content
        if not raw:
            return {"code": 200, "msg": "success"}
        if raw[:1] in (b"{", b"["):
            try:
                return json.loads(raw.decode("utf-8"))
            except Exception:
                pass
        try:
            result = self.crypto.decrypt_tienc(raw.hex())
            return result if isinstance(result, dict) else {"data": result}
        except Exception:
            pass
        return {"raw": raw.hex(), "status": r.status_code}

    # ── lifecycle ─────────────────────────────────────────────────

    def close(self):
        self._session.close()
