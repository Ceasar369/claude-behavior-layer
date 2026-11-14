#!/usr/bin/env python3
"""panes.py — opening a pane, typing into one, and finding a session's.

Every skill that starts work in another terminal comes here. The
AppleScript is written once, and nowhere else.

A session's pane is the iTerm pane holding its terminal now. pane()
answers it, and every reader of a pane asks there.

A placement is two values. An anchor and a direction. `right` and `down`
split the anchor, `tab` joins its window, and `window` ignores it.

`down` is the default. A pane opened for a test splits its opener, so
it lands below it, in the same tab. A session I launch is placed on the
launch page, or passed as flags to tools/launch.py, and lib/launch.py
opens its pane.

A pane is named by its id alone. iTerm's session order follows the
layout, and a split renumbers it, so a position cannot be addressed.

Imported, never run. The command line is .claude/tools/panes.py.
"""

import collections
import io
import json
import os
import re
import shlex
import subprocess
import sys
import threading
import time
import traceback

import accounts
import ports
import reader
import registry

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

WHERE = ("right", "down", "tab", "window")

# The efforts `claude --effort` accepts. A model is any name `--model` takes.
EFFORTS = ("low", "medium", "high", "xhigh", "max")

# The account a session runs under is its config folder, and nothing else
# can set it once the process is up, so the folder is named on the line
# itself. Claude Code's own folder names none, so the boot line first
# drops any it inherited.
def named(folder: str) -> str:
    """CLAUDE_CONFIG_DIR as a boot line sets it: under $HOME when FOLDER
    sits there. Empty for Claude Code's own folder."""
    if folder == accounts.DEFAULT:
        return ""
    home = os.path.expanduser("~") + os.sep
    at = "$HOME/" + shlex.quote(folder[len(home):]) if folder.startswith(home) else shlex.quote(folder)
    return f"CLAUDE_CONFIG_DIR={at} "


# Each account's, as a boot line starts with it: lib/accounts.py's.
CONFIG = {a: named(accounts.ACCOUNTS[a]["folder"]) for a in accounts.KNOWN}

# Every process a Claude session starts carries its markers: CLAUDECODE,
# CLAUDE_CODE_CHILD_SESSION, its CLAUDE_CONFIG_DIR, its session id. A
# claude started under them is a child session, and saves no transcript.
# An app a call brings up keeps that call's environment. iTerm crashed
# once mid-launch, and a claim's /rename brought it back up carrying the
# claiming session's markers, so every pane it opened after held them.
# Every call to iTerm goes out without them, and every boot line drops
# them before claude starts.
UNSET = "unset -m 'CLAUDE*'; "

# Set after UNSET, on a Haiku session's claude line alone.
HAIKU_SUBAGENTS = "CLAUDE_CODE_SUBAGENT_MODEL=haiku CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1 "


def clean() -> dict:
    """This process's environment, with no Claude session's markers in it."""
    return {k: v for k, v in os.environ.items() if not k.startswith("CLAUDE")}

# A pane id, and the window holding it. The search finishes before anything
# is created, because a split renumbers the sessions it is walking.
FIND = '''  set target to missing value
  set win to missing value
  repeat with w in windows
    repeat with t in tabs of w
      repeat with s in sessions of t
        if (id of s) is "{pane}" then
          set target to s
          set win to w
        end if
      end repeat
    end repeat
  end repeat
  if target is missing value then return ""
'''

# Each one leaves the new session in `n`. A profile clause taking a command
# returns missing value and opens nothing, so the command is typed instead.
MAKE = {
    "right": '''  tell target
    set n to (split vertically with same profile)
  end tell''',
    "down": '''  tell target
    set n to (split horizontally with same profile)
  end tell''',
    "tab": '''  tell win
    set tb to (create tab with default profile)
  end tell
  set n to current session of tb''',
}

WINDOW = '''tell application "iTerm"
  set wn to (create window with default profile)
  set n to current session of current tab of wn
  return id of n
end tell'''

