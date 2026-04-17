"""
talkin.console — real-time request tracker and session summary display.

Usage::

    from talkin import TalkinClient

    client = TalkinClient(api_key="...", console=True)

    # ... make API calls ...

    client.console.summary()
"""

from __future__ import annotations

import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from .constants import PLAN_RATE_LIMITS, PLAN_LABELS

# ── ANSI colour helpers ────────────────────────────────────────────

_RESET  = "\033[0m"
_BOLD   = "\033[1m"
_DIM    = "\033[2m"
_RED    = "\033[91m"
_GREEN  = "\033[92m"
_YELLOW = "\033[93m"
_BLUE   = "\033[94m"
_MAGENTA= "\033[95m"
_CYAN   = "\033[96m"
_WHITE  = "\033[97m"

def _c(text: str, *codes: str) -> str:
    return "".join(codes) + str(text) + _RESET

def _status_color(status: int) -> str:
    if 200 <= status < 300:
        return _GREEN
    if 400 <= status < 500:
        return _YELLOW
    return _RED

def _time_color(ms: float) -> str:
    if ms > 1000:
        return _RED
    if ms > 500:
        return _YELLOW
    return _DIM + _WHITE


# ── Data models ────────────────────────────────────────────────────

@dataclass
class RequestEntry:
    ts:        str
    method:    str
    endpoint:  str
    status:    int
    ms:        float
    encrypted: bool
    error:     Optional[str] = None

    @property
    def ok(self) -> bool:
        return self.error is None and 200 <= self.status < 300


@dataclass
class CryptoEntry:
    ts:        str
    operation: str
    ms:        float
    error:     Optional[str] = None

    @property
    def ok(self) -> bool:
        return self.error is None


# ── Console ────────────────────────────────────────────────────────

