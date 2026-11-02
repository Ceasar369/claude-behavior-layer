#!/usr/bin/env python3
"""ports.py — the port scheme, in one place.

Imported by anything that starts, checks or stops a server. The scheme is
ruled by the vault, at
knowledge/0010-playbook/0019-targeted/the-map/running-locally.md. Its
digits, the shift, and the database, are the project's own: lib/project.py
reads them.

While a shift holds, every port is read with it taken off, so 21100 reads
as 1100, and a four-digit port is no longer this project's: it is the other
project's the shift stands clear of.

Standard library only.
"""

import json
import os
import re
import signal
import socket
import subprocess

import hear
import project

# What runs a dev server, and so may sit above the one listening.
LAUNCHERS = {"node", "pnpm", "npm", "npx", "yarn", "tsx", "bun", "deno", "vite"}
# The shift in force, and the one a flip moves to. 20000 keeps every port
# under 30000, clear of ollama's 11434 and of the four-digit ports.
SHIFT = project.SHIFT
SHIFTED = 20000
# The port inside a local address: http://localhost:1400/x holds 1400.
ADDRESS = re.compile(r"://(?:localhost|127\.0\.0\.1):(\d{4,5})(?!\d)")


def plain(port) -> int:
    """A port as the scheme reads it, the shift taken off: 21100 is 1100
    while the shift is 20000. 0 when it then holds no four digits."""
    p = int(port) - SHIFT
    return p if 1000 <= p <= 9999 else 0


def of(address: str) -> int:
    """The port a local address names, or 0 when it names none."""
    m = ADDRESS.search(address or "")
    return int(m.group(1)) if m else 0


def flip() -> int:
    """Move every port by SHIFTED, or back to none. The shift now in force.

    Only processes started after it read it. A running server keeps the
    port it bound. A shift project.json fixes never moves."""
    if project.FIXED:
        return SHIFT
    import registry  # registry imports this module, so it comes in here
    to = 0 if SHIFT else SHIFTED
    path = os.path.join(project.ROOT, project.SHIFT_FILE)
    registry.write_whole(path, json.dumps({"shift": to}) + "\n")
    return to


def started(pids) -> dict:
    """When each running pid started, in UTC, spacing aside. One ps call.

    A pid not running is left out. A pid can be handed to a new process
    once its own ends, so a start time is how a pid is told from its reuse.
    """
    wanted = [str(int(p)) for p in pids if str(p).isdigit() and int(p) > 0]
    if not wanted:
        return {}
    r = subprocess.run(["/bin/ps", "-o", "pid=,lstart=", "-p", ",".join(wanted)],
                       capture_output=True, text=True,
                       env={**os.environ, "TZ": "UTC", "LC_ALL": "C"})
    out = {}
    for line in r.stdout.splitlines():
        pid, _, when = line.strip().partition(" ")
        if pid.isdigit():
            out[int(pid)] = " ".join(when.split())
    return out


def alive(pid: int) -> bool:
    """Whether a pid names a live process.

    pid 0 means "every process in my own group" to kill(2), so it would
    report alive and then signal the caller's own shell. It is never a
    process.

    A zombie is no live process either. It has exited, and only waits for
    its parent to reap it. A pane's shell can take a moment to, and a watch
    taking the zombie for life would miss its one exit event, then wait out
    its whole timeout.

    A process another user owns refuses the signal, yet runs. It is live,
    unless ps reads it as a zombie.
    """
    try:
        pid = int(pid)
    except (TypeError, ValueError):
        return False
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except PermissionError:
        pass
    except OSError:
        return False
    state = subprocess.run(["/bin/ps", "-o", "stat=", "-p", str(pid)],
                           capture_output=True, text=True).stdout.strip()
    return bool(state) and not state.startswith("Z")


def answering(port: int, timeout: float = 0.25) -> bool:
    """Whether anything is listening on a port.

    "localhost", never 127.0.0.1. A Vite frontend binds [::1] alone, so an
    IPv4-only check calls a running server down. create_connection resolves
    the name and tries every family it gets back.
    """
    try:
        socket.create_connection(("localhost", port), timeout).close()
        return True
    except OSError:
        return False


# The project's one database: its port, and the pg_isready that asks it.
# A project naming none has neither.
POSTGRES = project.DATABASE.get("port")
PG_ISREADY = project.DATABASE.get("pg_isready", "")


def database() -> bool:
    """Whether the project's database accepts connections, not merely
    listens. A project naming none has none to accept them.

    A Postgres still starting listens, and refuses every query. pg_isready
    asks the database itself. Named with no pg_isready, a database is up
    while its port answers.
    """
    if not POSTGRES:
        return False
    if not PG_ISREADY:
        return answering(POSTGRES)
    try:
        return subprocess.run([PG_ISREADY, "-q", "-h", "localhost", "-p", str(POSTGRES)],
                              timeout=5).returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def in_scheme(port: int) -> bool:
    """Whether a port could have been derived by this project.

    <layer><role><session>. Layer 1 is the behaviour layer, in every
    project. It holds band 00, and each session's copy of a band-00
    server: session 08 tries 1100 on 1108. Every other layer is a folder
    digit the project names, and takes a role, or a site, it names.

    Role 0 is never assigned, which is what keeps every blocked low port and
    the shared stack outside this set. Postgres on 5432 carries role 4, so
    it is not in the scheme and is never reached.

    A shifted port is read with the shift taken off: plain().
    """
    s = str(plain(port))
    if len(s) != 4:
        return False
    layer, role = int(s[0]), int(s[1])
    if layer == 1:
        return role >= 1
    return layer in project.FOLDERS and role in project.SITES.get(layer, project.ROLES)


