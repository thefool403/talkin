import time
from typing import Any, Dict, List
from ..http.session import TalkinSession


class ActivityAPI:
    """Activity, utility, and app-level endpoints."""

    def __init__(self, session: TalkinSession):
        self._s = session

    def version_check(self, version: str = "4.9.1", platform: str = "android") -> Dict[str, Any]:
        return self._s.post("/api/app/v1/version/check",
                            {"version": version, "platform": platform}).get("data", {})

    def report_events(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        return self._s.post("/api/app/v1/events/reports", {"events": events})

    def get_activity_entry(self, code: str) -> Dict[str, Any]:
        return self._s.get(f"/api/activity/v2/entry?code={code}").get("data", {})

    def translate(self, text: str, to_lang: str, from_lang: str = "auto") -> Dict[str, Any]:
        payload: Dict[str, Any] = {"text": text, "to": to_lang}
        if from_lang and from_lang != "auto":
            payload["from"] = from_lang
        return self._s.post("/api/toolkit/v1/text/translations", payload).get("data", {})
