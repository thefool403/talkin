from typing import Any, Dict, List, Optional
from ..http.session import TalkinSession


class UserAPI:
    """User profile, social, VIP, and cosmetic endpoints."""

    def __init__(self, session: TalkinSession):
        self._s = session

    def get_profile(self, aid: Optional[str] = None) -> Dict[str, Any]:
        """GET /api/user/v1/users/profile"""
        ep = "/api/user/v1/users/profile" + (f"?aid={aid}" if aid else "")
        return self._s.get(ep).get("data", {})

    def get_extra(self, aids: List[str], includes: str = "basic_info,lang_ex,vip") -> Dict[str, Any]:
        """GET /api/user/v1/users/extra — batch field fetch."""
        return self._s.get(
            f"/api/user/v1/users/extra?aids={','.join(aids)}&includes={includes}"
        ).get("data", {})

    def get_vip_info_batch(self, aids: List[str]) -> Dict[str, Any]:
        """GET /api/user/v1/vip/info/batch"""
        return self._s.get(
            f"/api/user/v1/vip/info/batch?aids={','.join(aids)}"
        ).get("data", {})

    def get_following(self, cursor: Optional[str] = None, limit: int = 20) -> Dict[str, Any]:
        """GET /api/user/v1/users/follows"""
        ep = f"/api/user/v1/users/follows?page.limit={limit}"
        if cursor:
            ep += f"&page.cursor={cursor}"
        return self._s.get(ep).get("data", {})

    def get_visitors(self, aid: str, limit: int = 20, cursor: Optional[str] = None) -> List[Dict]:
        """GET /api/user/v1/users/visits/visitors"""
        ep = f"/api/user/v1/users/visits/visitors?to_aid={aid}&page.limit={limit}"
        if cursor:
            ep += f"&page.cursor={cursor}"
        return self._s.get(ep).get("data", {}).get("list", [])

    def like_user(self, aid: str, action: str = "LIKE") -> Dict[str, Any]:
        """POST /api/user/v1/like — action: LIKE | UNLIKE"""
        return self._s.post("/api/user/v1/like", {"aid": aid, "action": action})

    def mark_active(self) -> Dict[str, Any]:
        """POST /api/user/v1/active — update presence heartbeat."""
        return self._s.post("/api/user/v1/active", {})

    def get_unlock_config(self) -> Dict[str, Any]:
        """GET /api/user/v1/unlock/config"""
        return self._s.get("/api/user/v1/unlock/config").get("data", {})

    def get_dressup_items(self, status: str = "ACTIVE") -> Any:
        """GET /api/user/v1/dressups/own — status: ACTIVE | ALL | EXPIRED"""
        return self._s.get(f"/api/user/v1/dressups/own?status={status}").get("data")

    def get_intimacy_detail(self, to_aid: str) -> Dict[str, Any]:
        """GET /api/user/v1/intimacy/detail"""
        return self._s.get(f"/api/user/v1/intimacy/detail?to_aid={to_aid}").get("data", {})

    def get_meeting_gift_givers(self, to_aid: str, limit: int = 20, cursor: Optional[str] = None) -> Any:
        """GET /api/user/v1/meeting-gifts/givers"""
        ep = f"/api/user/v1/meeting-gifts/givers?to_aid={to_aid}&page.limit={limit}"
        if cursor:
            ep += f"&page.cursor={cursor}"
        return self._s.get(ep).get("data")

    def get_meeting_gifts_on_sale(self) -> Any:
        """GET /api/user/v1/meeting-gifts/on-sale"""
        return self._s.get("/api/user/v1/meeting-gifts/on-sale").get("data")
