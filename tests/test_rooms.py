"""Tests for RoomAPI."""
import pytest
from unittest.mock import MagicMock

from talkin.apis.room_api import RoomAPI


def make_session(get_resp=None, post_resp=None):
    session      = MagicMock()
    session.get  = MagicMock(return_value=get_resp  or {"data": {}})
    session.post = MagicMock(return_value=post_resp or {"code": "200"})
    return session


# ── list_rooms ────────────────────────────────────────────────────

def test_list_rooms_returns_list():
    rooms_data = {"list": [{"room_id": "1", "session_id": "s1"}]}
    session    = make_session(get_resp={"data": rooms_data})
    api        = RoomAPI(session)
    result     = api.list_rooms()
    assert result == rooms_data
    session.get.assert_called_once()
    call_ep = session.get.call_args[0][0]
    assert "audio/list" in call_ep
    assert "tab=ALL"    in call_ep


def test_list_rooms_with_cursor():
    session = make_session(get_resp={"data": {"list": []}})
    api     = RoomAPI(session)
    api.list_rooms(cursor="abc123")
    ep = session.get.call_args[0][0]
    assert "page.cursor=abc123" in ep


def test_list_rooms_custom_tab():
    session = make_session(get_resp={"data": {"list": []}})
    api     = RoomAPI(session)
    api.list_rooms(tab="FOLLOWING")
    ep = session.get.call_args[0][0]
    assert "tab=FOLLOWING" in ep


# ── enter / exit ──────────────────────────────────────────────────

def test_enter_room_posts_correct_body():
    session = make_session(post_resp={"code": "200", "data": {"rtc_token": "tok"}})
    api     = RoomAPI(session)
    api.enter_room("ROOM1", "SID1")
    session.post.assert_called_once_with(
        "/api/room/v1/audio/enter",
        {"room_id": "ROOM1", "session_id": "SID1"},
    )


def test_exit_room_uses_get():
    session = make_session(get_resp={"code": "200"})
    api     = RoomAPI(session)
    api.exit_room("ROOM1", "SID1")
    ep = session.get.call_args[0][0]
    assert "audio/exit" in ep
    assert "room_id=ROOM1" in ep


# ── heartbeat ─────────────────────────────────────────────────────

def test_heartbeat_posts_ids():
    session = make_session(post_resp={"code": "200"})
    api     = RoomAPI(session)
    api.heartbeat("R1", "S1")
    session.post.assert_called_once_with(
        "/api/room/v1/event/heartbeat",
        {"room_id": "R1", "session_id": "S1"},
    )


# ── gift panel ────────────────────────────────────────────────────

def test_get_gift_panel_no_params():
    session = make_session(get_resp={"data": {"items": []}})
    api     = RoomAPI(session)
    api.get_gift_panel()
    ep = session.get.call_args[0][0]
    assert ep == "/api/room/v1/gift/panel"


def test_get_gift_panel_with_params():
    session = make_session(get_resp={"data": {}})
    api     = RoomAPI(session)
    api.get_gift_panel(category="POPULAR", tab="ALL")
    ep = session.get.call_args[0][0]
    assert "category=POPULAR" in ep
    assert "tab=ALL"          in ep
