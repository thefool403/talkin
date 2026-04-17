from dataclasses import dataclass
from .constants import TALKIN_BASE_URL, CRYPTO_BASE_URL


@dataclass
class TalkinConfig:
    """
    Configuration for TalkinClient.

    api_key      : TalkinCrypto API key  (X-API-Key on the crypto service)
    device_id    : device fingerprint    (x-ti-device-id header)
    user_agent   : HTTP User-Agent string
    app_version  : app version string    (x-app-ver header)
    base_url     : Talkin social API base URL
    crypto_url   : TalkinCrypto service URL (handles all AES operations)
    timeout      : request timeout in seconds
    retries      : automatic retry count on network error
    """

    api_key: str

    device_id:   str = "692E63137BB388C9D3BAD4AB5C15152F01EFECF6"
    user_agent:  str = "okhttp/4.11.0"
    app_version: str = "4.9.1"

    base_url:   str = TALKIN_BASE_URL
    crypto_url: str = CRYPTO_BASE_URL

    device_name: str = "ONEPLUS A6003 OnePlus"
    device_type: str = "1"
    language:    str = "en"
    app_source:  str = "Google"

    timeout: int = 30
    retries: int = 3
