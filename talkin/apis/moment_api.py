from typing import Any, Dict, Optional
from ..http.session import TalkinSession


class MomentAPI:
    """Social feed / moments endpoints."""

    def __init__(self, session: TalkinSession):
        self._s = session

    def feed(self, feed_type: str = "BEST", limit: int = 20,
             cursor: Optional[str] = None) -> Dict[str, Any]:
        """feed_type: BEST | NEW | FOLLOWING"""
        ep = f"/api/moment/v1/moments?type={feed_type}&page.limit={limit}"
        if cursor:
            ep += f"&page.cursor={cursor}"
        res  = self._s.get(ep)
        data = res.get("data", {})
        return {"list": data.get("list") or data.get("items") or [],
                "next_cursor": data.get("page", {}).get("next_cursor")}

    def user_moments(self, aid: str, limit: int = 20,
                     cursor: Optional[str] = None) -> Dict[str, Any]:
        ep = f"/api/moment/v1/moments/profile?aid={aid}&page.limit={limit}"
        if cursor:
            ep += f"&page.cursor={cursor}"
        res  = self._s.get(ep)
        data = res.get("data", {})
        return {"list": data.get("list") or data.get("items") or [],
                "next_cursor": data.get("page", {}).get("next_cursor")}

    def like_moment(self, moment_id: str, action: str = "LIKE") -> Dict[str, Any]:
        """action: LIKE | UNLIKE"""
        return self._s.post(f"/api/moment/v1/moments/{moment_id}/like", {"action": action})

    def comment_moment(self, moment_id: str, text: str) -> Dict[str, Any]:
        return self._s.post(f"/api/moment/v1/moments/{moment_id}/comments", {"content": text})
