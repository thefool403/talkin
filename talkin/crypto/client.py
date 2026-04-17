import time
import requests
from typing import Any, Dict, Optional, TYPE_CHECKING

from ..exceptions import CryptoError, RateLimitError
from ..constants  import PLAN_RATE_LIMITS

if TYPE_CHECKING:
    from ..console import Console


class CryptoClient:
    """
    Delegates all AES encryption/decryption to the TalkinCrypto API.

    Keys and algorithm details never exist in this SDK — they live
    exclusively inside the crypto service. Every encrypt/decrypt call
    is an HTTP request to that service.

    Supported modes (all via API):
        tienc  — bin/tienc  (AES-CBC, Talkin wire format)
        gcm    — AES-GCM
        ctr    — AES-CTR
        cbc    — AES-CBC  (custom key)
        ecb    — AES-ECB
        gzip   — gzip decompress
    """

    def __init__(
        self,
        base_url:   str,
        api_key:    str,
        user_agent: str,
        timeout:    int = 30,
        console:    Optional["Console"] = None,
    ):
        self._base       = base_url.rstrip("/")
        self._api_key    = api_key
        self._user_agent = user_agent
        self._timeout    = timeout
        self._console    = console

    # ── internal ──────────────────────────────────────────────────

    def _headers(self) -> Dict[str, str]:
        return {
            "X-API-Key":    self._api_key,
            "User-Agent":   self._user_agent,
            "Content-Type": "application/json",
            "x-request-id": "talkin-sdk",
        }

    def _post(self, path: str, body: Dict[str, Any]) -> Dict[str, Any]:
        url = self._base + path
        op  = path.split("/")[-1]       # e.g. "encrypt", "decrypt_tienc"
        t0  = time.perf_counter()
        try:
            r = requests.post(
                url,
                headers=self._headers(),
                json=body,
                timeout=self._timeout,
            )
        except requests.RequestException as exc:
            ms = (time.perf_counter() - t0) * 1000
            if self._console:
                self._console.record_crypto(op, ms, error=str(exc))
            raise CryptoError(f"Crypto API unreachable: {exc}") from exc

        ms = (time.perf_counter() - t0) * 1000

        try:
            data = r.json()
        except Exception:
            data = {"raw": r.text}

        if r.status_code == 429:
            plan  = data.get("plan", "unknown")
            limit = PLAN_RATE_LIMITS.get(plan, 0)
            if self._console:
                self._console.record_crypto(op, ms, error="rate_limit")
            raise RateLimitError(plan=plan, limit=limit)

        if r.status_code != 200:
            msg = data.get("detail") or data.get("message") or str(data)
            if self._console:
                self._console.record_crypto(op, ms, error=msg)
            raise CryptoError(f"Crypto API error {r.status_code}: {msg}")

        if self._console:
            self._console.record_crypto(op, ms)

        return data

    # ── tienc (primary Talkin wire format — AES-CBC) ───────────────

    def encrypt_tienc(self, payload: Any) -> str:
        """Encrypt using bin/tienc. Returns hex-encoded ciphertext."""
        res = self._post("/api/v1/crypto/encrypt/tienc", {"payload": payload})
        return res["encrypted"]

    def decrypt_tienc(self, data: str) -> Any:
        """Decrypt a tienc hex ciphertext. Returns original value."""
        res = self._post("/api/v1/crypto/decrypt/tienc", {"data": data})
        return res["result"]

    # ── generic CBC ────────────────────────────────────────────────

    def encrypt(self, payload: Any) -> str:
        res = self._post("/api/v1/crypto/encrypt", {"payload": payload})
        return res["encrypted"]

    def decrypt(self, data: str) -> Any:
        res = self._post("/api/v1/crypto/decrypt", {"data": data})
        return res["result"]

    # ── AES-GCM ────────────────────────────────────────────────────

    def encrypt_gcm(self, text: str) -> str:
        res = self._post("/api/v1/crypto/encrypt/gcm", {"data": text})
        return res["encrypted"]

    def decrypt_gcm(self, data: str) -> Any:
        res = self._post("/api/v1/crypto/decrypt/gcm", {"data": data})
        return res["result"]

    # ── AES-CTR ────────────────────────────────────────────────────

    def encrypt_ctr(self, text: str) -> str:
        res = self._post("/api/v1/crypto/encrypt/ctr", {"data": text})
        return res["encrypted"]

    def decrypt_ctr(self, data: str) -> Any:
        res = self._post("/api/v1/crypto/decrypt/ctr", {"data": data})
        return res["result"]

    # ── AES-CBC (explicit mode) ────────────────────────────────────

    def encrypt_cbc(self, text: str, key_type: str = "primary") -> str:
        res = self._post("/api/v1/crypto/encrypt/cbc", {"data": text, "key_type": key_type})
        return res["encrypted"]

    def decrypt_cbc(self, data: str) -> Any:
        res = self._post("/api/v1/crypto/decrypt/cbc", {"data": data})
        return res["result"]

    # ── AES-ECB ────────────────────────────────────────────────────

    def encrypt_ecb(self, text: str) -> str:
        res = self._post("/api/v1/crypto/encrypt/ecb", {"data": text})
        return res["encrypted"]

    def decrypt_ecb(self, data: str) -> Any:
        res = self._post("/api/v1/crypto/decrypt/ecb", {"data": data})
        return res["result"]

    # ── gzip ───────────────────────────────────────────────────────

    def gzip_decompress(self, data: str) -> Any:
        res = self._post("/api/v1/crypto/gzip/decompress", {"data": data})
        return res.get("result", res)

    # ── key info ───────────────────────────────────────────────────

    def key_info(self) -> Dict[str, Any]:
        """Return info about the current API key (plan, rate limit, etc.)."""
        url = self._base + "/api/v1/crypto/me"
        try:
            r = requests.get(url, headers=self._headers(), timeout=self._timeout)
            data = r.json()
            if self._console and isinstance(data, dict):
                plan  = data.get("plan", "")
                rl    = data.get("rate_limit", {})
                used  = rl.get("used", 0)
                limit = rl.get("limit")
                self._console.set_plan(plan, used, limit)
            return data
        except requests.RequestException as exc:
            raise CryptoError(f"Crypto API unreachable: {exc}") from exc
