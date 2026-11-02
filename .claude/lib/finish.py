"""finish.py — how a session I drive finished, read one way for all who ask.

A driven session ends each turn one of seven ways, and each asks its own
act of the assistant driving it:

  done      its move proposes its own stop, or hands its assistant its
            report.
  asking    its move asks me something.
  capped    its account hit a usage limit. It goes on once the limit resets.
  error     an API error that is not a usage limit ended its turn. A minute
            later it gets one more try, so a busy server has time to
            clear, three tries in all, as .claude/rules/thinking.md gives
            a failing step. A third error in a row reaches me.
  full      its context filled its window: the request was too long.
            Automatic compaction is off, so it is handed over instead.
  blocked   a permission prompt or a dialog holds it. A Return there picks
            option 1, so only my hand answers it.
  gone      its process ended, and nothing stopped it. Its record stays.

Between finishes it is working, or idle with nothing new. Stopped is a
session /9-session-stop ended: its record went with it.

A cap whose reset has come, and an error whose one more try falls due,
say "due now": the session goes on at once.

Every kind is read live, from what Claude Code already writes, so no mark
is left behind to outlive what it marked.

  Its record      Claude Code's own, sessions/<pid>.json. None, while the
                  registry's record stays, is gone. Waiting is a dialog
                  open: blocked. Busy is working, and so is a turn ended
                  on its own background work, its move no Ruling, Action
                  or Answer, and a turn whose move is a Wait.
  Its transcript  An API error is written there as a record of its own,
                  isApiErrorMessage, with the error StopFailure carries, and
                  before that hook fires. A usage limit is rate_limit, and
                  its quotaLimits say when it resets. A request too long
                  for the window, invalid_request saying "Prompt is too
                  long", is full. Any other error is an error finish.
                  Anything said since means the session went on.
  Its move        transcripts.last_said, as the assistant page reads it.

A wait's timeout is never a finish. Only what the session shows is.

Each account's two windows are kept here too, from the status line, for
a cap whose record names no reset. tools/statusline.py hands them over.
1100 also asks each account for them itself, every ten minutes: ask().
So use none of my sessions made, on claude.ai or by another person on a
shared account, shows too. The file's time says when they were last
handed over, to the minute, so 1100/system shows how old they are.

1100 resumes a driving assistant capped on its own account, and any other
seat that drives or follows a session: watch().

Imported, never run.
"""

import datetime
import json
import os
import re
import subprocess
import tempfile
import time
import zoneinfo

import accounts
import drive
import hear
import models
import panes
import registry
import successor
import transcripts
import wake

# A move proposing its own stop, or handing its assistant its report: its
# work is reported done.
DONE = re.compile(r"^action: stop this session|/9-session-stop|^action: tell session \d+ .*report\.md", re.I)
# A move waiting on work still running: it is working.
WAIT = re.compile(r"^wait\b", re.I)

# The words Claude Code ends a turn on once its context fills its window.
FULL = re.compile(r"^prompt is too long", re.I)

# Seconds past a reset before a capped session goes on. Claude Code's own
# resume waits 30 to 90, so the reset has surely landed by then.
AFTER = 30

# What a capped seat that drives or follows is typed at its reset, unless
# it is an assistant whose drive runs.
LIFTED = "Your cap lifted. Arm your wait again."

# Seconds after an API error before its one more try, so a busy server
# has time to clear.
RETRY = 60
# A failing step's tries, its first among them, as .claude/rules/thinking.md
# gives them: a turn's before its error reaches me, a launch row's too.
TRIES = 3

# Each account's two windows, as last kept.
STATE = os.path.join(registry.ROOT, ".claude", "state", "finish")
# Seconds between touches of a kept file whose windows have not moved.
SEEN = 60


def found(kind: str, at=None, reset: int = 0, move: str = "") -> dict:
    return {"kind": kind, "at": at, "reset": reset, "move": move}