# Text and return are two writes, a second apart. Sent together they
# arrive as one paste, and a return inside a paste is a newline, not a
# send. The line then sits in the prompt, typed and unsent.
#
# Each write is its own script, and write() retries it. A script searches
# for the pane anew, because a pane reached through windows by position
# breaks when a window changes place, as one going full screen does.
#
# The text itself goes in pieces, because a long enough line outruns the
# prompt and it keeps only what arrived last.
#
# 400 is measured, at a Claude prompt and at a shell. One write of 400
# arrived whole. At a shell one write of 1,200 arrived whole, and 2,400
# did not, in pieces or out of them.
#
# Eighty was the old size, and it bought nothing: every size that lost at
# 400 lost at 80 too. It only made a message take longer to arrive, and a
# message that is still arriving is a message I can type into by mistake.
#
# Bracketed paste is not the answer. Claude Code recognises it, draws
# "[Pasted text #N]", and treats it as pasted content rather than as my
# own words. A message is meant to arrive as my typing.
#
# The pane is found first, and typed into once the walk is over. The walk
# follows the layout, and a split elsewhere renumbers it while it runs.
# Typing inside the walk is the likely cause of a doubled rename, seen
# on two sessions of one launch. The pane is held by its id, so it still
# answers after a split. `contents of` would not do: on a session it is
# the text on screen, not the session.
WRITE = '''tell application "iTerm"
  set s to missing value
  repeat with w in windows
    repeat with t in tabs of w
      repeat with c in sessions of t
        if (id of c) is "{pane}" then set s to (session id "{pane}" of t)
      end repeat
    end repeat
  end repeat
  if s is missing value then return ""
{writes}  return "1"
end tell'''

PIECE = 400
PAUSE = 0.15

# A window going full screen, or coming back, makes iTerm refuse every
# search of its windows for about 0.4 seconds. Measured on iTerm 3.7.6: 8
# of 170 searches failed, in three stretches, across one round trip. A
# failed search types nothing, so it is tried again, a second apart.
TRIES = 3
A_RETRY = 1

# Told of each refused write, with iTerm's words. lib/launch.py sets it to
# its log. One holder of the hook, since panes cannot import launch.
MISSED = [lambda pane, why: None]

# A new pane answers with its id before its shell has drawn a prompt, and
# a line typed into that gap lands scrambled. A 175 character line typed
# the moment the id came back arrived spliced, its pieces out of order.
# The same line arrived whole at half a second, and at every longer wait
# measured.
SETTLE = 0.5

RETURN = "          tell s to write text (character id 13) newline NO\n"
A_RETURN = 1

# Control-K then Control-U, ten times, in one write: a Claude prompt
# emptied before a command types. Each pair kills one line, the cursor
# anywhere on it, and the next pair the break above. Measured on Claude
# Code 2.1.296: two lines, the cursor mid-line, emptied; an empty prompt
# unchanged; /help typed after it arrived whole. Stray letters left in the
# box had joined the front of /handover-prepare, and it never ran.
WIPE = ("          tell s to write text ("
        + " & ".join(["(character id 11)", "(character id 21)"] * 10)
        + ") newline NO\n"
        f"          delay {PAUSE}\n")

# Control-U, which kills the line the cursor sits on. A new pane is not
# always at an empty prompt: a recalled command can be sitting there, and
# the next thing typed joins onto the end of it. That splice produced
# a recalled flag running straight into the boot's "cd", and the boot failed.
# Killing the line costs nothing when the line is already empty.
CLEAR = "          tell s to write text (character id 21) newline NO\n"

# Every pane's id, then the terminal it holds. A browser pane holds none,
# and its tty reads "missing value".
LIST = '''tell application "iTerm"
  set out to ""
  repeat with w in windows
    repeat with t in tabs of w
      repeat with s in sessions of t
        set out to out & (id of s) & " " & (tty of s) & linefeed
      end repeat
    end repeat
  end repeat
  return out
end tell'''


# At most ASKERS programs ask iTerm at once, from one process: osascript
# here, and lib/iterm.py's tool. Uncapped, a slow iTerm left 1100 with
# hundreds of them waiting at once, and they filled the Mac's memory. An
# ask that finds no place within its own timeout is never started.
ASKERS = threading.BoundedSemaphore(3)

# More than BURST asks inside BURST_SECONDS is a flood. One line on stderr,
# 1100's server log, names its askers, at most once a minute.
BURST, BURST_SECONDS = 50, 10
ASKS: collections.deque = collections.deque()
TOLD = [0.0]
TALLY = threading.Lock()


