from typing import Any, Dict, List, Optional
from ..http.session import TalkinSession


class IMAPI:
    """IM / Chat / DM endpoints."""

    def __init__(self, session: TalkinSession):
        self._s = session

    def get_im_info(self) -> Dict[str, Any]:
        return self._s.get("/api/user/v1/im/info").get("data", {})

    def get_user_sig(self) -> Dict[str, Any]:
        """Returns uid + UserSig needed for WebSocket TIM auth."""
        return self._s.get("/api/user/v1/im/user-sig").get("data", {})

    def get_c2c_info(self, to_aid: str) -> Dict[str, Any]:
        return self._s.get(f"/api/user/v1/im/chat/c2c/info?to_aid={to_aid}").get("data", {})

    def get_c2c_restriction(self, aids: List[str]) -> Dict[str, Any]:
        return self._s.get(
            f"/api/user/v1/im/chat/c2c/restrict?aids={','.join(aids)}"
        ).get("data", {})

    def get_conversation_list(self, limit: int = 20, cursor: Optional[str] = None) -> Dict[str, Any]:
        ep = f"/api/message/v1/conversations?page.limit={limit}"
        if cursor:
            ep += f"&page.cursor={cursor}"
        res = self._s.get(ep)
        data = res.get("data") or {}
        return {"list": data} if isinstance(data, list) else data

    def get_conversation(self, to_aid: str) -> Dict[str, Any]:
        return self._s.get(f"/api/message/v1/conversations/{to_aid}").get("data", {})

    def get_message_history(self, to_aid: str, limit: int = 20,
                            cursor: Optional[str] = None) -> Dict[str, Any]:
        ep = f"/api/message/v1/messages?to_aid={to_aid}&page.limit={limit}"
        if cursor:
            ep += f"&page.cursor={cursor}"
        return self._s.get(ep).get("data", {})

    def mark_conversation_read(self, to_aid: str) -> bool:
        res = self._s.post(f"/api/message/v1/conversations/{to_aid}/read", {})
        return str(res.get("code", "")) in ("200", "0")

    def get_unread_profile(self) -> Dict[str, Any]:
        return self._s.get("/api/message/v1/unread/profile").get("data", {})

    def get_unread_count(self) -> int:
        try:
            return int(self.get_unread_profile().get("unread_count", 0))
        except Exception:
            return 0
