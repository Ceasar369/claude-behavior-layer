#!/usr/bin/env python3
"""schedule.py — a launch page the drive fires itself, with no press.

While a stage runs, the assistant driving a plan prepares the next stage's
launch page, as the launch skill writes one: its own launch.json. One key
more schedules it, naming the stage whose close fires it.

  {"after": "B", "rows": [{"name": "...", "message": "..."}]}

The page is today's, drawn by launch-page.py. Scheduled, a press there
launches nothing. I change any row until it fires.
Planned pane moves require my Launch press. A fire unschedules that page
and stops, so it can never move an existing session on its own.

  schedule.py fire NN        launch session NN's launch page, scheduled or not

A fire takes the key out, then posts the page's rows to the page's own
take, as my press of Launch does. First each row gets what the page gives
it as it draws, by the one rule in lib/launch.py, fill and settle: its
number, and a place standing in iTerm's layout now. An account, a model
or an effort it leaves unset is read as its pane opens.

The layout comes from iTerm's API, which answers from inside a session.

A row that never claims its number launches again, once the pane it
opened is closed, three tries in all, as .claude/rules/thinking.md gives
a failing step. One whose session waits at a dialog never launches
again: only my hand answers it, so its pane stays. A row failing three
times, or left at its dialog, stays on the page, failed, as any failed
row does.

The fire waits for every row, then prints one line per row, and exits 1
unless every row launched. A fire ended by a signal fails the rows still
booting, as a fresh 1100 does, so the page is not left locked.
"""

import argparse
import json
import os
import re
import signal
import subprocess
import sys
import threading

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import finish  # noqa: E402
import iterm  # noqa: E402
import launch  # noqa: E402
import page  # noqa: E402
import panes  # noqa: E402
import registry  # noqa: E402

# A row's launches, its first among them: a failing step's tries.
TRIES = finish.TRIES


def unschedule(lp, nn: str) -> None:
    """Take the key out of NN's launch.json. Its rows stay as they are."""
    with lp.LOCK:
        try:
            with open(lp.path(nn)) as f:
                d = json.load(f)
        except (OSError, ValueError):
            return
        if not isinstance(d, dict) or lp.AFTER not in d:
            return
        del d[lp.AFTER]
        with open(lp.path(nn), "w") as f:
            json.dump(d, f, indent=2)
            f.write("\n")


# ---- the fire --------------------------------------------------------------------

def waits(n: str) -> bool:
    """Whether the session booted to claim number N, which never did, waits
    at a dialog. Its boot line asks for N, so its process names it."""
    live = {int(d["pid"]): d for d in registry.claude_records().values()}
    if not live:
        return False
    out = subprocess.run(["/bin/ps", "-ww", "-o", "pid=,args=", "-p", ",".join(map(str, live))],
                         capture_output=True, text=True).stdout
    for line in out.splitlines():
        pid, _, args = line.strip().partition(" ")
        if re.search(rf"/0-session-start {n}\b", args) and live.get(int(pid), {}).get("status") == "waiting":
            return True
    return False


def press(lp, nn: str, rows: list, seen: list) -> str:
    """Post `rows` to the page's own take, as my press of Launch does, then
    wait until each has claimed its number or failed. The page's banner,
    when nothing launched. A row in the file and in `seen`, never posted,
    leaves the file, as a row I delete on the page does."""
    rec = registry.entries().get(nn) or {}
    tree = iterm.tree()
    if not tree:
        return "Nothing launched. iTerm did not answer."
    starter = panes.pane(rec) if rec else ""
    launch.fill(rows, lp.free(nn, rows), launch.home(tree, starter), launch.browsers_named(nn, tree), nn)
    launch.settle(rows, tree, starter)
    banner, before = [""], set(threading.enumerate())
    lp.take_for(nn, banner)({"act": ["launch"], "rows": [json.dumps(rows)], "seen": [json.dumps(seen)]})
    # The take launches on threads of its own, and each pane's wait on one more.
    while mine := [t for t in threading.enumerate() if t not in before]:
        for t in mine:
            t.join()
    return banner[0]


def tag(r: dict) -> str:
    return f"browser {r.get('site')}" if launch.browser(r) else str(r.get("n"))


