"""Tests for AuthAPI."""
import pytest
from unittest.mock import MagicMock

from talkin.auth.auth_api import AuthAPI
from talkin.exceptions    import AuthenticationError


def make_session(post_responses):
    """Return a session mock that yields responses from a list."""
    session       = MagicMock()
    session.token = None
    session.config = MagicMock()
    session.config.device_id   = "DEVICE"
    session.config.device_name = "Test Device"
    session.config.app_version = "4.9.1"
    side_effects = iter(post_responses)
    session.post.side_effect = lambda *a, **kw: next(side_effects)
    return session


# ── send_email ────────────────────────────────────────────────────

def test_send_email_ok():
    session = make_session([{"code": "200", "msg": "success"}])
    api     = AuthAPI(session)
    res     = api.send_email("test@example.com")
    assert res["code"] == "200"
    session.post.assert_called_once_with(
        "/api/user/v1/sessions/email", {"email": "test@example.com"}
    )


def test_send_email_failure_raises():
    session = make_session([{"code": "400", "msg": "invalid email"}])
    api     = AuthAPI(session)
    with pytest.raises(AuthenticationError, match="invalid email"):
        api.send_email("bad")


# ── login ─────────────────────────────────────────────────────────

GOOD_LOGIN = {
    "code": "200",
    "data": {"token": "eyJ.test.token", "aid": "12345"},
}

def test_login_success_first_shape():
    session = make_session([GOOD_LOGIN])
    api     = AuthAPI(session)
    token   = api.login("test@example.com", "123456")
    assert token == "eyJ.test.token"
    assert session.token == "eyJ.test.token"


def test_login_falls_through_to_second_shape():
    bad  = {"code": "BAD_PARAMETER", "msg": "bad shape"}
    session = make_session([bad, GOOD_LOGIN])
    api     = AuthAPI(session)
    token   = api.login("test@example.com", "123456")
    assert token == "eyJ.test.token"
    assert session.post.call_count == 2


def test_login_all_shapes_fail_raises():
    bad = {"code": "BAD_PARAMETER", "msg": "bad shape"}
    session = make_session([bad, bad, bad, bad])
    api     = AuthAPI(session)
    with pytest.raises(AuthenticationError):
        api.login("test@example.com", "wrongcode")


def test_login_auth_error_stops_cascade():
    auth_fail = {"code": "INVALID_CODE", "msg": "wrong OTP"}
    session   = make_session([auth_fail])
    api       = AuthAPI(session)
    with pytest.raises(AuthenticationError, match="wrong OTP"):
        api.login("test@example.com", "000000")
    assert session.post.call_count == 1


# ── logout ────────────────────────────────────────────────────────

def test_logout_clears_token():
    session       = make_session([{"code": "200"}])
    session.token = "existing_token"
    api           = AuthAPI(session)
    api.logout()
    assert session.token is None
