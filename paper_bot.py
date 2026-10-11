#!/usr/bin/env python3
"""Crypto Pulse paper-trading bot.

Pulls live prices/candles from the Crypto.com Exchange public API, generates
EMA-cross + RSI signals, and trades a simulated (paper) account long and short
with stop-loss / take-profit. No API key needed; no real money is touched.

Usage:
    python paper_bot.py --symbols BTCUSDT ETHUSDT
    python paper_bot.py --symbols BTC_USDT ETH_USDT --mode long --interval 30
    python paper_bot.py --symbols BTCUSDT --once        # single pass, e.g. for cron/Actions
"""
import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone

import requests

BASE = "https://api.crypto.com/exchange/v1/public"
FEE = 0.001  # 0.1% per side


# ---------- helpers ----------
def norm(sym: str) -> str:
    """BTCUSDT / btc-usdt -> BTC_USDT"""
    s = sym.upper().replace("-", "_").replace("/", "_")
    if "_" in s:
        return s
    for quote in ("USDT", "USDC", "USD", "BTC", "ETH"):
        if s.endswith(quote) and len(s) > len(quote):
            return f"{s[:-len(quote)]}_{quote}"
    return s


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def log(msg: str) -> None:
    print(f"[{now()}] {msg}", flush=True)


def get_candles(inst: str, timeframe: str, count: int = 100):
    r = requests.get(
        f"{BASE}/get-candlestick",
        params={"instrument_name": inst, "timeframe": timeframe, "count": count},
        timeout=15,
    )
    r.raise_for_status()
    body = r.json()
    if body.get("code", 0) != 0:
        raise RuntimeError(f"API error for {inst}: {body}")
    data = body["result"]["data"]
    data.sort(key=lambda c: c["t"])
    return [float(c["c"]) for c in data]


def ema(values, period):
    k = 2 / (period + 1)
    out, e = [], values[0]
    for v in values:
        e = v * k + e * (1 - k)
        out.append(e)
    return out


def rsi(values, period=14):
    if len(values) <= period:
        return 50.0
    gains = losses = 0.0
    for i in range(1, period + 1):
        d = values[i] - values[i - 1]
        gains += max(d, 0)
        losses += max(-d, 0)
    avg_g, avg_l = gains / period, losses / period
    for i in range(period + 1, len(values)):
        d = values[i] - values[i - 1]
        avg_g = (avg_g * (period - 1) + max(d, 0)) / period
        avg_l = (avg_l * (period - 1) + max(-d, 0)) / period
    if avg_l == 0:
        return 100.0
    return 100 - 100 / (1 + avg_g / avg_l)


def signal(closes, rsi_low, rsi_high):
    """Return 'long', 'short' or None."""
    if len(closes) < 30:
        return None
    fast, slow = ema(closes, 9), ema(closes, 21)
    r = rsi(closes)
    crossed_up = fast[-2] <= slow[-2] and fast[-1] > slow[-1]
    crossed_dn = fast[-2] >= slow[-2] and fast[-1] < slow[-1]
    if crossed_up or r < rsi_low:
        return "long"
    if crossed_dn or r > rsi_high:
        return "short"
    return None


# ---------- paper account ----------
def load_state(path, balance):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {"balance": balance, "start": balance, "positions": {}, "history": []}


def save_state(path, state):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2)
    os.replace(tmp, path)


def equity(state, prices):
    total = state["balance"]
    for sym, p in state["positions"].items():
        px = prices.get(sym, p["entry"])
        pnl = (px - p["entry"]) * p["qty"] * (1 if p["side"] == "long" else -1)
        total += p["margin"] + pnl
    return total


def open_pos(state, sym, side, price, size_frac, sl, tp):
    notional = equity(state, {}) * size_frac
    notional = min(notional, state["balance"] / (1 + FEE))
    if notional < 10:
        return
    qty = notional / price
    state["balance"] -= notional * (1 + FEE)
    sign = 1 if side == "long" else -1
    state["positions"][sym] = {
        "side": side, "entry": price, "qty": qty, "margin": notional,
        "sl": price * (1 - sign * sl), "tp": price * (1 + sign * tp),
        "opened": now(),
    }
    log(f"OPEN {side.upper():5} {sym} @ {price:.4f}  qty={qty:.6f}  "
        f"SL={state['positions'][sym]['sl']:.4f}  TP={state['positions'][sym]['tp']:.4f}")


