#!/usr/bin/env python3
# Builds weather.json for the pi-clock display.
# Run on tahoe via cron every minute:
#   * * * * * /usr/bin/python3 /root/pi-clock/update-weather.py

import json, os, subprocess, sys

SCRIPT_DIR    = os.path.dirname(os.path.abspath(__file__))
OUT           = os.path.join(SCRIPT_DIR, "weather.json")
BTC_BLOCKS    = "/vault/btc/ckpool/logs/pool/blocks"
BCH_BLOCKS    = "/vault/bch/asic/logs/pool/blocks"


def count_blocks(directory):
    if not os.path.isdir(directory):
        return 0
    return len(os.listdir(directory))


# ── Pool stats from postgres ──────────────────────────────────────────────────

def query_pool(db):
    sql = 'SELECT hashrate1m, bestshare FROM "PoolStats" ORDER BY id DESC LIMIT 1;'
    r = subprocess.run(
        ["psql", "-U", "postgres", db, "-t", "-A", "-F", "\t", "-c", sql],
        capture_output=True, text=True
    )
    if r.returncode != 0 or not r.stdout.strip():
        return None, None
    parts = r.stdout.strip().split("\t")
    return int(parts[0]), int(parts[1])

def fmt_hashrate(h):
    if h >= 1e15: return f"{h/1e15:.2f}PH"
    if h >= 1e12: return f"{h/1e12:.2f}TH"
    if h >= 1e9:  return f"{h/1e9:.2f}GH"
    if h >= 1e6:  return f"{h/1e6:.2f}MH"
    return f"{h}H"

def fmt_difficulty(d):
    if d >= 1e15: return f"{d/1e15:.2f}P"
    if d >= 1e12: return f"{d/1e12:.2f}T"
    if d >= 1e9:  return f"{d/1e9:.2f}G"
    if d >= 1e6:  return f"{d/1e6:.2f}M"
    return str(int(d))


# ── Main ──────────────────────────────────────────────────────────────────────

btc_hr, btc_bs = query_pool("ckstats_btc")
bch_hr, bch_bs = query_pool("ckstats_bch")

btc_display = f"BTC {fmt_hashrate(btc_hr)} · Best {fmt_difficulty(btc_bs)}" if btc_hr else "BTC --"
bch_display = f"BCH {fmt_hashrate(bch_hr)} · Best {fmt_difficulty(bch_bs)}" if bch_hr else "BCH --"

existing = {}
if os.path.exists(OUT):
    try:
        with open(OUT) as f:
            existing = json.load(f)
    except Exception:
        pass

weather = existing.get("weather", "--")
existing["btc_display"] = btc_display
existing["bch_display"] = bch_display
existing["display"]     = f"{weather} · {btc_display}"

# ── Block detection ───────────────────────────────────────────────────────────
btc_count = count_blocks(BTC_BLOCKS)
bch_count = count_blocks(BCH_BLOCKS)

# On first run, seed the seen counts so we don't false-alarm on startup
btc_seen = existing.get("btc_blocks_seen", btc_count)
bch_seen = existing.get("bch_blocks_seen", bch_count)

# Previous bestshare values (0 on first run — won't trigger since current will also be small)
prev_btc_bs = existing.get("prev_btc_bs", 0)
prev_bch_bs = existing.get("prev_bch_bs", 0)

if "block_chain" not in existing:
    # Method 1: new file in blocks directory
    if btc_count > btc_seen:
        existing["block_chain"] = "BTC"
    elif bch_count > bch_seen:
        existing["block_chain"] = "BCH"
    # Method 2: bestshare reset to 0 after holding a substantial value
    elif btc_bs == 0 and prev_btc_bs > 1_000_000_000:
        existing["block_chain"] = "BTC"
    elif bch_bs == 0 and prev_bch_bs > 1_000_000_000:
        existing["block_chain"] = "BCH"

existing["btc_blocks_seen"] = btc_count
existing["bch_blocks_seen"] = bch_count
existing["prev_btc_bs"] = btc_bs if btc_bs is not None else prev_btc_bs
existing["prev_bch_bs"] = bch_bs if bch_bs is not None else prev_bch_bs

print(existing["display"])
print(bch_display)
with open(OUT, "w") as f:
    json.dump(existing, f)
