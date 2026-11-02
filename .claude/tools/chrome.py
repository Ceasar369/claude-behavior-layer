#!/usr/bin/env python3
"""chrome.py — which Chrome profile a session on Chrome's account can drive, and how.

  chrome.py account                     the account that drives my Chrome
  chrome.py profiles                    every profile holding the extension
  chrome.py profile "Work"              one profile, by label or directory

Each line names a profile's directory, its label, its browser ID and the
Claude account its extension is signed into. The browser ID is the
deviceId that list_connected_browsers shows and select_browser takes.

A session reaches a profile only through an extension signed into its own
Claude account, and only one account drives my Chrome: the one this Mac's
list names, lib/accounts.py's. So `profile` refuses any profile that
account cannot reach, and says why. Otherwise it adds the line that opens
that profile's window, which connects its extension.

Everything is read from Chrome's own files, and nothing is written. Each
profile's extension store is LevelDB, read here as LevelDB reads it: the
.log record by record, each .ldb block by block. A block is Snappy
compressed, and keeps each key as only what differs from the key before
it, so bridgeDeviceId can sit on disk as viceId. A key's newest write wins.
"""

import argparse
import glob
import json
import os
import sys

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import accounts  # noqa: E402

CHROME = os.path.expanduser("~/Library/Application Support/Google/Chrome")
EXTENSION = "fcoeoabgfenejglbffodgkkbkcdhcgfn"
# A .log is written in blocks of this size.
LOG_BLOCK = 32768
# The last eight bytes of every finished .ldb.
TABLE_END = (0xdb4775248b80fb57).to_bytes(8, "little")


def varint(b: bytes, i: int) -> tuple:
    """The number packed at I, seven bits to a byte, and where it ends."""
    n = shift = 0
    while True:
        c, i = b[i], i + 1
        n |= (c & 0x7F) << shift
        if c < 0x80:
            return n, i
        shift += 7


