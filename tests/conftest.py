"""
Shared pytest fixtures for the talkin test suite.

All HTTP calls are intercepted — no live network or crypto service needed.
"""
import pytest
from unittest.mock import MagicMock, patch

from talkin         import TalkinClient
from talkin.config  import TalkinConfig
from talkin.crypto  import CryptoClient
from talkin.http    import TalkinSession


FAKE_API_KEY  = "tm_free_test000000000000000"
FAKE_DEVICE   = "AABBCCDDEEFF00112233445566778899AABBCCDD"
FAKE_TOKEN    = "eyJhbGciOiJIUzI1NiJ9.test.token"
FAKE_ROOM_ID  = "1234567890"
FAKE_SID      = "9876543210"
FAKE_AID      = "1111111111111111111"


# ── mock crypto client ────────────────────────────────────────────

@pytest.fixture
def mock_crypto():
    crypto = MagicMock(spec=CryptoClient)
    crypto.encrypt_tienc.return_value = "deadbeef" * 8
    crypto.decrypt_tienc.return_value = {"code": "200", "msg": "success", "data": {}}
    crypto.key_info.return_value = {
        "key":    FAKE_API_KEY,
        "plan":   "free",
        "status": "active",
        "rate_limit": {"limit": 30, "used": 5, "remaining": 25},
    }
    return crypto


# ── mock session ──────────────────────────────────────────────────

@pytest.fixture
def mock_session(mock_crypto):
    config  = TalkinConfig(api_key=FAKE_API_KEY, device_id=FAKE_DEVICE)
    session = TalkinSession(config=config, crypto=mock_crypto)
    session.token = FAKE_TOKEN
    return session


# ── full client with mocked session ───────────────────────────────

@pytest.fixture
def client(mock_crypto):
    with patch("talkin.client.CryptoClient", return_value=mock_crypto), \
         patch("talkin.http.session.requests.Session") as mock_sess_cls:

        mock_http = MagicMock()
        mock_sess_cls.return_value = mock_http
        mock_http.headers = {}

        c = TalkinClient(api_key=FAKE_API_KEY, device_id=FAKE_DEVICE)
        c._session.token = FAKE_TOKEN
        yield c