def read(number: str, since: str = "") -> dict:
    """Session NN's finish, as {"kind", "at", "reset", "move"}.

    `at` is when it finished, written as a bookmark is: a turn's last
    words, a cap, a cap's reset once it is past, an error, its one more
    try once that is due, a dialog opening. Gone and stopped carry none,
    so every wait hears them. `reset` is a cap's reset, or when an
    error's one more try falls due, in epoch seconds. 0 when nothing
    names one, or when an error already had its last try.

    Done and asking count only a turn ending after `since`. Every other
    kind holds whatever the bookmark.
    """
    rec = registry.entries().get(number)
    if not rec:
        return found("stopped")
    live = registry.claude_records().get(rec.get("session_id"))
    if live is None:
        return found("gone")
    status = live.get("status")
    if status == "waiting":
        moved = live.get("statusUpdatedAt") or live.get("updatedAt") or 0
        return found("blocked", clock(moved / 1000))
    # Busy only on an agent it sent to the background, its turn is over.
    if (status == "busy" and not wake.over(live, rec)) or wake.waiting(live, rec):
        return found("working")
    path = rec.get("transcript", "")
    tail = registry.tail(path)
    hit = failed(tail)
    if hit.get("error") == "invalid_request" and FULL.search(transcripts.texts(hit.get("message") or {})):
        return found("full", transcripts.stamp(hit))
    if hit.get("error") == "rate_limit":
        reset = reset_of(hit, rec.get("account", ""))
        lifted = clock(reset + AFTER) if reset and reset + AFTER <= time.time() else ""
        return found("capped", max(transcripts.stamp(hit), lifted), reset)
    if hit:
        when = transcripts.moment(hit)
        due_at = int(when.timestamp()) + RETRY if when and in_a_row(tail) < TRIES else 0
        tried = clock(due_at) if due_at and due_at <= time.time() else ""
        return found("error", max(transcripts.stamp(hit), tried), due_at,
                     transcripts.texts(hit.get("message") or {}).strip())
    said, at, move = transcripts.last_said(path)
    if WAIT.search(move):
        return found("working")
    if said and transcripts.stamp(at) > since:
        return found("done" if DONE.search(move) else "asking", transcripts.stamp(at), move=move)
    return found("idle")


def word(f: dict) -> str:
    """A finish as the states and the wait print it. A cap says until when,
    and an error when its one more try falls due, or that it had its last.
    Each adds "due now" once that time has come."""
    now = ", due now" if f["reset"] and not due(f) else ""
    if f["kind"] == "capped" and f["reset"]:
        return f"capped until {drive.hour(f['reset'])}{now}"
    if f["kind"] == "error":
        return f"error, one more try at {drive.hour(f['reset'])}{now}" if f["reset"] else "error, three times in a row"
    return f["kind"]


def new(f: dict, since: str) -> bool:
    """Whether a wait bookmarked at `since` wakes on this finish."""
    return f["kind"] not in ("working", "idle") and (f["at"] is None or f["at"] > since)


def due(f: dict) -> float:
    """When a wait wakes by the clock, in epoch seconds: at a cap's reset,
    or at an error's one more try. 0 when nothing lies ahead, because only
    a write can wake it then."""
    go = (f["reset"] + AFTER if f["kind"] == "capped" and f["reset"]
          else f["reset"] if f["kind"] == "error" else 0)
    return go if go > time.time() else 0


def failed(tail: list) -> dict:
    """The API error a transcript ends on, or {} once anything was said
    after it.

    A meta record says nothing: a rename's reminder, or the line Claude
    Code types to resume a cap, which its answer or its next error follows.
    """
    for d in reversed(tail):
        if d.get("type") not in ("user", "assistant") or d.get("isMeta"):
            continue
        return d if d.get("isApiErrorMessage") else {}
    return {}


def cap(tail: list) -> dict:
    """The usage-limit error a transcript ends on, or {}."""
    hit = failed(tail)
    return hit if hit.get("error") == "rate_limit" else {}


def in_a_row(tail: list) -> int:
    """How many API errors, none a usage limit, a transcript ends on, with
    only words typed to the session between them. A turn that did any
    work between two errors breaks the row."""
    n = 0
    for d in reversed(tail):
        if d.get("type") != "assistant" or d.get("isMeta"):
            continue
        if not d.get("isApiErrorMessage") or d.get("error") == "rate_limit":
            break
        n += 1
    return n


