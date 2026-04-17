"""
talkin — Official Python SDK for the Talkin social API.

All encryption/decryption is handled by the TalkinCrypto service.
No AES keys or algorithm details live in this SDK.

Quick start::

    from talkin import TalkinClient

    with TalkinClient(
        api_key    = "tm_free_xxxx",
        device_id  = "YOUR_DEVICE_ID",
        user_agent = "okhttp/4.11.0",
        app_version= "4.9.1",
        crypto_url = "http://your-crypto-service:8000",
        console    = True,          # live request logging
    ) as client:

        client.auth.send_email("you@example.com")
        token = client.auth.login("you@example.com", "123456")

        rooms   = client.rooms.list_rooms()
        profile = client.users.get_profile()

        client.console.summary()    # print session summary table

Discord   : https://discord.gg/talkinapi
GitHub    : https://github.com/talkin-sdk/talkin-python
PyPI      : https://pypi.org/project/talkin/
"""

from ._version import (
    __version__,
    __author__,
    __author_email__,
    __description__,
    __url__,
    __discord__,
    __license__,
)

from .client    import TalkinClient
from .config    import TalkinConfig
from .console   import Console
from .exceptions import (
    TalkinError,
    AuthenticationError,
    APIRequestError,
    CryptoError,
    NetworkError,
    RateLimitError,
)
from .constants import PLAN_RATE_LIMITS, PLAN_LABELS

__all__ = [
    "TalkinClient",
    "TalkinConfig",
    "Console",
    "TalkinError",
    "AuthenticationError",
    "APIRequestError",
    "CryptoError",
    "NetworkError",
    "RateLimitError",
    "PLAN_RATE_LIMITS",
    "PLAN_LABELS",
    "__version__",
    "__discord__",
]


def check_for_updates(silent: bool = False) -> None:
    """
    Check PyPI for a newer version of talkin in the background.
    Prints a notice to stderr if an update is available.
    Set env var TALKIN_NO_UPDATE_CHECK=1 to disable.
    """
    print(f"JOIN OUR DISCORD : {__discord__}")
    import os
    if os.environ.get("TALKIN_NO_UPDATE_CHECK"):
        return

    import threading

    def _check():
        try:
            import requests as _req
            r = _req.get(
                "https://pypi.org/pypi/talkin/json",
                timeout=3,
                headers={"User-Agent": f"talkin/{__version__}"},
            )
            latest = r.json()["info"]["version"]

            def _ver(v: str):
                return tuple(int(x) for x in v.split("."))

            if _ver(latest) > _ver(__version__):
                import sys
                print(
                    f"\n  \033[93m[talkin] Update available: "
                    f"{__version__} \u2192 {latest}\033[0m\n"
                    f"  \033[2mRun: pip install --upgrade talkin\033[0m\n",
                    file=sys.stderr,
                )
        except Exception:
            pass

    threading.Thread(target=_check, daemon=True).start()
