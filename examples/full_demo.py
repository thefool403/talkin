"""
examples/full_demo.py — complete walkthrough of every SDK endpoint.

Install: pip install talkin
Run    : python examples/full_demo.py
Logs   : full_demo_debug.log
"""
import json
import logging
import sys
import traceback
import time

from talkin import TalkinClient
from talkin.exceptions import (
    TalkinError, AuthenticationError, CryptoError,
    NetworkError, RateLimitError, APIRequestError,
)

# ── logging ──────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("full_demo_debug.log", encoding="utf-8"),
    ],
)
log = logging.getLogger("talkin.full_demo")
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)

# ── config ───────────────────────────────────────────────────────

API_KEY    = "YOUR_KEY_HERE"
DEVICE_ID  = "692E63137BB388C9D3BAD4AB5C15152F01EFECF6"
USER_AGENT = "okhttp/4.11.0"
APP_VER    = "4.9.1"
EMAIL      = "YOUR_MAIL_HERE"

# ── helpers ──────────────────────────────────────────────────────

_step_num = 0

def sep(title):
    global _step_num
    _step_num += 1
    bar = "=" * 64
    print(f"\n{bar}\n  [{_step_num}] {title}\n{bar}")

def show(title, data):
    try:
        print(json.dumps(data, indent=2, default=str))
    except Exception:
        print(repr(data))

def call(label, fn, *args, **kwargs):
    log.debug(">>> %s", label)
    t0 = time.perf_counter()
    try:
        result = fn(*args, **kwargs)
        log.info("  %-44s OK  (%.0f ms)", label, (time.perf_counter()-t0)*1000)
        return result
    except RateLimitError as exc:
        log.error("  %-44s RATE LIMIT  %s", label, exc)
        log.debug("Traceback:\n%s", traceback.format_exc())
        log.warning("Waiting 10s …")
        time.sleep(10)
    except CryptoError as exc:
        log.error("  %-44s CRYPTO ERR  %s", label, exc)
        log.debug("Traceback:\n%s", traceback.format_exc())
    except NetworkError as exc:
        log.error("  %-44s NETWORK ERR %s", label, exc)
        log.debug("Traceback:\n%s", traceback.format_exc())
    except APIRequestError as exc:
        log.error("  %-44s API ERR  code=%s  %s", label, exc.code, exc.message)
        log.debug("Traceback:\n%s", traceback.format_exc())
    except AuthenticationError as exc:
        log.critical("  %-44s AUTH FAIL  %s", label, exc)
        raise
    except TalkinError as exc:
        log.error("  %-44s TALKIN ERR  %s", label, exc)
        log.debug("Traceback:\n%s", traceback.format_exc())
    except Exception as exc:
        log.error("  %-44s UNEXPECTED  %s", label, exc)
        log.debug("Traceback:\n%s", traceback.format_exc())
    return None


# ── main ─────────────────────────────────────────────────────────