def reset_of(hit: dict, account: str) -> int:
    """When a cap lifts, in epoch seconds: the reset its record names, else
    its window's, as last kept for the account. 0 when
    neither names one."""
    quota = hit.get("quotaLimits") or {}
    if isinstance(quota.get("resetsAt"), (int, float)):
        return int(quota["resetsAt"])
    window = limits(account).get(quota.get("rateLimitType") or "five_hour")
    return int(window.get("resets_at") or 0) if isinstance(window, dict) else 0


def clock(epoch: float) -> str:
    """An instant as a bookmark is written: this Mac's clock, to the second."""
    return time.strftime(transcripts.STAMP, time.localtime(epoch))


# ---- each account's windows ---------------------------------------------------

def keep(account: str, rate_limits, into: str = STATE) -> bool:
    """Keep one account's two windows, as the status line hands them over.

    Written only when they moved, and whole at once, so a reader never
    sees half. Every session of an account hands over the same values, so
    most calls write nothing. Unmoved, the file's time is touched instead,
    at most once a minute, so it says when they were last handed over.
    True when it wrote.
    """
    if account not in accounts.KNOWN or not isinstance(rate_limits, dict) or not rate_limits:
        return False
    path = os.path.join(into, f"limits-{account}.json")
    text = json.dumps(rate_limits, sort_keys=True) + "\n"
    try:
        with open(path) as f:
            if f.read() == text:
                if time.time() - os.path.getmtime(path) >= SEEN:
                    os.utime(path)
                return False
    except OSError:
        pass
    registry.write_whole(path, text)
    return True


def limits(account: str) -> dict:
    """One account's two windows, as last kept: five_hour and seven_day,
    each with used_percentage and resets_at. {} when none were."""
    try:
        with open(os.path.join(STATE, f"limits-{account}.json")) as f:
            got = json.load(f)
    except (OSError, ValueError):
        return {}
    return got if isinstance(got, dict) else {}


# ---- each account's windows, asked for --------------------------------------------

# Claude Code's /usage prints an account's two windows with no session
# open: a local command, never the model, so asking costs no usage. It runs
# from a folder of its own, outside the repo, loading no settings, so no
# hook fires, and it saves no session. It runs the claude a launch runs,
# lib/models.py's.
ASK = ["-p", "/usage", "--setting-sources", "project", "--no-session-persistence"]
ASKED_FROM = os.path.join(tempfile.gettempdir(), "usage-ask")
# Seconds between two asks of every account.
ASK_EVERY = 600
# "Current session: 4% used · resets Oct 9 at 6:10pm (America/Toronto)",
# and the same for "Current week (all models)". A window not yet started
# names no reset.
USED = re.compile(r"^Current (session|week \(all models\)): (\d+(?:\.\d+)?)% used"
                  r"(?: · resets (\w{3}) (\d{1,2}) at (\d{1,2})(?::(\d{2}))?(am|pm) \(([^)]+)\))?", re.M)
NAMED = {"session": "five_hour", "week (all models)": "seven_day"}


def reset_at(month: str, day: str, hour: str, minute: str, half: str, zone: str, now: float) -> int:
    """A reset as /usage prints it, in epoch seconds. It names no year, so
    the year putting it nearest now is its own."""
    try:
        tz = zoneinfo.ZoneInfo(zone)
    except (zoneinfo.ZoneInfoNotFoundError, ValueError):
        tz = None
    m = datetime.datetime.strptime(month, "%b").month
    h = int(hour) % 12 + (12 if half == "pm" else 0)
    year = datetime.datetime.fromtimestamp(now, tz).year
    at = [datetime.datetime(y, m, int(day), h, int(minute or 0), tzinfo=tz).timestamp() for y in (year - 1, year, year + 1)]
    return int(min(at, key=lambda t: abs(t - now)))


def read_usage(text: str, now: float) -> dict:
    """/usage's printout as the status line hands the windows over:
    {"five_hour": {"used_percentage": 4, "resets_at": 1791583800},
    "seven_day": {...}}. {} unless both windows read."""
    out = {}
    for name, pct, *reset in USED.findall(text):
        used = float(pct)
        out[NAMED[name]] = {"used_percentage": int(used) if used.is_integer() else used,
                            "resets_at": reset_at(*reset, now) if reset[0] else 0}
    return out if len(out) == len(NAMED) else {}


