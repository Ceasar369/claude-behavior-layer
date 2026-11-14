#!/usr/bin/env python3
"""files-page.py — Files, 1100's page at /files.

Every session's folder as a tree, a team's together, and the file I pick,
its text or itself, at /tree/NN/REL, /text/NN/REL and /raw/NN/REL. Nothing
outside a session's own folder is ever listed, read or sent.

drawn() draws it on the contract, lib/live.py's: it loads once, and only
what moved is put in place. Its own script is .claude/pages/scripts/files.js. sessions-dashboard.py answers every name another
file calls here, and routes each address.

Imported, never run.
"""

import base64
import codecs
import json
import os
import re
import sys
import urllib.parse

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import live  # noqa: E402
import page  # noqa: E402
import plans  # noqa: E402
import registry  # noqa: E402

# Home: its teams, the panes open, and each session's state.
workstation = page.tool("workstation")

# ---- the files ----------------------------------------------------------------------

# A file larger than this opens cut, with a line saying so. A wave is 10 KB.
SHOWN = 400_000

# A picture or a clip opens as itself, inside the /text answer the view
# drops in whole. A clip, or a picture past BIG, plays from its own
# address, /raw/NN/REL, sent in pieces off 1100's queue, so no page waits.
BIG = 5_000_000
MEDIA = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
         ".gif": "image/gif", ".webp": "image/webp", ".svg": "image/svg+xml",
         ".webm": "video/webm", ".mp4": "video/mp4", ".mov": "video/quicktime"}


def size(n: int) -> str:
    return f"{n} B" if n < 1024 else f"{n / 1024:.1f} KB" if n < 1048576 else f"{n / 1048576:.1f} MB"


# One icon per kind of file, keyed by extension. A long name is cut before
# its extension shows, so the icon is what says a row is a picture.
ICONS = {
    "image": '<rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="9" cy="9" r="2"/>'
             '<path d="m21 15-3.1-3.1a2 2 0 0 0-2.8 0L6 21"/>',
    "video": '<rect x="2" y="5" width="14" height="14" rx="2"/><path d="m22 8-6 4 6 4z"/>',
    "text": '<path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/>'
            '<path d="M14 3v6h6"/><path d="M8 13h8M8 17h6"/>',
    "data": '<path d="M8 3H7a2 2 0 0 0-2 2v5a2 2 0 0 1-2 2 2 2 0 0 1 2 2v5a2 2 0 0 0 2 2h1"/>'
            '<path d="M16 21h1a2 2 0 0 0 2-2v-5a2 2 0 0 1 2-2 2 2 0 0 1-2-2V5a2 2 0 0 0-2-2h-1"/>',
    "log": '<path d="m4 17 6-6-6-6"/><path d="M12 19h8"/>',
    "code": '<path d="m16 18 6-6-6-6"/><path d="m8 6-6 6 6 6"/>',
    "file": '<path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><path d="M14 3v6h6"/>',
}
KIND = {".md": "text", ".txt": "text", ".json": "data", ".yml": "data", ".yaml": "data",
        ".log": "log", ".py": "code", ".ts": "code", ".tsx": "code", ".js": "code",
        ".sh": "code", ".css": "code", ".html": "code"}


def icon(name: str) -> str:
    """The icon for one file. A picture or a clip is media, and wears blue."""
    ext = os.path.splitext(name)[1].lower()
    kind = MEDIA.get(ext, "").split("/")[0] or KIND.get(ext, "file")
    media = " media" if ext in MEDIA else ""
    return (f'<svg class="kind{media}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">{ICONS[kind]}</svg>')


def count(root: str) -> int:
    """How many files sit anywhere under one folder, hidden ones aside."""
    files = 0
    for _, dirs, names in os.walk(root, followlinks=True):
        dirs[:] = [n for n in dirs if not n.startswith(".")]
        files += sum(1 for n in names if not n.startswith("."))
    return files