def asker() -> str:
    """Who asks iTerm: the first caller outside this module and lib/iterm.py."""
    for f in reversed(traceback.extract_stack()[:-2]):
        if os.path.basename(f.filename) not in ("panes.py", "iterm.py"):
            return f"{os.path.basename(f.filename)}:{f.lineno} {f.name}"
    return "unknown"


def tally() -> None:
    """Count one ask, and name the askers once they flood. Never raises."""
    try:
        now, who = time.time(), asker()
        with TALLY:
            ASKS.append((now, who))
            while now - ASKS[0][0] > BURST_SECONDS:
                ASKS.popleft()
            if len(ASKS) <= BURST or now - TOLD[0] < 60:
                return
            TOLD[0], count = now, len(ASKS)
            top = collections.Counter(w for _, w in ASKS).most_common(5)
    except Exception:
        return
    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} panes: {count} iTerm asks in {BURST_SECONDS} seconds, from "
          + ", ".join(f"{w} ({n})" for w, n in top), file=sys.stderr, flush=True)


def ask(argv: list, timeout: float) -> subprocess.CompletedProcess:
    """One program asking iTerm, once a place among ASKERS frees. Raises
    subprocess.TimeoutExpired when none frees within `timeout`, as when
    the program itself outlasts it."""
    tally()
    if not ASKERS.acquire(timeout=timeout):
        raise subprocess.TimeoutExpired(argv, timeout)
    try:
        return subprocess.run(argv, env=clean(), capture_output=True, text=True, timeout=timeout)
    finally:
        ASKERS.release()


def run(script: str, timeout: float = 10) -> str | None:
    """One osascript call. None means the question was not answered."""
    try:
        r = ask(["/usr/bin/osascript", "-e", script], timeout)
    except Exception:
        return None
    return r.stdout.strip() if r.returncode == 0 else None


def write(pane: str, writes: str) -> bool:
    """One write into a pane, tried until iTerm finds the pane: TRIES. A
    call that timed out may still land, so it is never tried again."""
    script = WRITE.format(pane=pane, writes=writes)
    for i in range(TRIES):
        if i:
            time.sleep(A_RETRY)
        try:
            r = ask(["/usr/bin/osascript", "-e", script], 20)
        except subprocess.TimeoutExpired:
            MISSED[0](pane, "timed out")
            return False
        except Exception as e:
            MISSED[0](pane, str(e))
            continue
        if r.returncode == 0 and r.stdout.strip() == "1":
            return True
        MISSED[0](pane, r.stderr.strip() or "pane not found")
    return False


def detach(script: str) -> None:
    """The same call, abandoned. For a line that must land after this exits."""
    try:
        subprocess.Popen(["/usr/bin/osascript", "-e", script], env=clean(),
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         start_new_session=True)
    except Exception:
        return


def me() -> str:
    """This session's own pane: the one holding its terminal now.

    A hook or a tool call sits on no terminal, so the process asked is
    CLAUDE_PID's, the session's own. Run outside a session, the process
    asks about itself. The id its shell started with can outlive the pane
    it names, so it answers only when iTerm cannot be asked.

    A split renumbers the panes iTerm is walking, so a list read during
    one can miss this pane. A terminal no pane holds is asked again, three
    times, a second apart.
    """
    tty = tty_of(os.environ.get("CLAUDE_PID") or os.getpid())
    for _ in range(3):
        found = on(tty)
        if found is None:
            return os.environ.get("ITERM_SESSION_ID", "").split(":", 1)[-1]
        if found or not tty:
            return found
        time.sleep(1)
    caller = int(os.environ.get("CLAUDE_PID") or 0)
    mine = next((r for r in registry.entries().values() if caller and registry.pid_of(r) == caller), None)
    return parked(mine) if mine else ""


def parked(record: dict, within: float = 0) -> str:
    """The pane an older process of a session still holds, "" when none.

    A session sent to the background runs on as a copy in no pane, and the
    process it left behind holds the pane I see. The record on disk keeps
    the id the session claimed with, so every id its chain has run under
    is asked, oldest first, and the first one holding a pane answers.
    """
    try:
        # open() is this module's own, below, so the file comes through io.
        with io.open(os.path.join(registry.folder(record["number"]), registry.RECORD)) as f:
            first = json.load(f)
    except (KeyError, OSError, ValueError):
        return ""
    running = registry.claude_records()
    for sid, _ in registry.chain(first):
        found = on(tty_of(running[sid]["pid"]), within) if sid in running else ""
        if found:
            return found
    return ""


