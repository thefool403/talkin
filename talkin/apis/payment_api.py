from typing import Any, Dict, List
from ..http.session import TalkinSession


class PaymentAPI:
    """Payment, wallet, and VIP endpoints."""

    def __init__(self, session: TalkinSession):
        self._s = session

    def wallet(self) -> Dict[str, Any]:
        return self._s.get("/api/user/v1/payment/wallets").get("data", {})

    def recharge_plans(self) -> List[Dict[str, Any]]:
        res  = self._s.get("/api/user/v1/payment/recharge/plans")
        data = res.get("data") or []
        if isinstance(data, dict):
            data = data.get("list") or data.get("items") or data.get("plans") or []
        return [item for item in data if isinstance(item, dict)]

    def vip_plans(self) -> List[Dict[str, Any]]:
        res  = self._s.get("/api/user/v1/payment/vip/plans")
        data = res.get("data") or []
        if isinstance(data, dict):
            data = data.get("list") or data.get("items") or data.get("plans") or []
        return [item for item in data if isinstance(item, dict)]

    def vip_detail(self) -> Dict[str, Any]:
        return self._s.get("/api/user/v1/vip/detail").get("data", {})