def unsnappy(b: bytes) -> bytes:
    """A Snappy block, unpacked: runs of bytes, and copies of what came before."""
    i = varint(b, 0)[1]
    out = bytearray()
    while i < len(b):
        tag, i = b[i], i + 1
        if tag & 3 == 0:
            n = tag >> 2
            if n >= 60:
                n, i = int.from_bytes(b[i:i + n - 59], "little"), i + n - 59
            out += b[i:i + n + 1]
            i += n + 1
            continue
        if tag & 3 == 1:
            n, back, i = ((tag >> 2) & 7) + 4, ((tag >> 5) << 8) | b[i], i + 1
        else:
            width = 2 if tag & 3 == 2 else 4
            n, back, i = (tag >> 2) + 1, int.from_bytes(b[i:i + width], "little"), i + width
        # A copy longer than its distance back repeats itself.
        start = len(out) - back
        out += (out[start:start + n] * (n // back + 1))[:n]
    return bytes(out)


def block(data: bytes, handle: bytes) -> bytes:
    """The block HANDLE points at, by its offset and size, unpacked."""
    at, j = varint(handle, 0)
    size = varint(handle, j)[0]
    raw = data[at:at + size]
    return unsnappy(raw) if data[at + size] == 1 else raw


def entries(b: bytes):
    """Each key and value a block holds, each key rebuilt from the one before it."""
    end = len(b) - 4 - 4 * int.from_bytes(b[-4:], "little")
    i, key = 0, b""
    while i < end:
        shared, i = varint(b, i)
        own, i = varint(b, i)
        size, i = varint(b, i)
        key, i = key[:shared] + b[i:i + own], i + own
        yield key, b[i:i + size]
        i += size


def table(path: str):
    """Each write an .ldb holds: its key, number, kind and value. A table
    Chrome is still writing holds none yet."""
    with open(path, "rb") as f:
        data = f.read()
    if data[-8:] != TABLE_END:
        return
    footer = data[-48:]
    index = block(data, footer[varint(footer, varint(footer, 0)[1])[1]:])
    for _, handle in entries(index):
        for key, value in entries(block(data, handle)):
            stamp = int.from_bytes(key[-8:], "little")
            yield key[:-8], stamp >> 8, stamp & 0xFF, value


def log(path: str):
    """Each write a .log holds, as table() yields them. A record Chrome is
    still writing ends it."""
    with open(path, "rb") as f:
        data = f.read()
    i, record = 0, b""
    while i + 7 <= len(data):
        room = LOG_BLOCK - i % LOG_BLOCK
        size, kind = int.from_bytes(data[i + 4:i + 6], "little"), data[i + 6]
        if room < 7 or not kind:  # the rest of the block is padding
            i += room
            continue
        piece, i = data[i + 7:i + 7 + size], i + 7 + size
        if len(piece) < size:
            return
        record = piece if kind in (1, 2) else record + piece
        if kind in (1, 4):
            yield from batch(record)


def batch(b: bytes):
    """Each write one .log record carries, numbered on from its first."""
    first, count, i = int.from_bytes(b[:8], "little"), int.from_bytes(b[8:12], "little"), 12
    for k in range(count):
        kind, i = b[i], i + 1
        n, i = varint(b, i)
        key, i = b[i:i + n], i + n
        value = b""
        if kind == 1:
            n, i = varint(b, i)
            value, i = b[i:i + n], i + n
        yield key, first + k, kind, value


def stored(store: str) -> dict:
    """What the extension keeps in STORE: each key's newest value, as JSON."""
    newest = {}
    for path in glob.glob(os.path.join(store, "*.ldb")) + glob.glob(os.path.join(store, "*.log")):
        try:
            writes = list((table if path.endswith(".ldb") else log)(path))
        except (OSError, ValueError, IndexError):  # gone since the glob, or damaged
            continue
        for key, number, kind, value in writes:
            if number > newest.get(key, (-1,))[0]:
                newest[key] = (number, kind, value)
    out = {}
    for key, (_, kind, value) in newest.items():
        if kind != 1:  # a delete
            continue
        try:
            out[key.decode()] = json.loads(value)
        except ValueError:
            continue
    return out


def profiles() -> list:
    """Every profile, in Chrome's order, with what its extension holds."""
    with open(os.path.join(CHROME, "Local State"), encoding="utf-8") as f:
        cache = json.load(f).get("profile", {}).get("info_cache", {})
    known = accounts.logins()
    rows = []
    for directory, info in cache.items():
        store = os.path.join(CHROME, directory, "Local Extension Settings", EXTENSION)
        held = os.path.isdir(store)
        kept = stored(store) if held else {}
        rows.append({"directory": directory,
                     "label": info.get("name", ""),
                     "extension": held,
                     "browser": str(kept.get("bridgeDeviceId", "")),
                     "account": known.get(str(kept.get("accountUuid", "")), ("", ""))[0]})
    return sorted(rows, key=lambda r: (r["directory"] != "Default", r["directory"]))


def line(row: dict) -> str:
    account = f"account {row['account']}" if row["account"] else "no account"
    return f"{row['directory']:<11} {row['label']:<17} {row['browser'] or '-':<37} {account}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("account")
    sub.add_parser("profiles")
    one = sub.add_parser("profile")
    one.add_argument("name")
    args = parser.parse_args()

    if args.cmd == "account":
        print(accounts.CHROME)
        return

    rows = profiles()
    if args.cmd == "profiles":
        for row in rows:
            if row["extension"]:
                print(line(row))
        return

    wanted = args.name.strip().lower()
    row = next((r for r in rows if wanted in (r["directory"].lower(), r["label"].lower())), None)
    if not row:
        sys.exit(f"Refused: no Chrome profile is named {args.name}.")
    if not row["extension"]:
        sys.exit(f"Refused: {row['label']} has no Claude extension. Install it there first.")
    if row["account"] != accounts.CHROME:
        email = next((e for n, e in accounts.logins().values() if n == accounts.CHROME), f"account {accounts.CHROME}")
        held = f"account {row['account']}" if row["account"] else "no Claude account"
        sys.exit(f"Refused: {row['label']}'s extension is signed into {held}. "
                 f"Sign it into {email}'s Claude login.")
    print(line(row))
    print(f'open -na "Google Chrome" --args --profile-directory="{row["directory"]}"')


if __name__ == "__main__":
    main()