def pane(record: dict, pid: int | None = None, within: float = 0) -> str:
    """A registered session's pane: the iTerm pane holding its terminal now.

    While it runs, its process's terminal names the pane. A restart, a
    resume in another pane and a restored shell each leave the record's
    pane behind, so the record only stands in: for a process gone, and
    for an iTerm that cannot be asked. A session outside iTerm has none.

    A process running in no pane is a background copy, and the pane its
    older process still holds is the session's: parked().

    A pane found that differs goes into the record. Once the process ends,
    the record holds the last pane it lived in, and that tells closed from
    gone.

    `pid` is its process, 0 once gone, for a caller already holding it.
    registry.pid_of answers it otherwise. `within` is terminals()'s.
    """
    saved = record.get("pane", "")
    pid = registry.pid_of(record) if pid is None else pid
    found = on(tty_of(pid), within) if pid else None
    if found is None:
        return saved
    if pid and not found:
        return parked(record, within)
    if found and found != saved and record.get("number"):
        registry.repane(record["number"], found)
    return found


def pane_of(number: str) -> str:
    """A registered session's pane, by its two-digit number. pane() answers it."""
    s = str(number)
    if not s.isdigit():
        return ""
    record = registry.entries().get(f"{int(s):02d}")
    return pane(record) if record else ""


def numbers(within: float = 0) -> dict:
    """Every running session's number, by the pane it sits in now. iTerm is
    asked once, or not at all for a page passing `within`: terminals()'s."""
    held, running = registry.entries(), registry.claude_records()
    terminals(within)
    found = {}
    for number, record in held.items():
        pid = registry.pid_of(record, running)
        at = pane(record, pid, within or FRESH) if pid else ""
        if at:
            found[at] = number
    return found


def anchor(frm=None) -> str:
    """The pane a placement hangs off. A number, an id, or mine."""
    if frm in (None, ""):
        return me()
    s = str(frm)
    return pane_of(s) if re.fullmatch(r"\d{1,2}", s) else s


# Every session's terminal, as last listed, and when. A page asks for each
# session's in turn: all of them within one second read one ps call, for
# every running session's pid at once.
TTYS: list = [0.0, {}]
A_SECOND = 1.0


def tty_of(pid) -> str:
    """The terminal a process sits on, as iTerm names it: /dev/ttys003.
    Empty when it sits on none, as a hook or a tool call does, or once it
    is gone."""
    try:
        pid = int(pid)
    except (TypeError, ValueError):
        return ""
    if pid <= 0:
        return ""
    # Inside 1100, the process list read in the background names it, and no
    # program starts. A process too new for that list is asked of ps.
    if ports.PROCESSES.running() and pid in (seen := ports.PROCESSES.last()):
        t = seen[pid][2]
        return f"/dev/{t}" if t and t != "??" else ""
    if pid not in TTYS[1] or time.time() - TTYS[0] >= A_SECOND:
        wanted = {pid} | {int(d["pid"]) for d in registry.claude_records().values()}
        found = {p: "" for p in wanted}
        for line in subprocess.run(["/bin/ps", "-o", "pid=,tty=", "-p", ",".join(str(p) for p in sorted(wanted))],
                                   capture_output=True, text=True).stdout.splitlines():
            p, _, t = line.strip().partition(" ")
            t = t.strip()
            if p.isdigit():
                found[int(p)] = f"/dev/{t}" if t and t != "??" else ""
        TTYS[:] = [time.time(), found]
    return TTYS[1].get(pid, "")


# A page takes an answer from iTerm this many seconds old. iTerm takes a
# fifth of a second to answer, and a page draws on every beat it hears.
# 1100 rechecks every 3 seconds, so a fresher answer would go unread.
FRESH = 3

# terminals()'s last answer, and when it was given; when a page last asked
# for one; and whether a refresher runs. 1100 runs one, freshen(): while
# pages keep asking, it asks iTerm every FRESH seconds on a thread of its
# own, and a page takes the last answer at once, never waiting on iTerm. A
# tool run alone has none, and asks iTerm itself.
LAST = [0.0, None]
ASKED = [0.0]
REFRESHING = [False]
# How long after a page's last ask the refresher keeps asking iTerm.
WANTED = 60


