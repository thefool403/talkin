from typing import Any, Dict, List, Optional
from ..http.session import TalkinSession


class RoomAPI:
    """Voice room endpoints."""

    def __init__(self, session: TalkinSession):
        self._s = session

    def list_rooms(self, tab: str = "ALL", scene: str = "INDEX",
                   limit: int = 20, cursor: Optional[str] = None) -> Dict[str, Any]:
        """GET /api/room/v1/audio/list — tab: ALL | FOLLOWING | NEW | <lang>"""
        ep = f"/api/room/v1/audio/list?tab={tab}&scene={scene}&page.limit={limit}"
        if cursor:
            ep += f"&page.cursor={cursor}"
        return self._s.get(ep).get("data", {})

    def recommended_rooms(self) -> Any:
        return self._s.get("/api/room/v1/audio/recommend").get("data")

    def social_rooms(self) -> Any:
        return self._s.get("/api/room/v1/audio/social").get("data")

    def get_rankings(self, category: str = "HOT", tab: str = "DAY") -> Any:
        """category: HOT | NEW | LANGUAGE   tab: DAY | WEEK | MONTH"""
        return self._s.get(f"/api/room/v1/audio/rank?category={category}&tab={tab}").get("data")

    def enter_room(self, room_id: str, session_id: str) -> Dict[str, Any]:
        """POST /api/room/v1/audio/enter — returns rtc_token, im_token."""
        return self._s.post("/api/room/v1/audio/enter",
                            {"room_id": room_id, "session_id": session_id})

    def exit_room(self, room_id: str, session_id: str) -> Dict[str, Any]:
        return self._s.get(f"/api/room/v1/audio/exit?room_id={room_id}&session_id={session_id}")

    def get_room_info(self) -> Any:
        return self._s.get("/api/room/v1/room/info").get("data")

    def get_room_config(self, room_id: str, session_id: str,
                        includes: str = "MICS,GIFTS,SETTINGS", limit: int = 20) -> Any:
        """includes: MICS | GIFTS | SETTINGS | CHAT_TOPICS (comma-separated)"""
        ep = (f"/api/room/v1/cfg?includes={includes}"
              f"&room_id={room_id}&session_id={session_id}&page.limit={limit}")
        return self._s.get(ep).get("data")

    def get_chat_topics(self, room_id: str, session_id: str) -> Any:
        ep = f"/api/room/v1/cfg?includes=CHAT_TOPICS&room_id={room_id}&session_id={session_id}"
        return self._s.get(ep).get("data")

    def get_audiences(self, room_id: str, session_id: str,
                      limit: int = 20, cursor: Optional[str] = None) -> Any:
        ep = f"/api/room/v1/audio/audiences?room_id={room_id}&session_id={session_id}&page.limit={limit}"
        if cursor:
            ep += f"&page.cursor={cursor}"
        return self._s.get(ep).get("data")

    def heartbeat(self, room_id: str, session_id: str) -> Dict[str, Any]:
        """POST /api/room/v1/event/heartbeat — call every ~30s while in a room."""
        return self._s.post("/api/room/v1/event/heartbeat",
                            {"room_id": room_id, "session_id": session_id})

    def get_mic_state(self) -> Any:
        return self._s.get("/api/room/v1/mic/state").get("data")

    def apply_mic(self, room_id: str, session_id: str) -> Dict[str, Any]:
        return self._s.post("/api/room/v1/mic/apply",
                            {"room_id": room_id, "session_id": session_id})

    def reply_mic_invite(self, room_id: str, session_id: str, opinion: str) -> Dict[str, Any]:
        """opinion: YES | NO"""
        return self._s.post("/api/room/v1/mic/invite/reply",
                            {"room_id": room_id, "session_id": session_id, "opinion": opinion})

    def get_gift_panel(self, category: str = "", tab: str = "") -> Any:
        params = "&".join(f"{k}={v}" for k, v in [("category", category), ("tab", tab)] if v)
        ep = "/api/room/v1/gift/panel" + (f"?{params}" if params else "")
        return self._s.get(ep).get("data")

    def get_gift_rankings(self, room_id: str, session_id: str, limit: int = 20) -> Any:
        ep = f"/api/room/v1/gift/rank?room_id={room_id}&session_id={session_id}&page.limit={limit}"
        return self._s.get(ep).get("data")

    def get_public_gifts(self) -> Any:
        return self._s.get("/api/room/v1/public/res/gifts").get("data")

    def get_stt_packages(self) -> Any:
        return self._s.get("/api/room/v1/stt/package/list").get("data")
