"""Tests for CryptoClient — all HTTP mocked via responses library."""
import pytest
import responses as resp_lib
import json

from talkin.crypto    import CryptoClient
from talkin.exceptions import CryptoError, RateLimitError

BASE = "http://localhost:8000"
KEY  = "tm_free_testkey"


def make_client():
    return CryptoClient(base_url=BASE, api_key=KEY, user_agent="test/1.0")


# ── key_info ──────────────────────────────────────────────────────

@resp_lib.activate
def test_key_info_returns_plan():
    resp_lib.add(
        resp_lib.GET, f"{BASE}/api/v1/crypto/me",
        json={"key": KEY, "plan": "free", "rate_limit": {"limit": 30, "used": 0}},
        status=200,
    )
    info = make_client().key_info()
    assert info["plan"] == "free"
    assert info["rate_limit"]["limit"] == 30


@resp_lib.activate
def test_key_info_unreachable_raises_crypto_error():
    resp_lib.add(resp_lib.GET, f"{BASE}/api/v1/crypto/me",
                 body=ConnectionError("refused"))
    with pytest.raises(CryptoError, match="unreachable"):
        make_client().key_info()


# ── encrypt_tienc / decrypt_tienc ─────────────────────────────────

@resp_lib.activate
def test_encrypt_tienc_returns_hex():
    resp_lib.add(
        resp_lib.POST, f"{BASE}/api/v1/crypto/encrypt/tienc",
        json={"encrypted": "aabbccdd", "format": "bin/tienc"},
        status=200,
    )
    result = make_client().encrypt_tienc({"msg": "hello"})
    assert result == "aabbccdd"


@resp_lib.activate
def test_decrypt_tienc_returns_payload():
    resp_lib.add(
        resp_lib.POST, f"{BASE}/api/v1/crypto/decrypt/tienc",
        json={"result": {"msg": "hello"}},
        status=200,
    )
    result = make_client().decrypt_tienc("aabbccdd")
    assert result == {"msg": "hello"}


@resp_lib.activate
def test_rate_limit_raises_rate_limit_error():
    resp_lib.add(
        resp_lib.POST, f"{BASE}/api/v1/crypto/encrypt/tienc",
        json={"detail": "rate limit exceeded", "plan": "free"},
        status=429,
    )
    with pytest.raises(RateLimitError):
        make_client().encrypt_tienc({"msg": "test"})


@resp_lib.activate
def test_server_error_raises_crypto_error():
    resp_lib.add(
        resp_lib.POST, f"{BASE}/api/v1/crypto/encrypt/tienc",
        json={"detail": "internal server error"},
        status=500,
    )
    with pytest.raises(CryptoError, match="500"):
        make_client().encrypt_tienc({"msg": "test"})


# ── AES modes ─────────────────────────────────────────────────────

@resp_lib.activate
@pytest.mark.parametrize("mode,path,body_key", [
    ("gcm", "encrypt/gcm",  "data"),
    ("ctr", "encrypt/ctr",  "data"),
    ("cbc", "encrypt/cbc",  "data"),
    ("ecb", "encrypt/ecb",  "data"),
])
def test_encrypt_modes(mode, path, body_key):
    resp_lib.add(
        resp_lib.POST, f"{BASE}/api/v1/crypto/{path}",
        json={"encrypted": f"hex_{mode}", "mode": mode.upper()},
        status=200,
    )
    client = make_client()
    fn     = getattr(client, f"encrypt_{mode}")
    result = fn("hello world")
    assert result == f"hex_{mode}"


@resp_lib.activate
@pytest.mark.parametrize("mode,path", [
    ("gcm", "decrypt/gcm"),
    ("ctr", "decrypt/ctr"),
    ("cbc", "decrypt/cbc"),
    ("ecb", "decrypt/ecb"),
])
def test_decrypt_modes(mode, path):
    resp_lib.add(
        resp_lib.POST, f"{BASE}/api/v1/crypto/{path}",
        json={"result": f"plain_{mode}"},
        status=200,
    )
    client = make_client()
    fn     = getattr(client, f"decrypt_{mode}")
    result = fn("hexdata")
    assert result == f"plain_{mode}"