def terminals(within: float = 0) -> dict | None:
    """Every open pane's id, mapped to the terminal it holds, or None when
    iTerm is not running. A browser pane holds none, and maps to "".

    ids() and on() both read it, so one iTerm call answers both.

    `within` takes an answer up to that many seconds old. Only a page
    drawing itself passes it: whatever acts on a pane asks afresh. With
    the refresher running, a page takes its last answer whatever its age,
    so a stalled iTerm never holds a draw up. Without one, a page waits
    that long at most.
    """
    if within:
        ASKED[0] = time.time()
        if (REFRESHING[0] and LAST[0]) or time.time() - LAST[0] < within:
            return LAST[1]
    # pgrep skips the processes that started it unless -a is passed, and
    # iTerm2 started every process in a pane: a session, its hooks, its tools.
    if subprocess.run(["/usr/bin/pgrep", "-a", "-x", "iTerm2"],
                      capture_output=True).returncode != 0:
        found = None
    else:
        out = run(LIST, within or 10)
        found = None if out is None else {
            p: t if t.startswith("/dev/") else ""
            for p, _, t in (line.partition(" ") for line in out.splitlines()) if p}
    # A pane opened or closed since the last answer is told at once: lib/reader.py's moved().
    news = bool(LAST[0]) and found != LAST[1]
    LAST[:] = [time.time(), found]
    if news:
        reader.moved()
    return found


def freshen(every: float = FRESH) -> None:
    """The refresher, on a thread of its own for as long as 1100 runs. It
    asks iTerm once at the start, then every `every` seconds while a page
    asked within the last minute."""
    REFRESHING[0] = True
    while True:
        if not LAST[0] or time.time() - ASKED[0] < WANTED:
            try:
                terminals()
            except Exception:
                pass
        time.sleep(every)


def ids(within: float = 0) -> set | None:
    """Every pane id open now, or None when iTerm is not running.

    None means the question cannot be answered. A caller comparing a
    recorded pane against this never calls one missing on a guess.
    """
    found = terminals(within)
    return None if found is None else set(found)


def on(tty: str, within: float = 0) -> str | None:
    """The pane holding a terminal, or "" when none does. None when iTerm
    is not running."""
    found = terminals(within)
    if found is None:
        return None
    return next((p for p, t in found.items() if tty and t == tty), "")


def say(pane: str, line: str, delay: float = 0, enter: bool = True,
        clear: bool = False) -> bool:
    """Type one line into a pane, and press return.

    `enter` off leaves the line sitting in the prompt, typed and unsent.
    Filling a prompt and sending it are two different asks.

    `clear` empties the prompt first. Only Hand over and clarify's Send
    clear. Every other button never does, since I may have added to what
    it typed.

    A session that is working queues the line. A message reaches it once
    the tool calls it is running end, within the same turn. A command
    waits for the turn to end.

    False means part of the line, or all of it, never landed.

    A delay is for a hook typing into its own pane, because the prompt it
    is answering is still being submitted. A delayed call is abandoned, so
    it reports nothing back, and nothing tries it again.
    """
    if not pane:
        return False
    pieces = [line[i:i + PIECE] for i in range(0, len(line), PIECE)] or [""]
    steps = ([WIPE] if clear else []) + [
        f'          tell s to write text "{p}" newline NO\n'
        f"          delay {PAUSE}\n"
        for p in (q.replace("\\", "\\\\").replace('"', '\\"') for q in pieces)]
    if delay:
        tail = f"          delay {A_RETURN}\n{RETURN}" if enter else ""
        detach(f"delay {delay}\n" + WRITE.format(pane=pane, writes="".join(steps) + tail))
        return True
    if not all(write(pane, step) for step in steps):
        return False
    if not enter:
        return True
    time.sleep(A_RETURN)
    return write(pane, RETURN)


# The keys a page presses, each as the bytes my keyboard sends for it.
KEYS = {"escape": "(character id 27)", "shift-tab": '((character id 27) & "[Z")',
        "down": '((character id 27) & "[B")', "tab": "(character id 9)"}


def press(pane: str, *keys: str) -> bool:
    """Press keys in a pane, in order, as I would. Escape stops a working
    session's turn; Shift+Tab moves it to its next mode."""
    if not pane or not keys:
        return False
    writes = "".join(f"          tell s to write text {KEYS[k]} newline NO\n          delay {PAUSE}\n"
                     for k in keys)
    return run(WRITE.format(pane=pane, writes=writes)) == "1"