def ask(account: str) -> dict:
    """Ask one account for its two windows, and keep them. {} when the
    account is no known one, or /usage could not be read."""
    if account not in accounts.KNOWN:
        return {}
    env = dict(os.environ)
    env.pop("CLAUDE_CONFIG_DIR", None)
    if (folder := accounts.ACCOUNTS[account]["folder"]) != accounts.DEFAULT:
        env["CLAUDE_CONFIG_DIR"] = folder
    os.makedirs(ASKED_FROM, exist_ok=True)
    try:
        r = subprocess.run([models.binary() or "claude", *ASK], cwd=ASKED_FROM, env=env,
                           capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        return {}
    got = read_usage(r.stdout, time.time())
    if got:
        keep(account, got)
    return got


def asking() -> None:
    """1100's asking, on a thread of its own, for as long as 1100 runs:
    every account at once on start, then every ten minutes. An account
    whose windows a session's status line kept within those ten minutes is
    fresh already, and is not asked: each ask starts a whole claude."""
    while True:
        for account in accounts.KNOWN:
            try:
                kept = os.path.getmtime(os.path.join(STATE, f"limits-{account}.json"))
            except OSError:
                kept = 0
            if time.time() - kept < ASK_EVERY:
                continue
            try:
                ask(account)
            except Exception:
                pass
        time.sleep(ASK_EVERY)


# ---- 1100's resume --------------------------------------------------------------

def driving() -> dict:
    """Every assistant whose drive runs, and every other seat that drives
    or follows a session, with the reset of the cap its own last turn ended
    on, or 0: {"90": 1790913000}. A paused drive is left out, so nothing is
    ever typed into it."""
    out, held = {}, registry.entries()
    for nn, rec in held.items():
        state = drive.state(nn)
        if state == "running" or state != "paused" and successor.watching(nn, held):
            hit = cap(registry.tail(rec.get("transcript", "")))
            out[nn] = reset_of(hit, rec.get("account", "")) if hit else 0
    return out


def line(nn: str) -> str:
    """What a capped seat is typed at its reset: an assistant's Resume
    button's line, or any other seat's call back to its one wait."""
    return drive.RESUME if drive.state(nn) == "running" else LIFTED


def resume(typed: set, now: float) -> dict:
    """Type line() into each seat driving() names whose cap's reset is
    past: drive.RESUME, the line an assistant's Resume button types.

    It is still capped at that moment: never blocked, gone or working
    again, by read's order. Each reset is typed once, so a line the
    server refuses at the reset never repeats: Claude Code's own resume
    follows it. A line iTerm never typed counts for nothing, and is tried
    again on the next pass. Returns the picture it acted on.
    """
    seen = driving()
    for nn, reset in seen.items():
        if reset and reset + AFTER <= now and (nn, reset) not in typed \
                and read(nn)["kind"] == "capped":
            if panes.say(panes.pane_of(nn), line(nn)):
                typed.add((nn, reset))
    return seen


def watch(hold: float = 900) -> None:
    """1100's resume, on a thread of its own, for as long as 1100 runs.

    Between resets it sleeps until a drive, a record or a driver's
    transcript is written, or until the next reset falls due. A seat
    claimed or gone wakes it too, so a new seat's folder is heard from
    then on. `hold` is the safety net: the picture is read again after
    that long, heard or not.
    """
    typed: set = set()
    while True:
        try:
            now = time.time()
            seen = resume(typed, now)
            ahead = [r + AFTER for r in seen.values() if r and r + AFTER > now]
            held = registry.entries()
            files = [registry.WORK] + [p for nn, rec in held.items() for p in (
                registry.folder(nn), drive.path(nn), rec.get("transcript", "") if nn in seen else "") if p]
            hear.until(lambda: driving() != seen or registry.entries().keys() != held.keys(), files,
                       seconds=min(ahead, default=now + hold) - now)
        except Exception:
            time.sleep(60)
