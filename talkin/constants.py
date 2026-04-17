TALKIN_BASE_URL  = "https://api-global.talkin.com.cn"
CRYPTO_BASE_URL  = "http://127.0.0.1:8000"

CONTENT_TYPE_TIENC = "bin/tienc"
CONTENT_TYPE_JSON  = "application/json"

DEFAULT_PAGE_LIMIT = 20

# ── Crypto API plan rate limits (requests per minute) ──────────────
PLAN_RATE_LIMITS: dict = {
    "free":      30,
    "helper":    100,
    "paid":      200,
    "developer": 300,
}

PLAN_LABELS: dict = {
    "free":      "Free",
    "helper":    "Helper",
    "paid":      "Paid",
    "developer": "Developer",
}
