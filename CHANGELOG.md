# Changelog

All notable changes to **talkin** are documented here.

---

## [1.0.0] — 2026-04-17

### Added
- Initial public release of the **talkin** Python SDK.
- `TalkinClient` — main entry point with `api_key`, `device_id`, `user_agent`, `app_version`.
- `Console` — integrated request tracker with live logging and session summary table.
- All encryption/decryption delegated to the TalkinCrypto API (no local key material).
- `AuthAPI` — email OTP login flow with multi-shape payload fallback.
- `UserAPI` — profile, extra, VIP batch, following, visitors, dressup, intimacy, meeting gifts.
- `RoomAPI` — room list, enter/exit, config, audiences, mic, gift panel, rankings, heartbeat.
- `IMAPI` — TIM user sig, C2C info/restriction, conversations, message history, unread count.
- `MomentAPI` — global feed, user moments, like, comment.
- `PaymentAPI` — wallet, recharge plans, VIP plans, VIP detail.
- `ActivityAPI` — version check, translate, report events, activity entry.
- `CryptoClient` — tienc, CBC, GCM, CTR, ECB, gzip modes all via API.
- Plan rate limit display: `free(30)`, `helper(100)`, `paid(200)`, `developer(300)` req/min.
- `talkin.check_for_updates()` — background PyPI version check.
- Context manager support (`with TalkinClient(...) as client`).
- Full `pytest` test suite and `examples/` folder.

---

## [Unreleased]

- Async (`asyncio`) client variant.
- Webhook support for real-time events.
- CLI tool `talkin` for quick API exploration from the terminal.