def listed(d: str) -> list:
    """One folder's paths in the tree's order: pictures first, then other
    files, then folders, each by name, its numbers counted as numbers.
    Hidden ones aside. The app door reads Files in this order too."""
    try:
        names = [n for n in os.listdir(d) if not n.startswith(".")]
    except OSError:
        return []
    return sorted((os.path.join(d, n) for n in names), key=lambda p: (
        os.path.isdir(p),
        not MEDIA.get(os.path.splitext(p)[1].lower(), "").startswith("image/"),
        [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", os.path.basename(p))]))


def level(number: str, root: str, d: str) -> str:
    """The files and folders right under one folder, as tree rows. Pictures
    first, then other files, then folders, each by name. A folder comes
    closed, counting the files under it, and its rows load once it opens.
    """
    full = listed(d)
    depth = 1 if d == root else os.path.relpath(d, root).count(os.sep) + 2
    pad = f' style="padding-left:{6 + depth * 14}px"'
    rows = []
    for p in full:
        rel = os.path.relpath(p, root)
        try:
            st = os.stat(p)
        except OSError:
            continue
        if os.path.isdir(p):
            rows.append(f'<details data-k="{page.esc(number)}/{page.esc(rel)}"><summary class="frow"{pad}>'
                        f'<span class="nm">{page.esc(os.path.basename(p))}/</span>'
                        f'<span class="fs">{count(p)}</span></summary></details>')
        else:
            rows.append(f'<a class="frow file" data-f="{page.esc(number)}/{page.esc(rel)}"{pad}'
                        f' href="?f={page.esc(urllib.parse.quote(f"{number}/{rel}"))}"'
                        f' title=".claude/state/sessions/{page.esc(number)}/{page.esc(rel)}">'
                        f'{icon(p)}<span class="nm">{page.esc(os.path.basename(p))}</span>'
                        f'<span class="fs">{size(st.st_size)} · <span data-since="{int(st.st_mtime)}"></span></span></a>')
    return "".join(rows)


def tree(nn: str, rel: str) -> str:
    """One folder's rows, asked the first time it opens. Nothing outside a
    session's own folder is ever listed, whatever the address says."""
    root = os.path.realpath(registry.folder(nn))
    want = os.path.realpath(os.path.join(root, rel)) if rel else root
    if not ((want == root or want.startswith(root + os.sep)) and os.path.isdir(want)):
        return ""
    return level(nn, root, want)


FILES_STYLE = "<style>\n" + page.shared("files.css") + "</style>\n"


def sessions_part() -> str:
    """Every session's folder, lowest number first. A team's sit together,
    under its head's, and only a team wears a header: an assistant with a
    plan, and its sessions, as its hub has a team tab. Then the file I
    pick's side, its text left to the page's script. Each folder carries
    an id, so the rows I opened stay with it wherever 1100 moves it, and a
    folder whose record cannot be read still shows, last, saying so."""
    held, live, open_ids = registry.entries(), registry.claude_records(), workstation.panes.ids(workstation.panes.FRESH)
    owned = workstation.plans.owners(held)
    states = {nn: page.shown(nn, r, live.get(r.get("session_id")), open_ids)[:4] for nn, r in held.items()}
    out = []
    for head, members in workstation.teams_of(held, owned):
        folders = []
        for nn in [head] + members:
            files = count(os.path.realpath(registry.folder(nn)))
            name, word, colour, look = states[nn]
            folders.append(f'<details data-k="{nn}" id="d-{nn}">'
                           f'<summary class="frow" title="{page.esc(word)}">'
                           f'<span class="chip{" g" if colour == "grey" else ""}{" dashed" if look else ""}" '
                           f'style="--c:var(--{colour})">'
                           f'{page.esc(workstation.plans.tag(nn, owned))}</span><span class="nm">sessions/{nn}/ · '
                           f'{page.esc(name)}</span>'
                           f'<span class="fs">{files}</span></summary></details>')
        if workstation.plans.plan(head).get("stages"):
            out.append(f'<div class="team"><div class="tl">Team {head} · '
                       f'{page.esc(states[head][0])}</div>{"".join(folders)}</div>')
        else:
            out += folders
    for nn in unread():
        out.append(f'<details data-k="{nn}" id="d-{nn}"><summary class="frow" title="unreadable">'
                   f'<span class="chip g" style="--c:var(--grey)">{nn}</span><span class="nm">sessions/{nn}/ · '
                   f'its record is unreadable</span><span class="fs">{count(os.path.realpath(registry.folder(nn)))}'
                   '</span></summary></details>')
    return (FILES_STYLE + '<div class="files" data-picked="0"><div class="tree">'
            f'<div class="fhd">{page.family("files")}<span class="dim">· {len(held)} session folders</span>'
            '<button class="btn" id="again" title="Draw the page again, as it stands now">Refresh</button></div>'
            f'<div class="scroll"><div class="ftb">{"".join(out)}</div></div></div>'
            f'<div class="view"><div class="fhd"><span class="p" id="fpath"></span>'
            '<span id="copy-status" role="status"></span><button class="btn" id="copy" disabled>Copy</button>'
            f'<button class="close" id="shut" aria-label="Close the file" title="Show no file">{page.icon("close", 15)}</button></div>'
            f'<div class="scroll" id="fview"></div>{page.blank("Pick a file")}</div></div>')


def inside(nn: str, rel: str) -> str:
    """The file REL names inside session NN's own folder, as its real path,
    or "" when it is no file there. Nothing outside a session's own folder
    is ever read or sent, whatever the address says."""
    root = os.path.realpath(registry.folder(nn))
    want = os.path.realpath(os.path.join(root, rel))
    return want if want.startswith(root + os.sep) and os.path.isfile(want) else ""


def raw(path: str):
    """The file /raw/NN/REL names, for serve.run to send in pieces, or None."""
    m = re.fullmatch(r"/raw/(\d{2})/(.+)", path)
    return (inside(m.group(1), urllib.parse.unquote(m.group(2))) or None) if m else None


def mark(path: str) -> str:
    """A picked file's mark: its size and time, so a session rewriting it
    moves it."""
    try:
        st = os.stat(path)
    except OSError:
        return "none"
    return f"{st.st_size}-{st.st_mtime_ns}"


def text(nn: str, rel: str) -> str:
    """One picked file, as the right side shows it: its path, size and mark,
    then its text, or itself when it is a picture or a clip."""
    want = inside(nn, rel)
    if not want:
        return '<p class="cut">This file is gone.</p>'
    root = os.path.realpath(registry.folder(nn))
    kind = MEDIA.get(os.path.splitext(want)[1].lower())
    with open(want, "rb") as f:
        sample = f.read(8192)
    try:
        codecs.getincrementaldecoder("utf-8")().decode(sample, final=False)
        copy_kind = "text" if b"\0" not in sample else "file"
    except UnicodeDecodeError:
        copy_kind = "file"
    if kind and kind.startswith("image/"):
        copy_kind = "image" if kind in ("image/png", "image/jpeg") else "file"
    elif kind and kind.startswith("video/"):
        copy_kind = "file"
    head = (f'<div class="picked" data-path=".claude/state/sessions/{nn}/{page.esc(os.path.relpath(want, root))}" '
            f'data-size="{size(os.path.getsize(want))}" data-mark="{mark(want)}" data-copy="{copy_kind}"></div>')
    if kind:
        if kind.startswith("video/") or os.path.getsize(want) > BIG:
            src = f"/raw/{nn}/{urllib.parse.quote(os.path.relpath(want, root))}"
        else:
            with open(want, "rb") as f:
                src = f"data:{kind};base64,{base64.b64encode(f.read()).decode()}"
        return head + (f'<div class="media"><video src="{src}" controls preload="metadata"></video></div>'
                       if kind.startswith("video/") else f'<div class="media"><img src="{src}" alt=""></div>')
    # The cut counts bytes, as SHOWN does: a letter taking two bytes still
    # says where the file was cut.
    with open(want, "rb") as f:
        raw = f.read(SHOWN + 1)
    return (head + f'<pre class="txt">{page.esc(raw[:SHOWN].decode("utf-8", "replace"))}</pre>'
            + (f'<p class="cut">Cut at {size(SHOWN)}.</p>' if len(raw) > SHOWN else ""))


# ---- the page on the contract --------------------------------------------------
#
# 1100 draws every session's folder, sessions_part(), and a change lands part by
# part: lib/live.py. So the tree is current, with no Refresh. The picked
# file goes as its mark, in the page's data: a session rewriting it, or
# removing it, moves the picture, and the page's own script,
# .claude/pages/scripts/files.js, draws its text again in place, where I scrolled.
# A folder I open still fills from /tree/NN/REL, and Refresh fills each
# open one again.

def unread() -> list:
    """Each session folder whose record is there and cannot be read, which
    registry.entries() leaves out."""
    try:
        names = sorted(n for n in os.listdir(registry.WORK) if re.fullmatch(r"\d{2}", n))
    except OSError:
        return []
    held = registry.entries()
    return [n for n in names if n not in held and os.path.isfile(os.path.join(registry.folder(n), registry.RECORD))]


def named(query: str) -> str:
    """The file a query picks, f=NN/REL, as its real path inside session
    NN's own folder, there or gone, or "" when it names none."""
    m = re.fullmatch(r"(\d{2})/(.+)", (urllib.parse.parse_qs(query).get("f") or [""])[0])
    if not m:
        return ""
    root = os.path.realpath(registry.folder(m.group(1)))
    want = os.path.realpath(os.path.join(root, m.group(2)))
    return want if want.startswith(root + os.sep) else ""


def drawn(query: str = "") -> str:
    """Files on the contract: sessions_part(), its watch first, and the picked
    file's mark as data. A file gone, or no file, marks none."""
    path = named(query)
    data = json.dumps({"mark": mark(path) if path and os.path.isfile(path) else "none"})
    body = (live.watch() + sessions_part() + f'<script type="application/json" id="picked">{data}</script>\n'
            f'<script src="{live.src("files.js")}"></script>\n')
    return page.render("00-files", [("", body)], refresh=0)


def files(query: str = "") -> list:
    """Every file and folder whose write can move Files: each session's
    folder, its record and Claude Code's, registry.watched()'s, each plan,
    each record that cannot be read, and the picked file with its folder. A file deep in a session's folder
    moves only its count, which the 25-second check brings in line."""
    held = list(registry.entries())
    out = registry.watched(held) + [os.path.join(registry.folder(n), plans.PLAN) for n in held]
    out += [os.path.join(registry.folder(n), registry.RECORD) for n in unread()]
    path = named(query)
    return out + ([path, os.path.dirname(path)] if path else [])


def opened() -> tuple:
    """The panes open now, as home's refresher last read them: a pane
    closing greys its chip, and writes no file."""
    return tuple(sorted(workstation.panes.ids(workstation.panes.FRESH)))


# The page's contract, lib/live.py's: its address, its query naming the
# picked file, its draw, its files, and the panes no file carries.
LIVE = live.Page("/files", drawn, files=files, looks=(opened,), query=True)