def own(port: int, number: str | None) -> bool:
    """Whether a port is session NUMBER's own: in the scheme, its last two
    digits the number. A behaviour-layer port ending in NN is NN's copy of
    one of band 00's, as 1108 is 1100 tried by session 08, so it counts too.

    Band 00 is never a session's. A port outside the scheme, like Postgres
    on 5432, is the shared stack, and nobody's.
    """
    s = str(plain(port))
    if not number or number == "00" or len(s) != 4 or s[2:] != number:
        return False
    return s[1] != "0" if s[0] == "1" else in_scheme(port)


def listeners() -> dict:
    """Every listening TCP port on this machine, mapped to its pid.

    One lsof call, then filtered by the caller. Scanning thousands of ports
    by hand would take minutes and prove less.
    """
    r = subprocess.run(
        ["/usr/sbin/lsof", "-nP", "-iTCP", "-sTCP:LISTEN", "-F", "pn"],
        capture_output=True, text=True)
    found, pid = {}, 0
    for line in r.stdout.splitlines():
        if line.startswith("p"):
            pid = int(line[1:] or 0)
        elif line.startswith("n") and ":" in line:
            tail = line.rsplit(":", 1)[-1]
            if tail.isdigit():
                found.setdefault(int(tail), pid)
    return found


def held(band: str | None = None) -> dict:
    """In-scheme ports listening now, mapped to their pids.

    A band of "07" narrows it to session 07's own ports. Band 00 is never a
    session's, so a session can never reach it this way.
    """
    out = {p: pid for p, pid in listeners().items() if in_scheme(p)}
    if band is not None:
        out = {p: pid for p, pid in out.items() if str(plain(p))[2:] == band}
    return out


def end(pid: int) -> None:
    """Send SIGTERM to one live pid. A pid already gone is left alone."""
    if alive(pid):
        try:
            os.kill(int(pid), signal.SIGTERM)
        except OSError:
            pass


def gone(pids, seconds: float) -> bool:
    """Wait up to `seconds` for every pid to exit, each exit heard. Whether
    they all did. What happens to a pane after is each caller's own choice.
    """
    return hear.until(lambda: not any(alive(p) for p in pids), pids=pids, seconds=seconds)


def stop(ports: dict) -> list:
    """Send SIGTERM to each live pid. Returns the ports stopped, sorted."""
    done = []
    for port in sorted(ports):
        if alive(ports[port]):
            os.kill(ports[port], signal.SIGTERM)
            done.append(str(port))
    return done


def table(environment: bool = False) -> dict:
    """Every process now, by pid: its parent and its command. One ps call,
    for a reader that needs no environment.

    With `environment`, ps prints each one's environment after its command,
    as processes() reads it.
    """
    r = subprocess.run(["/bin/ps", *(["-E"] if environment else []), "-axww",
                        "-o", "pid=,ppid=,command="], capture_output=True, text=True)
    out = {}
    for line in r.stdout.splitlines():
        a = line.split(None, 2)
        if len(a) == 3 and a[0].isdigit() and a[1].isdigit():
            out[int(a[0])] = (int(a[1]), a[2])
    return out


def processes() -> dict:
    """Every process: its parent, its command, and its environment.

    ps prints the environment after the command, so the command alone is
    read too, and cut off. A command that only mentions PORT=4105 is no
    process started for it.
    """
    plain, full = table(), table(environment=True)
    return {pid: (pp, cmd, full.get(pid, (0, cmd))[1][len(cmd):])
            for pid, (pp, cmd) in plain.items()}


def name(command: str) -> str:
    return os.path.basename(command.split(" ", 1)[0])


def carried(table: dict) -> set:
    """Every port some process carries as PORT in its environment."""
    return {int(m.group(1)) for _, _, env in table.values()
            if (m := re.search(r"(?:^|\s)PORT=(\d{4,5})(?:\s|$)", env))}


def serving(port: int, table: dict) -> set:
    """Every pid serving one port: its listener, the launchers above it,
    and every process carrying the port as PORT. A watcher waiting with no
    server still carries it."""
    found = {pid for pid, (_, _, env) in table.items()
             if re.search(rf"(^|\s)PORT={port}(\s|$)", env)}
    up = listeners().get(port, 0)
    while up > 1 and up in table:
        found.add(up)
        up = table[up][0]
        if up not in table or name(table[up][1]) not in LAUNCHERS:
            break
    return found


def spared(table: dict) -> set:
    """Every Claude Code running, and the caller with every process above
    it: the shell or hook that ran it, its session, and that session's pane."""
    keep = {pid for pid, (_, cmd, _) in table.items() if name(cmd) == "claude"}
    up = os.getpid()
    while up > 1:
        keep.add(up)
        up = table[up][0] if up in table else 1
    return keep


def halt(pids) -> list:
    """SIGTERM each pid, then SIGKILL whatever still runs five seconds on.
    The pids still alive after that, which is none when it worked."""
    pids = sorted(pids)
    for pid in pids:
        end(pid)
    if not gone(pids, 5):
        for pid in pids:
            if alive(pid):
                try:
                    os.kill(pid, signal.SIGKILL)
                except OSError:
                    pass
        gone(pids, 2)
    return [p for p in pids if alive(p)]


def sweep(number: str) -> list:
    """Stop everything serving session NUMBER's own ports: what listens on
    one, and what waits to, as a watcher carrying its port does. The ports
    it stopped, sorted."""
    table = processes()
    keep = spared(table)
    found = {}
    for port in set(listeners()) | carried(table):
        if own(port, number):
            pids = serving(port, table) - keep
            if pids:
                found[port] = pids
    halt(set().union(*found.values()))
    return [str(p) for p in sorted(found)]