def sort(rows: list, left: dict, n: int, lines: dict, kept: list, opened: dict) -> list:
    """Each row's line after try N, as the page left it: launched, kept on
    the page, or failed. Returns the failed rows to launch again, each pane
    they opened closed. After the last try, a failed row keeps its pane."""
    again = []
    for r in rows:
        got = left.get(r["uid"])
        if got is None:
            lines[r["uid"]] = f"{tag(r)} launched" + (f", on try {n}" if n > 1 else "")
        elif not str(got.get("status", "")).startswith("failed"):
            kept.append(got)
            lines[r["uid"]] = f"{tag(r)} not launched"
        elif str(got.get("status", "")).startswith("failed: arrangement"):
            kept.append(got)
            lines[r["uid"]] = f"{tag(r)} {got['status']}"
        elif not launch.browser(got) and waits(got["n"]):
            kept.append(got)
            lines[r["uid"]] = f"{tag(r)} waits at a dialog in its pane, for your hand"
        elif n < TRIES:
            if opened.get(str(r["uid"])):
                iterm.close(opened[str(r["uid"])])
            again.append(got)
        else:
            lines[r["uid"]] = f"{tag(r)} failed {TRIES} times: {str(got.get('status', ''))[len('failed: '):]}"
    return again


def fire(nn: str, lp=None) -> tuple:
    """Launch session NN's launch page, as my press of Launch does. Each
    row's line, in launch order, and whether every row launched."""
    lp = lp or page.tool("launch-page")
    unschedule(lp, nn)
    # A planned move is applied only by the user's own Launch press.
    if lp.moves(nn):
        return [f"Session {nn}'s planned moves need your press of Launch."], False
    with lp.LOCK:
        rows = lp.load(nn)
    if not rows:
        return [f"Session {nn}'s launch page holds no row."], False
    # The page's go() keeps each pane it opens to itself. Its place is
    # watched, so a pane opened for a row that failed can be closed.
    opened, place = {}, launch.place

    def placed(r, made, windows):
        opened[str(r["uid"])] = place(r, made, windows)
        return opened[str(r["uid"])]

    launch.place = placed
    try:
        said = press(lp, nn, rows, [r["uid"] for r in rows])
        if said:
            return [said], False
        left = {r["uid"]: r for r in lp.read(nn)}
        lines, kept = {}, [r for u, r in left.items() if u not in {s["uid"] for s in rows}]
        again = sort(rows, left, 1, lines, kept, opened)
        for n in range(2, TRIES + 1):
            if not again:
                break
            ids = {str(r["uid"]) for r in again}
            for r in again:
                r.pop("status", None)
                a = r.get("at") or {}
                u = str(a.get("anchor", ""))
                # A row launched, or left at a dialog, keeps its pane: a row
                # hanging off it lands beside that pane again.
                if u.startswith("r:") and u[2:] not in ids and opened.get(u[2:]):
                    r["at"] = {"anchor": f"p:{opened[u[2:]]}", "side": a.get("side", "right")}
            said = press(lp, nn, again, list(left))
            if said:
                for r in again:
                    lines[r["uid"]] = f"{tag(r)} failed, then nothing launched: {said}"
                break
            left = {r["uid"]: r for r in lp.read(nn)}
            again = sort(again, left, n, lines, kept, opened)
        # A take after the first leaves out every row it did not launch.
        # Each comes back, as it stood.
        with lp.LOCK:
            now = lp.load(nn)
            back = [r for r in kept if r["uid"] not in {s["uid"] for s in now}]
            if back:
                lp.save(nn, now + back)
        return [lines[r["uid"]] for r in rows], all(lines[r["uid"]].startswith(f"{tag(r)} launched")
                                                     for r in rows)
    finally:
        launch.place = place


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="verb", required=True)
    sub.add_parser("fire").add_argument("nn")
    args = ap.parse_args()
    nn = f"{int(args.nn):02d}"
    lp = page.tool("launch-page")

    # A signal can land while this thread holds the page's lock, so another
    # thread fails the rows still booting.
    def cut(*_):
        threading.Thread(target=lambda: (lp.unboot(nn), os._exit(1)), daemon=True).start()

    for sig in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
        signal.signal(sig, cut)
    lines, every = fire(nn, lp)
    print("\n".join(lines))
    sys.exit(0 if every else 1)


if __name__ == "__main__":
    main()
