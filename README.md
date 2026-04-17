<div align="center">

```
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        ⚠️  COMMUNITY UNLOCK — PUBLIC RELEASE NOTICE          ║
║                                                              ║
║   The Talkin Python SDK will become fully public once       ║
║   our Discord community reaches **100 members**.            ║
║                                                              ║
║   Until then, early access is available for community       ║
║   members who join the Discord server and help with:        ║
║                                                              ║
║      • Testing new SDK features                             ║
║      • Reporting API issues or bugs                         ║
║      • Sharing scripts, bots, and integrations              ║
║                                                              ║
║   When the server reaches 100 members:                      ║
║      ✔ The SDK becomes publicly accessible                  ║
║      ✔ Discord bot integrations are enabled                 ║
║      ✔ All developer tools will be unlocked                 ║
║                                                              ║
║        Join the community and help unlock the release!      ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

[![Join Discord](https://img.shields.io/badge/Join%20Discord-5865F2?style=for-the-badge\&logo=discord\&logoColor=white)](https://discord.gg/gYhVPvVWCN)

</div>

---



<div align="center">

```
 ████████╗ █████╗ ██╗     ██╗  ██╗██╗███╗   ██╗
 ╚══██╔══╝██╔══██╗██║     ██║ ██╔╝██║████╗  ██║
    ██║   ███████║██║     █████╔╝ ██║██╔██╗ ██║
    ██║   ██╔══██║██║     ██╔═██╗ ██║██║╚██╗██║
    ██║   ██║  ██║███████╗██║  ██╗██║██║ ╚████║
    ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝
```

**Unofficial Python SDK for the Talkin Social API**

[![PyPI version](https://badge.fury.io/py/talkin.svg)](https://pypi.org/project/talkin/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Discord](https://img.shields.io/badge/Discord-Join%20Us-5865F2?logo=discord&logoColor=white)](https://discord.gg/gYhVPvVWCN)
[![Downloads](https://img.shields.io/pypi/dm/talkin)](https://pypi.org/project/talkin/)

*Encrypted · Fast · Easy to use*

</div>

---

## ✨ Features

- 🔐 **Zero local keys** — all AES encryption/decryption goes through the TalkinCrypto API, so your keys and algorithm never touch client machines
- 📡 **Full API coverage** — auth, users, rooms, IM/chat, moments, payment, activity
- 🖥️ **Built-in Console** — live request logger + session summary table with rate-limit bar
- 🚀 **Sync + simple** — pure `requests`, no asyncio required
- 📦 **PyPI ready** — install with one command, zero config

---

## 📦 Installation

```bash
pip install talkin
```

Requires Python 3.9+ and a running **TalkinCrypto** service (self-hosted or provided).

---

## ⚡ Quick Start

```python
from talkin import TalkinClient

with TalkinClient(
    api_key    = "tm_free_xxxx",
    device_id  = "YOUR_DEVICE_ID",
    user_agent = "okhttp/4.11.0",
    app_version= "4.9.1",
    crypto_url = "http://your-crypto-service:8000",
    console    = True,          # ← live request log
) as client:

    # 1. login
    client.auth.send_email("you@example.com")
    otp   = input("OTP: ")
    token = client.auth.login("you@example.com", otp)

    # 2. explore
    profile = client.users.get_profile()
    rooms   = client.rooms.list_rooms()

    print(f"Welcome, {profile['basic_info']['nick']}!")
    print(f"Found {len(rooms['list'])} rooms")

    # 3. session summary
    client.console.summary()
```

**Console output:**

```
  14:36:21  POST  /api/user/v1/sessions/email      200   735ms  [ENC]
  14:36:22  CRYP  encrypt_tienc                    OK     12ms
  14:36:22  POST  /api/user/v1/sessions             200   245ms  [ENC]
  ...

┌──────────────────────────────────────────────────────────────────────┐
│  TALKIN SDK  ·  SESSION SUMMARY                                       │
├──────────────────────────────────────────────────────────────────────┤
│  Plan : Free   Rate : [████████░░░░░░░░░░░░]  8 / 30  (per minute)  │
│  Requests   : 34   OK: 32  Err: 2  Encrypted: 28   Session: 12.4s   │
│  API timing : avg 220ms  min 66ms  max 735ms                         │
│  Crypto ops : 28   OK: 28   avg 14ms                                 │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 🔑 API Key Plans

Get your API key from the TalkinCrypto service. Rate limits apply per minute:

| Plan          | Rate Limit | Access               |
|:--------------|:----------:|:---------------------|
| 🆓 `free`     | 30 / min   | Public access        |
| 🤝 `helper`   | 100 / min  | Community helpers    |
| 💳 `paid`     | 200 / min  | Paid subscribers     |
| 🛠️ `developer`| 300 / min  | Verified developers  |

