"""
examples/basic_login.py — minimal login + profile fetch.

Install: pip install talkin
Run    : python examples/basic_login.py
"""
from talkin import TalkinClient

API_KEY    = "YOUR_KEY_HERE"
EMAIL      = "you@example.com"

with TalkinClient(
    api_key    = API_KEY,
    console    = True,
) as client:

    # ── crypto service info ──────────────────────────────────────
    info = client.crypto.key_info()
    rl   = info.get("rate_limit", {})
    print(f"\nPlan : {info.get('plan')}   "
          f"Requests remaining : {rl.get('remaining')}/{rl.get('limit')} per min\n")

    # ── OTP login ────────────────────────────────────────────────
    client.auth.send_email(EMAIL)
    otp   = input("[?] Enter OTP : ").strip()
    token = client.auth.login(EMAIL, otp)
    print(f"\nLogged in!  token = {token[:24]}...\n")

    # ── own profile ──────────────────────────────────────────────
    profile = client.users.get_profile()
    basic   = profile.get("basic_info") or profile
    print(f"Welcome, {basic.get('nick')}  (aid={basic.get('aid')})")

    # ── wallet balance ───────────────────────────────────────────
    wallet = client.payment.wallet()
    print(f"Coins  : {wallet.get('coins', '?')}")

    # ── summary ──────────────────────────────────────────────────
    client.console.summary() # type: ignore
