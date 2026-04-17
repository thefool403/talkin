"""
examples/room_explorer.py — browse rooms, enter one, watch audiences.

Install: pip install talkin
Run    : python examples/room_explorer.py
"""
import json
from talkin import TalkinClient
from talkin.exceptions import TalkinError

API_KEY    = "YOUR_KEY_HERE"
EMAIL      = "you@example.com"


def pprint(label, data):
    print(f"\n── {label} " + "─" * (54 - len(label)))
    print(json.dumps(data, indent=2, default=str))


with TalkinClient(
    api_key    = API_KEY,
    console    = True,
) as client:

    # ── login ────────────────────────────────────────────────────
    client.auth.send_email(EMAIL)
    otp   = input("[?] OTP : ").strip()
    token = client.auth.login(EMAIL, otp)
    print(f"\nLogged in — token prefix : {token[:20]}...\n")

    # ── fetch rooms ──────────────────────────────────────────────
    data      = client.rooms.list_rooms(limit=10)
    room_list = data.get("list") or []
    print(f"Found {len(room_list)} rooms\n")

    for i, r in enumerate(room_list, 1):
        host  = r.get("host_info", {}).get("basic_info", {}).get("nick", "?")
        topic = r.get("topic", r.get("name", "—"))
        print(f"  [{i}]  room={r.get('room_id')}  host={host}  topic={topic}")

    if not room_list:
        print("No rooms available.")
        raise SystemExit

    # ── pick a room ──────────────────────────────────────────────
    choice = input("\n[?] Enter room number to explore (or 1) : ").strip()
    idx    = int(choice) - 1 if choice.isdigit() else 0
    target = room_list[min(idx, len(room_list) - 1)]

    room_id    = str(target["room_id"])
    session_id = str(target["session_id"])
    print(f"\nEntering room {room_id} …")

    # ── enter ────────────────────────────────────────────────────
    try:
        enter = client.rooms.enter_room(room_id, session_id)
        pprint("ENTER ROOM", enter)

        cfg = client.rooms.get_room_config(room_id, session_id)
        pprint("ROOM CONFIG", cfg)

        audiences = client.rooms.get_audiences(room_id, session_id, limit=10)
        pprint("AUDIENCES", audiences)

        mic = client.rooms.get_mic_state()
        pprint("MIC STATE", mic)

        gifts = client.rooms.get_gift_rankings(room_id, session_id, limit=5)
        pprint("GIFT RANKINGS", gifts)

    except TalkinError as e:
        print(f"\n[!] Error: {e}")
    finally:
        client.rooms.exit_room(room_id, session_id)
        print(f"\nExited room {room_id}.")

    # ── summary ──────────────────────────────────────────────────
    client.console.summary() # type: ignore