class Console:
    """
    Attaches to TalkinClient and tracks every API request + crypto op.

    Parameters
    ----------
    live    : Print each call as it happens (default True)
    stream  : Output stream (default sys.stdout)
    """

    def __init__(self, live: bool = True, stream=None):
        self.live:   bool = live
        self._out         = stream or sys.stdout
        self.requests: List[RequestEntry] = []
        self.crypto:   List[CryptoEntry]  = []

        self._plan:  Optional[str] = None
        self._used:  int           = 0
        self._limit: Optional[int] = None
        self._session_start        = datetime.now()

    # ── plan info ──────────────────────────────────────────────────

    def set_plan(self, plan: str, used: int, limit: Optional[int] = None):
        self._plan  = plan.lower()
        self._used  = used
        self._limit = limit if limit is not None else PLAN_RATE_LIMITS.get(self._plan)

    # ── recording ──────────────────────────────────────────────────

    def record_request(
        self,
        method:    str,
        endpoint:  str,
        status:    int,
        ms:        float,
        encrypted: bool = False,
        error:     Optional[str] = None,
    ):
        entry = RequestEntry(
            ts=datetime.now().strftime("%H:%M:%S"),
            method=method,
            endpoint=endpoint,
            status=status,
            ms=ms,
            encrypted=encrypted,
            error=error,
        )
        self.requests.append(entry)
        if self.live:
            self._print_request(entry)

    def record_crypto(
        self,
        operation: str,
        ms:        float,
        error:     Optional[str] = None,
    ):
        entry = CryptoEntry(
            ts=datetime.now().strftime("%H:%M:%S"),
            operation=operation,
            ms=ms,
            error=error,
        )
        self.crypto.append(entry)
        if self.live:
            self._print_crypto(entry)

    # ── live output ────────────────────────────────────────────────

    def _print_request(self, e: RequestEntry):
        method  = _c(f"{e.method:<4}", _CYAN if e.method == "GET" else _YELLOW)
        status  = _c(str(e.status), _status_color(e.status))
        timing  = _c(f"{e.ms:>6.0f}ms", _time_color(e.ms))
        enc     = _c(" [ENC]", _MAGENTA) if e.encrypted else ""
        err     = _c(f"  !! {e.error}", _RED) if e.error else ""
        ep      = _c(f"{e.endpoint:<52}", _DIM)
        line    = f"  {_c(e.ts, _DIM)}  {method}  {ep}  {status}  {timing}{enc}{err}"
        print(line, file=self._out)

    def _print_crypto(self, e: CryptoEntry):
        op     = _c(f"{'CRYP':<4}", _MAGENTA)
        label  = _c(f"{e.operation:<52}", _DIM)
        state  = _c("OK ", _GREEN) if e.ok else _c("ERR", _RED)
        timing = _c(f"{e.ms:>6.0f}ms", _time_color(e.ms))
        err    = _c(f"  !! {e.error}", _RED) if e.error else ""
        line   = f"  {_c(e.ts, _DIM)}  {op}  {label}  {state}  {timing}{err}"
        print(line, file=self._out)

    # ── summary table ──────────────────────────────────────────────

    def summary(self):
        W = 70
        bar = "─" * W

        def row(left: str, right: str = ""):
            pad = W - 2 - len(left) - len(right)
            return f"│ {left}{' ' * max(pad, 1)}{right} │"

        def _plain(s: str) -> str:
            import re
            return re.sub(r"\033\[[0-9;]*m", "", s)

        def row_color(left_colored: str, right_colored: str = ""):
            plain_len = len(_plain(left_colored)) + len(_plain(right_colored))
            pad = W - 2 - plain_len
            return f"│ {left_colored}{' ' * max(pad, 1)}{right_colored} │"

        reqs        = self.requests
        total_reqs  = len(reqs)
        ok_reqs     = sum(1 for r in reqs if r.ok)
        err_reqs    = total_reqs - ok_reqs
        enc_reqs    = sum(1 for r in reqs if r.encrypted)
        avg_ms      = (sum(r.ms for r in reqs) / total_reqs) if reqs else 0
        min_ms      = min((r.ms for r in reqs), default=0)
        max_ms      = max((r.ms for r in reqs), default=0)

        crypto_ops  = len(self.crypto)
        crypto_ok   = sum(1 for c in self.crypto if c.ok)
        crypto_avg  = (sum(c.ms for c in self.crypto) / crypto_ops) if crypto_ops else 0

        duration    = (datetime.now() - self._session_start).total_seconds()

        out = self._out
        print(f"\n┌{'─' * W}┐", file=out)
        title = _c(" TALKIN SDK", _BOLD + _CYAN) + _c("  ·  SESSION SUMMARY", _DIM)
        print(row_color(title), file=out)
        print(f"├{'─' * W}┤", file=out)

        # plan + rate bar
        if self._plan:
            plan_label = PLAN_LABELS.get(self._plan, self._plan.title())
            limit      = self._limit or PLAN_RATE_LIMITS.get(self._plan, 0)
            used       = self._used
            filled     = int((used / limit) * 20) if limit else 0
            bar_color  = _RED if filled >= 18 else (_YELLOW if filled >= 12 else _GREEN)
            rate_bar   = _c("█" * filled, bar_color) + _c("░" * (20 - filled), _DIM)
            plan_str   = _c(plan_label, _CYAN + _BOLD)
            used_str   = _c(f"{used}", bar_color)
            lim_str    = _c(f"/{limit} per min", _DIM)
            print(row_color(
                f"  Plan : {plan_str}   Rate : {rate_bar}  {used_str}{lim_str}"
            ), file=out)
            print(f"├{'─' * W}┤", file=out)

        # stats
        sess  = _c(f"{duration:.1f}s", _DIM)
        t_ok  = _c(str(ok_reqs), _GREEN)
        t_err = _c(str(err_reqs), _RED if err_reqs else _DIM)
        t_enc = _c(str(enc_reqs), _MAGENTA)
        print(row_color(
            f"  Requests   : {_c(str(total_reqs), _BOLD)}   "
            f"OK: {t_ok}  Err: {t_err}  Encrypted: {t_enc}   "
            f"Session: {sess}"
        ), file=out)
        t_avgt = _c(f"{avg_ms:.0f}ms", _time_color(avg_ms))
        t_mint = _c(f"{min_ms:.0f}ms", _GREEN)
        t_maxt = _c(f"{max_ms:.0f}ms", _time_color(max_ms))
        print(row_color(
            f"  API timing : avg {t_avgt}  min {t_mint}  max {t_maxt}"
        ), file=out)
        c_ok = _c(str(crypto_ok), _GREEN)
        c_avg = _c(f"{crypto_avg:.0f}ms", _DIM)
        print(row_color(
            f"  Crypto ops : {_c(str(crypto_ops), _BOLD)}   OK: {c_ok}   avg {c_avg}"
        ), file=out)

        if not reqs:
            print(f"└{'─' * W}┘\n", file=out)
            return

        # request log table
        print(f"├{'─' * W}┤", file=out)
        hdr = (
            _c(f"{'#':<4}", _DIM) +
            _c(f"{'Method':<7}", _DIM) +
            _c(f"{'Endpoint':<44}", _DIM) +
            _c(f"{'St':<5}", _DIM) +
            _c(f"{'Time':>7}", _DIM) +
            _c("  Flags", _DIM)
        )
        print(row_color(f"  {hdr}"), file=out)
        print(f"├{'─' * W}┤", file=out)

        for i, r in enumerate(reqs, 1):
            num    = _c(f"{i:<4}", _DIM)
            method = _c(f"{r.method:<7}", _CYAN if r.method == "GET" else _YELLOW)
            ep     = r.endpoint[:43].ljust(44)
            ep_c   = _c(ep, _DIM if r.ok else _RED)
            st     = _c(f"{r.status:<5}", _status_color(r.status))
            ms_c   = _c(f"{r.ms:>6.0f}ms", _time_color(r.ms))
            flags  = (_c(" ENC", _MAGENTA) if r.encrypted else "    ")
            flags += (_c(" ERR", _RED) if not r.ok else "")
            print(row_color(f"  {num}{method}{ep_c}{st}{ms_c}{flags}"), file=out)

        print(f"└{'─' * W}┘\n", file=out)