def open(where: str = "down", frm=None, cwd: str = "") -> str:
    """Make a pane and return its id. An empty string means it was not made.

    The id comes back before anything runs inside it, so a caller can drive
    the pane from its first line. It comes back after SETTLE, because the
    shell needs that long before it reads what is typed, and after CLEAR,
    because the prompt it draws is not always empty.
    """
    if where not in WHERE:
        return ""
    if where == "window":
        new = run(WINDOW) or ""
    else:
        at = anchor(frm)
        if not at:
            return ""
        new = run('tell application "iTerm"\n' + FIND.format(pane=at)
                  + MAKE[where] + '\n  return id of n\nend tell') or ""
    if not new:
        return ""
    settle(new)
    if cwd:
        say(new, f"cd {cwd}")
    return new


def settle(pane: str) -> None:
    """Wait for a new pane's shell, then empty its prompt. Every new pane needs both."""
    time.sleep(SETTLE)
    write(pane, CLEAR)


def programs(pane: str) -> list | None:
    """What runs in a pane apart from its login and its shell, one command
    each. None when iTerm did not answer. A pane closed, or a browser pane,
    runs nothing: its terminal is empty."""
    found = terminals()
    if found is None:
        return None
    tty = found.get(pane, "")
    if not tty:
        return []
    out = subprocess.run(["/bin/ps", "-t", tty.removeprefix("/dev/"), "-o", "command="],
                         capture_output=True, text=True).stdout
    return [c for c in out.splitlines() if not c.startswith("/usr/bin/login")
            and c.split()[:1] != ["-zsh"]]


def boot_line(words: str = "", acct: str = "1", model: str = "", effort: str = "",
              number: str = "", fork: str = "") -> str:
    """The line that starts a numbered session. Empty when a value is refused.

    The child claims its own number through /0-session-start, which blocks
    its prompt, so the launch costs no model turn. A number passed in is
    the one it asks for. Left out, it takes the lowest free side number.

    The pane's shell may carry a Claude session's markers, so the line
    drops them first: UNSET. The pane's shell is zsh.

    The account is one of this Mac's list, and its folder rides the line:
    CONFIG. A model and an effort ride the claude line itself, so nothing
    is typed into the child afterwards. Left out, Claude Code's own
    defaults hold. An account pinned to a family takes its model instead:
    accounts.pinned().

    A Haiku session forces its subagents onto Haiku too, whatever model an
    Agent call or an agent file names: HAIKU_SUBAGENTS.

    Every session starts at ROOT. A session started in a subfolder loads
    no hook, because settings.json reaches each one through
    $CLAUDE_PROJECT_DIR, and that follows the folder it started in. Such
    a session never claims a number, and answers its own prompt instead.

    A fork is a session id. The session then starts from that one's
    conversation, forked, so the original carries on untouched. Its
    transcript must already sit in this account's folder:
    lib/launch.py's carry().
    """
    if effort and effort not in EFFORTS:
        return ""
    model = accounts.pinned(acct) or model
    if model and not re.fullmatch(r"[A-Za-z0-9.-]+", model):
        return ""
    if fork and not re.fullmatch(r"[A-Za-z0-9-]+", fork):
        return ""
    if str(acct) not in CONFIG:
        return ""
    clean = re.sub(r"[^A-Za-z0-9 -]", "", words).strip()
    asked = f"{int(number):02d} " if str(number).isdigit() else ""
    prompt = f"/0-session-start {asked}{clean}".strip()
    tuned = (f" --model {model}" if model else "") + \
        (f" --effort {effort}" if effort else "") + \
        (f" --resume {fork} --fork-session" if fork else "")
    forced = HAIKU_SUBAGENTS if "haiku" in model else ""
    return f'{UNSET}cd {ROOT} && {CONFIG[str(acct)]}{forced}claude "{prompt}"{tuned}'


def boot(where: str = "down", frm=None, words: str = "", acct: str = "1",
         model: str = "", effort: str = "", number: str = "") -> str:
    """Make a pane and start a numbered session in it."""
    line = boot_line(words, acct, model, effort, number)
    if not line:
        return ""
    new = open(where, frm)
    if new:
        say(new, line)
    return new


def close(pane: str) -> bool:
    """Close a pane by exiting its shell.

    AppleScript's own close leaves a window holding several panes standing.
    """
    return say(pane, "exit")
