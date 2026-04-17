from typing import Optional, Union

from .config   import TalkinConfig
from .console  import Console
from .crypto   import CryptoClient
from .http     import TalkinSession
from .auth     import AuthAPI
from .apis     import UserAPI, RoomAPI, IMAPI, MomentAPI, PaymentAPI, ActivityAPI


class TalkinClient:
    """
    Talkin SDK main client.

    All encryption/decryption is handled by the TalkinCrypto API service —
    no AES keys or algorithm details live in this SDK.

    Parameters
    ----------
    api_key      : TalkinCrypto API key
    device_id    : device fingerprint (x-ti-device-id header)
    user_agent   : HTTP User-Agent string
    app_version  : app version string (x-app-ver header)
    base_url     : Talkin social API base URL
    crypto_url   : TalkinCrypto service URL
    console      : True to enable live request logging + summary, or pass
                   a Console instance for custom configuration

    Modules
    -------
    crypto   : CryptoClient  — direct crypto API access + key info
    auth     : AuthAPI       — login, OTP, logout
    users    : UserAPI       — profiles, follows, VIP, dressups
    rooms    : RoomAPI       — room list, enter/exit, mic, gifts
    im       : IMAPI         — TIM credentials, DM conversations
    moments  : MomentAPI     — social feed, like, comment
    payment  : PaymentAPI    — wallet, recharge, VIP plans
    activity : ActivityAPI   — version check, translate, events

    Usage
    -----
        from talkin import TalkinClient

        with TalkinClient(
            api_key="tm_free_xxxx",
            device_id="...",
            console=True,
        ) as client:
            client.auth.send_email("you@example.com")
            token = client.auth.login("you@example.com", "123456")
            rooms = client.rooms.list_rooms()
            client.console.summary()
    """

    def __init__(
        self,
        api_key:     str,
        device_id:   str  = "692E63137BB388C9D3BAD4AB5C15152F01EFECF6",
        user_agent:  str  = "okhttp/4.11.0",
        app_version: str  = "4.9.1",
        base_url:    str  = "https://api-global.talkin.com.cn",
        crypto_url:  str  = "http://127.0.0.1:8000",
        console:     Union[bool, Console] = False,
    ):
        self.config = TalkinConfig(
            api_key=api_key,
            device_id=device_id,
            user_agent=user_agent,
            app_version=app_version,
            base_url=base_url,
            crypto_url=crypto_url,
        )

        if console is True:
            self.console: Optional[Console] = Console(live=True)
        elif isinstance(console, Console):
            self.console = console
        else:
            self.console = None

        self.crypto = CryptoClient(
            base_url=crypto_url,
            api_key=api_key,
            user_agent=user_agent,
            timeout=self.config.timeout,
            console=self.console,
        )

        self._session = TalkinSession(
            config=self.config,
            crypto=self.crypto,
            console=self.console,
        )

        self.auth     = AuthAPI(self._session)
        self.users    = UserAPI(self._session)
        self.rooms    = RoomAPI(self._session)
        self.im       = IMAPI(self._session)
        self.moments  = MomentAPI(self._session)
        self.payment  = PaymentAPI(self._session)
        self.activity = ActivityAPI(self._session)

    @property
    def token(self) -> Optional[str]:
        return self._session.token

    @token.setter
    def token(self, value: Optional[str]):
        self._session.token = value

    def close(self):
        self._session.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