def main():
    log.info("talkin full_demo starting  ver=%s  crypto=%s", APP_VER)

    with TalkinClient(
        api_key=API_KEY, device_id=DEVICE_ID,
        user_agent=USER_AGENT, app_version=APP_VER, console=True,
    ) as c:

        # ── crypto ────────────────────────────────────────────
        sep("CRYPTO — key info")
        info = call("crypto.key_info", c.crypto.key_info)
        if not info:
            log.critical("Crypto service unreachable — aborting")
            sys.exit(1)
        show("KEY INFO", info)
        rl = info.get("rate_limit", {})
        log.info("Plan: %s   remaining: %s/%s", info.get("plan"),
                 rl.get("remaining"), rl.get("limit"))

        # ── auth ──────────────────────────────────────────────
        sep("AUTH — send OTP")
        if not call("auth.send_email", c.auth.send_email, EMAIL):
            sys.exit(1)

        otp = input("\n[?] Enter OTP: ").strip()
        if not otp:
            log.critical("No OTP — aborting"); sys.exit(1)

        sep("AUTH — login")
        try:
            token = c.auth.login(EMAIL, otp)
            show("TOKEN", {"token": token[:20] + "..."})
            log.info("Logged in  %s...", token[:16])
        except AuthenticationError as e:
            log.critical("Login failed: %s", e); sys.exit(1)

        # ── users ─────────────────────────────────────────────
        sep("USER — profile")
        profile = call("users.get_profile", c.users.get_profile)
        my_aid = ""
        if profile:
            show("PROFILE", profile)
            basic  = profile.get("basic_info") or profile
            my_aid = str(basic.get("aid", ""))
            log.info("nick=%s  aid=%s", basic.get("nick"), my_aid)

        for label, fn, args in [
            ("users.get_extra",            c.users.get_extra,            ([my_aid],) if my_aid else None),
            ("users.get_vip_info_batch",   c.users.get_vip_info_batch,   ([my_aid],) if my_aid else None),
            ("users.get_following",        c.users.get_following,        ()),
            ("users.get_visitors",         c.users.get_visitors,         (my_aid,) if my_aid else None),
            ("users.mark_active",          c.users.mark_active,          ()),
            ("users.get_meeting_gifts_on_sale", c.users.get_meeting_gifts_on_sale, ()),
            ("users.get_meeting_gift_givers",   c.users.get_meeting_gift_givers,   (my_aid,) if my_aid else None),
            ("users.get_intimacy_detail",  c.users.get_intimacy_detail,  (my_aid,) if my_aid else None),
            ("users.get_unlock_config",    c.users.get_unlock_config,    ()),
            ("users.get_dressup_items",    c.users.get_dressup_items,    ()),
        ]:
            if args is None:
                log.warning("Skipping %s — no aid", label)
                continue
            sep(label)
            res = call(label, fn, *args)
            if res is not None:
                show(label, res)

        # ── payment ───────────────────────────────────────────
        for label, fn in [
            ("payment.wallet",          c.payment.wallet),
            ("payment.recharge_plans",  c.payment.recharge_plans),
            ("payment.vip_plans",       c.payment.vip_plans),
            ("payment.vip_detail",      c.payment.vip_detail),
        ]:
            sep(label)
            res = call(label, fn)
            if res is not None:
                show(label, res)

        # ── rooms ─────────────────────────────────────────────
        sep("ROOMS — list")
        rooms_data = call("rooms.list_rooms", c.rooms.list_rooms, limit=10)
        room_list  = []
        if rooms_data:
            show("ROOMS", rooms_data)
            room_list = rooms_data.get("list") or []

        for label, fn in [
            ("rooms.recommended_rooms", c.rooms.recommended_rooms),
            ("rooms.social_rooms",      c.rooms.social_rooms),
            ("rooms.get_rankings",      lambda: c.rooms.get_rankings("HOT", "DAY")),
            ("rooms.get_gift_panel",    c.rooms.get_gift_panel),
            ("rooms.get_public_gifts",  c.rooms.get_public_gifts),
            ("rooms.get_stt_packages",  c.rooms.get_stt_packages),
        ]:
            sep(label)
            res = call(label, fn)
            if res is not None:
                show(label, res)

        if room_list:
            first      = room_list[0]
            room_id    = str(first.get("room_id", ""))
            session_id = str(first.get("session_id", ""))
            log.info("Target room: %s / %s", room_id, session_id)

            for label, fn, args in [
                ("rooms.enter_room",       c.rooms.enter_room,       (room_id, session_id)),
                ("rooms.get_room_info",    c.rooms.get_room_info,    ()),
                ("rooms.get_room_config",  c.rooms.get_room_config,  (room_id, session_id)),
                ("rooms.get_chat_topics",  c.rooms.get_chat_topics,  (room_id, session_id)),
                ("rooms.get_audiences",    c.rooms.get_audiences,    (room_id, session_id)),
                ("rooms.get_gift_rankings",c.rooms.get_gift_rankings,(room_id, session_id)),
                ("rooms.get_mic_state",    c.rooms.get_mic_state,    ()),
                ("rooms.apply_mic",        c.rooms.apply_mic,        (room_id, session_id)),
                ("rooms.heartbeat",        c.rooms.heartbeat,        (room_id, session_id)),
                ("rooms.exit_room",        c.rooms.exit_room,        (room_id, session_id)),
            ]:
                sep(label)
                res = call(label, fn, *args)
                if res is not None:
                    show(label, res)

        # ── moments ───────────────────────────────────────────
        sep("MOMENTS — feed")
        feed = call("moments.feed", c.moments.feed, limit=10)
        moment_id = ""
        if feed:
            show("FEED", feed)
            for m in (feed.get("list") or []):
                moment_id = str(m.get("moment_id") or m.get("id", ""))
                if moment_id:
                    break

        if my_aid:
            sep("MOMENTS — user moments")
            my_m = call("moments.user_moments", c.moments.user_moments, my_aid, limit=10)
            if my_m:
                show("MY MOMENTS", my_m)

        # ── im ────────────────────────────────────────────────
        follow_data = call("users.get_following_for_im", c.users.get_following, limit=1)
        peer_aid = ""
        if follow_data:
            fl = follow_data.get("list") or []
            peer_aid = str(fl[0].get("aid", "")) if fl else ""

        for label, fn, args in [
            ("im.get_im_info",           c.im.get_im_info,           ()),
            ("im.get_user_sig",          c.im.get_user_sig,          ()),
            ("im.get_c2c_info",          c.im.get_c2c_info,          (peer_aid,) if peer_aid else None),
            ("im.get_c2c_restriction",   c.im.get_c2c_restriction,   ([peer_aid],) if peer_aid else None),
            ("im.get_unread_count",      c.im.get_unread_count,      ()),
            ("im.get_unread_profile",    c.im.get_unread_profile,    ()),
            ("im.get_conversation_list", c.im.get_conversation_list, ()),
        ]:
            if args is None:
                log.warning("Skipping %s — no peer aid", label)
                continue
            sep(label)
            res = call(label, fn, *args)
            if res is not None:
                show(label, res)

        # ── activity ──────────────────────────────────────────
        for label, fn, args in [
            ("activity.version_check",     c.activity.version_check,     (APP_VER,)),
            ("activity.translate_en_hi",   lambda: c.activity.translate("Hello!", "hi"), ()),
            ("activity.report_events",     c.activity.report_events,
             ([{"event_name": "sdk_test", "params": {}, "timestamp": int(time.time()*1000)}],)),
        ]:
            sep(label)
            res = call(label, fn, *args)
            if res is not None:
                show(label, res)

        # ── session summary ───────────────────────────────────
        c.console.summary() # type: ignore
        log.info("Full demo complete — see full_demo_debug.log for details")


if __name__ == "__main__":
    main()