> **Want a free Developer key?** [Join our Discord](#-join-our-discord--become-a-contributor) and become a contributor!

---

## 📚 API Reference

### `TalkinClient`

| Parameter     | Type    | Default                      | Description                       |
|:--------------|:--------|:-----------------------------|:----------------------------------|
| `api_key`     | `str`   | —                            | TalkinCrypto API key (required)   |
| `device_id`   | `str`   | `"692E...F6"`                | Device fingerprint header         |
| `user_agent`  | `str`   | `"okhttp/4.11.0"`            | HTTP User-Agent                   |
| `app_version` | `str`   | `"4.9.1"`                    | App version header                |
| `base_url`    | `str`   | `api-global.talkin.com.cn`   | Talkin social API URL             |
| `crypto_url`  | `str`   | `http://127.0.0.1:8000`      | TalkinCrypto service URL          |
| `console`     | `bool`  | `False`                      | Enable live logging + summary     |

### `client.auth`

| Method                       | Description                          |
|:-----------------------------|:-------------------------------------|
| `send_email(email)`          | Send OTP to email                    |
| `login(email, code) → token` | Verify OTP, returns JWT token        |
| `logout()`                   | Invalidate current session token     |

### `client.users`

| Method                           | Description                              |
|:---------------------------------|:-----------------------------------------|
| `get_profile(aid?)`              | Own or target user's profile             |
| `get_extra(aids, includes)`      | Batch field fetch for multiple users     |
| `get_vip_info_batch(aids)`       | VIP status for multiple users            |
| `get_following(cursor?, limit)`  | Users the account follows                |
| `get_visitors(aid, limit)`       | Profile visit history                    |
| `like_user(aid, action)`         | Like / unlike a user                     |
| `mark_active()`                  | Update presence heartbeat                |
| `get_unlock_config()`            | Profile unlock feature config            |
| `get_dressup_items(status)`      | Avatar frames, chat bubbles, cosmetics   |
| `get_intimacy_detail(to_aid)`    | Intimacy level with a user               |
| `get_meeting_gift_givers(aid)`   | Users who sent profile gifts             |
| `get_meeting_gifts_on_sale()`    | Available profile gifts                  |

### `client.rooms`

| Method                                | Description                           |
|:--------------------------------------|:--------------------------------------|
| `list_rooms(tab, scene, limit)`       | Room list — ALL / FOLLOWING / NEW     |
| `recommended_rooms()`                 | Algorithmically recommended rooms     |
| `social_rooms()`                      | Rooms where followed users are active |
| `get_rankings(category, tab)`         | HOT / NEW / LANGUAGE × DAY/WEEK/MONTH |
| `enter_room(room_id, session_id)`     | Enter a room, returns rtc/im tokens   |
| `exit_room(room_id, session_id)`      | Exit a room                           |
| `get_room_info()`                     | Current room details                  |
| `get_room_config(room_id, ...)`       | Mics, gifts, settings, topics         |
| `get_audiences(room_id, ...)`         | Paginated audience list               |
| `heartbeat(room_id, session_id)`      | Presence heartbeat (~30s interval)    |
| `get_mic_state()`                     | Current mic seat layout               |
| `apply_mic(room_id, session_id)`      | Request to go on mic                  |
| `reply_mic_invite(room_id, opinion)`  | Accept / decline mic invite           |
| `get_gift_panel(category?, tab?)`     | Available gifts                       |
| `get_gift_rankings(room_id, ...)`     | Top gift senders for this session     |
| `get_public_gifts()`                  | CDN URLs for gift animations          |
| `get_stt_packages()`                  | Speech-to-text packages               |

### `client.im`

| Method                              | Description                          |
|:------------------------------------|:-------------------------------------|
| `get_im_info()`                     | Tencent IM app_id, sdk_app_id        |
| `get_user_sig()`                    | uid + UserSig for WebSocket auth     |
| `get_c2c_info(to_aid)`              | Chat restriction + relation info     |
| `get_c2c_restriction(aids)`         | Batch chat restriction check         |
| `get_conversation_list(limit)`      | DM conversation list                 |
| `get_conversation(to_aid)`          | Single conversation detail           |
| `get_message_history(to_aid)`       | DM message history                   |
| `mark_conversation_read(to_aid)`    | Mark all messages as read            |
| `get_unread_profile()`              | Total unread count                   |
| `get_unread_count() → int`          | Convenience — returns int            |

### `client.moments`

| Method                            | Description                |
|:----------------------------------|:---------------------------|
| `feed(feed_type, limit)`          | BEST / NEW / FOLLOWING     |
| `user_moments(aid, limit)`        | Moments for a specific user|
| `like_moment(moment_id, action)`  | Like / unlike a moment     |
| `comment_moment(moment_id, text)` | Comment on a moment        |

### `client.payment`

| Method             | Description                    |
|:-------------------|:-------------------------------|
| `wallet()`         | Wallet balance                 |
| `recharge_plans()` | Available coin recharge plans  |
| `vip_plans()`      | Available VIP subscription plans|
| `vip_detail()`     | Current VIP status + expiry    |

### `client.activity`

| Method                              | Description                    |
|:------------------------------------|:-------------------------------|
| `version_check(version, platform)`  | Check for app update           |
| `translate(text, to_lang)`          | Translate text                 |
| `report_events(events)`             | Send analytics events          |
| `get_activity_entry(code)`          | Fetch campaign/activity entry  |

### `client.crypto`

| Method               | Description                                |
|:---------------------|:-------------------------------------------|
| `key_info()`         | Plan, rate limit, key status               |
| `encrypt_tienc(data)`| Encrypt with bin/tienc (Talkin wire format)|
| `decrypt_tienc(hex)` | Decrypt bin/tienc ciphertext               |
| `encrypt_gcm(text)`  | AES-GCM encrypt                            |
| `decrypt_gcm(hex)`   | AES-GCM decrypt                            |
| `encrypt_ctr(text)`  | AES-CTR encrypt                            |
| `decrypt_ctr(hex)`   | AES-CTR decrypt                            |
| `encrypt_cbc(text)`  | AES-CBC encrypt                            |
| `decrypt_cbc(hex)`   | AES-CBC decrypt                            |
| `encrypt_ecb(text)`  | AES-ECB encrypt                            |
| `decrypt_ecb(hex)`   | AES-ECB decrypt                            |
| `gzip_decompress(hex)`| Decompress gzip data                      |

---

## ⚠️ Error Handling

```python
from talkin.exceptions import (
    TalkinError,          # base — catch all SDK errors
    AuthenticationError,  # wrong OTP, expired token
    CryptoError,          # crypto service unreachable or error
    RateLimitError,       # plan rate limit exceeded
    NetworkError,         # network-level failure
    APIRequestError,      # server returned error code
)

try:
    token = client.auth.login(email, otp)
except AuthenticationError as e:
    print(f"Login failed: {e}")
except RateLimitError as e:
    print(f"Rate limit hit! Plan: {e.plan}, limit: {e.limit}/min")
except CryptoError as e:
    print(f"Crypto service error: {e}")
except NetworkError as e:
    print(f"Network error: {e}")
```

---

## 🔄 Version Check

```python
import talkin
talkin.check_for_updates()   # runs in background, prints to stderr if update available
```

Set `TALKIN_NO_UPDATE_CHECK=1` to disable.

---

## 🏗️ Architecture

```
TalkinClient
├── CryptoClient  ──────────────► TalkinCrypto API  (encrypt / decrypt)
│                                  http://your-service:8000
└── TalkinSession ──────────────► Talkin Social API
    ├── AuthAPI                    https://api-global.talkin.com.cn
    ├── UserAPI
    ├── RoomAPI                Every HTTP body is AES-encrypted.
    ├── IMAPI                  Keys never leave the crypto service.
    ├── MomentAPI
    ├── PaymentAPI
    └── ActivityAPI
```

---

## 💬 Join Our Discord — Become a Contributor

<div align="center">

```
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   🎙️  Join the Talkin SDK Community on Discord              ║
║                                                              ║
║   discord.gg/talkinapi                                       ║
║                                                              ║
║   ✅  Get a FREE Developer API key (300 req/min)            ║
║   ✅  Early access to new features before public release    ║
║   ✅  Direct line to the core dev team                      ║
║   ✅  Help shape the SDK roadmap                            ║
║                                                              ║
║   What we ask in return:                                     ║
║   › Report bugs or unexpected API behaviour you find        ║
║   › Share Python snippets, scripts, or integrations         ║
║   › Help answer questions from other SDK users              ║
║   › Even a star ⭐ on GitHub goes a long way!               ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

[![Join Discord](https://img.shields.io/badge/Join%20Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/gYhVPvVWCN)
[![Star on GitHub](https://img.shields.io/badge/Star%20on%20GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/talkin-sdk/talkin-python)

</div>

---

## 👨‍💻 Developer & Owner

<div align="center">

```
┌─────────────────────────────────────────────┐
│                                             │
│   Project  :  talkin Python SDK            │
│   Author   :  The Fool                     │
│   GitHub   :  github.com/thefool403/talkin │
│   Discord  :  discord.gg/talkinapi         │
│   PyPI     :  pypi.org/project/talkin/     │
│   License  :  MIT                          │
│   Version  :  1.0.0                        │
│   Type     :  Unofficial SDK               │
│                                             │
└─────────────────────────────────────────────┘
```

</div>

Contributions, bug reports, and PRs are welcome.
Please read [CONTRIBUTING.md](CONTRIBUTING.md) (coming soon) before submitting a PR.

---

## 📄 License

[MIT](LICENSE) © 2026 Talkin SDK Team