def close_pos(state, sym, price, reason):
    p = state["positions"].pop(sym)
    sign = 1 if p["side"] == "long" else -1
    pnl = (price - p["entry"]) * p["qty"] * sign
    pnl -= p["margin"] * FEE
    state["balance"] += p["margin"] + pnl
    state["history"].append({
        "symbol": sym, "side": p["side"], "entry": p["entry"], "exit": price,
        "pnl": pnl, "reason": reason, "opened": p["opened"], "closed": now(),
    })
    tag = {"TAKE PROFIT": "✅", "STOP LOSS": "🛑"}.get(reason, "↩️")
    log(f"{tag} CLOSE {p['side'].upper():5} {sym} @ {price:.4f}  "
        f"{reason}  PnL={pnl:+.2f} USDT")


# ---------- main loop ----------
def step(args, state, symbols):
    prices = {}
    for sym in symbols:
        try:
            closes = get_candles(sym, args.timeframe)
        except Exception as e:  # keep running on transient errors
            log(f"! {sym}: {e}")
            continue
        price = closes[-1]
        prices[sym] = price
        pos = state["positions"].get(sym)

        if pos:
            long = pos["side"] == "long"
            if (long and price >= pos["tp"]) or (not long and price <= pos["tp"]):
                close_pos(state, sym, price, "TAKE PROFIT")
            elif (long and price <= pos["sl"]) or (not long and price >= pos["sl"]):
                close_pos(state, sym, price, "STOP LOSS")
            else:
                sig = signal(closes, args.rsi_low, args.rsi_high)
                if sig and sig != pos["side"]:
                    close_pos(state, sym, price, "SIGNAL REVERSAL")
                    pos = None
            if sym in state["positions"]:
                continue

        sig = signal(closes, args.rsi_low, args.rsi_high)
        if sig and (args.mode in ("both", sig)) and sym not in state["positions"]:
            open_pos(state, sym, sig, price, args.size, args.stop_loss, args.take_profit)

    eq = equity(state, prices)
    state["equity"] = eq
    state["updated"] = now()
    pct = (eq / state["start"] - 1) * 100
    log(f"Equity {eq:,.2f} USDT ({pct:+.2f}%)  cash={state['balance']:,.2f}  "
        f"open={len(state['positions'])}  trades={len(state['history'])}")


def main():
    ap = argparse.ArgumentParser(description="Crypto Pulse paper-trading bot")
    ap.add_argument("--symbols", nargs="+", default=["BTCUSDT", "ETHUSDT"])
    ap.add_argument("--mode", choices=["both", "long", "short"], default="both")
    ap.add_argument("--timeframe", default="5m", help="1m 5m 15m 30m 1h 4h 1D")
    ap.add_argument("--interval", type=int, default=60, help="seconds between checks")
    ap.add_argument("--balance", type=float, default=10000.0, help="starting paper USDT")
    ap.add_argument("--size", type=float, default=0.2, help="fraction of equity per trade")
    ap.add_argument("--stop-loss", type=float, default=0.02, help="e.g. 0.02 = 2%%")
    ap.add_argument("--take-profit", type=float, default=0.04, help="e.g. 0.04 = 4%%")
    ap.add_argument("--rsi-low", type=float, default=40, help="long below this (aggressive=40)")
    ap.add_argument("--rsi-high", type=float, default=60, help="short above this (aggressive=60)")
    ap.add_argument("--state", default="bot_state.json")
    ap.add_argument("--once", action="store_true", help="run one pass and exit")
    args = ap.parse_args()

    symbols = [norm(s) for s in args.symbols]
    state = load_state(args.state, args.balance)
    log(f"Crypto Pulse bot started | {', '.join(symbols)} | mode={args.mode} "
        f"| {args.timeframe} | SL {args.stop_loss:.1%} TP {args.take_profit:.1%}")
    try:
        while True:
            step(args, state, symbols)
            save_state(args.state, state)
            if args.once:
                break
            time.sleep(args.interval)
    except KeyboardInterrupt:
        save_state(args.state, state)
        log("Stopped. State saved.")
        sys.exit(0)


if __name__ == "__main__":
    main()
