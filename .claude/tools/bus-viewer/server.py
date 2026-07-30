#!/usr/bin/env python3
"""Ask/answer status viewer.

A tiny local server that shows, at a glance, which session has a question out and
which has an answer waiting. It reads the session folders directly — there is no
separate bus root, no counter file, and no pairing state.

State is derived from which files exist, every read, never stored:

    90-NNNN-<slug>-ask.md          alone  -> open      (someone owes an answer)
    90-NNNN-<slug>-answer.md              -> answered  (that window owes an /4-inbox)
    90-NNNN-<slug>-answer.read.md         -> done

Open beats answered. The scan itself lives in ../bus.py, which this file imports,
so the page and the skills can never disagree about a session's state.

Numbers are contiguous per session, so how many exist is how deep the thread ran.
A card shows that count once it passes one, and warms at four.

Read-only. It never writes.

    python3 server.py              then open http://127.0.0.1:8787
    BUS_PORT=8788 python3 server.py    to run a second one beside the first
"""
import http.server
import importlib.util
import json
import os
import socketserver
from datetime import datetime

PORT = int(os.environ.get("BUS_PORT", "8787"))
REFRESH = 5  # seconds between auto-refreshes

# Import ../bus.py by path — it is a script, not an installed module.
_HERE = os.path.dirname(os.path.abspath(__file__))
_BUS_PY = os.path.join(os.path.dirname(_HERE), "bus.py")
_spec = importlib.util.spec_from_file_location("bus", _BUS_PY)
bus = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bus)

# The repo this engine is watching. Shown in the header, so two engines running
# side by side are never confused for one another.
REPO = os.path.basename(os.path.dirname(os.path.dirname(_HERE)))

ACTION = {
    "open": "Answer it",
    "answered": "Run /4-inbox there",
    "idle": "Idle",
}


def mtime_of(d, number):
    """When the current state was set — the file that decided it."""
    asks, answers, reads = bus.scan(d)
    for bucket in (answers, asks, reads):
        fn = bucket.get(number)
        if fn:
            try:
                return os.path.getmtime(os.path.join(d, fn))
            except OSError:
                return None
    return None


def collect():
    rows = []
    if not os.path.isdir(bus.SESSIONS):
        return rows
    for name in sorted(os.listdir(bus.SESSIONS)):
        d = os.path.join(bus.SESSIONS, name)
        if not os.path.isdir(d) or name.startswith("."):
            continue
        asks, answers, reads = bus.scan(d)
        if not (asks or answers or reads):
            continue  # never asked anything — not this page's subject
        live = os.path.exists(os.path.join(d, ".session-live"))
        state, number, count = bus.state_of(d)
        if state == "idle" and not live:
            continue  # closed, and everything it asked was answered and pulled
        ts = mtime_of(d, number) if number else None
        # How deep the thread ran.
        rounds = len(set(asks) | set(answers) | set(reads))
        rows.append({
            "session": name,
            "state": state,
            "number": f"{number:04d}" if number else "",
            "subject": bus.subject(d, number) if number else "",
            "count": count,
            "rounds": rounds,
            "live": live,
            "action": ACTION[state],
            "elapsed": (datetime.now().timestamp() - ts) if ts else None,
            "clock": datetime.fromtimestamp(ts).strftime("%H:%M") if ts else "",
        })
    # Open first, then answered, then idle. Within a state, oldest wait first.
    order = {"open": 0, "answered": 1, "idle": 2}
    rows.sort(key=lambda r: (order[r["state"]], -(r["elapsed"] or 0)))
    return rows


class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass  # silent; it usually runs headless behind the app

    def do_GET(self):
        if self.path.startswith("/status"):
            body = json.dumps({"sessions": collect()}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
        else:
            body = PAGE.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


PAGE = """<!doctype html>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ask / Answer — __REPO__</title>
<style>
  :root { color-scheme: light dark; --fg: #e7e9ee; --dim: #7b8090; --card: #171a21; --bg: #0f1115; }
  @media (prefers-color-scheme: light) {
    :root { --fg: #1a1c22; --dim: #6b7280; --card: #ffffff; --bg: #f5f6f8; }
  }
  * { box-sizing: border-box; }
  body { font: 13px/1.45 ui-sans-serif, -apple-system, "SF Pro Text", system-ui, sans-serif;
         background: var(--bg); color: var(--fg); margin: 0; padding: 14px 12px; }
  h1 { font-size: 12px; font-weight: 700; letter-spacing: .12em; text-transform: uppercase;
       color: var(--dim); margin: 0 0 2px; }
  .repo { font-size: 11px; color: var(--dim); opacity: .7; margin: 0 0 12px;
          word-break: break-all; }
  .card { background: var(--card); border-left: 3px solid var(--c); border-radius: 6px;
          padding: 10px 12px; margin-bottom: 8px; box-shadow: 0 1px 2px rgba(0,0,0,.18); }
  .open     { --c: #ef7f37; }
  .answered { --c: #46c46a; }
  .idle     { --c: #7b8090; }
  .name { font-weight: 650; word-break: break-all; }
  .rounds { color: var(--dim); font-size: 11px; font-weight: 600; margin-left: 6px;
            white-space: nowrap; }
  .rounds.hot { color: #ef7f37; }
  .turn { color: var(--c); font-weight: 700; margin-top: 3px; }
  .subject { opacity: .8; margin-top: 2px; word-break: break-word; }
  .meta { color: var(--dim); margin-top: 3px; font-size: 12px; }
  .badge { display: inline-block; background: var(--c); color: var(--bg); border-radius: 3px;
           padding: 0 5px; font-size: 11px; font-weight: 700; margin-left: 5px; }
  .empty { color: var(--dim); padding: 20px 2px; }
</style>
<h1>Ask / Answer</h1>
<div class="repo">__REPO__</div>
<div id="grid"></div>
<script>
const REFRESH = __REFRESH__;
function ago(s){
  if(s==null) return "";
  s = Math.max(0, Math.round(s));
  if(s < 60) return s + "s";
  if(s < 3600) return Math.round(s/60) + "m";
  if(s < 86400) return Math.round(s/3600) + "h";
  return Math.round(s/86400) + "d";
}
function esc(s){ return String(s).replace(/[&<>"']/g, c =>
  ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c])); }
async function tick(){
  try {
    const r = await fetch("/status", {cache:"no-store"});
    const d = await r.json();
    const g = document.getElementById("grid");
    if(!d.sessions.length){ g.innerHTML = '<div class="empty">No sessions.</div>'; return; }
    g.innerHTML = d.sessions.map(s => {
      const subj = s.subject ? `<div class="subject">${esc(s.number)} · ${esc(s.subject)}</div>` : "";
      const many = s.count > 1 ? `<span class="badge">${esc(s.count)} open</span>` : "";
      const meta = s.clock ? `<div class="meta">${ago(s.elapsed)} ago · ${esc(s.clock)}</div>` : "";
      // One question is the norm and needs no marker. Four or more is the cost
      // the ask doctrine warns about, so it goes warm.
      const rounds = s.rounds > 1
        ? `<span class="rounds${s.rounds >= 4 ? " hot" : ""}">${esc(s.rounds)} rounds</span>` : "";
      return `<div class="card ${esc(s.state)}">
        <div class="name">${esc(s.session)}${rounds}</div>
        <div class="turn">${esc(s.action)}${many}</div>
        ${subj}${meta}
      </div>`;
    }).join("");
  } catch(e){ /* server closing */ }
}
tick(); setInterval(tick, REFRESH*1000);
</script>
"""
PAGE = PAGE.replace("__REFRESH__", str(REFRESH)).replace("__REPO__", REPO)


def main():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
        print(f"Ask/answer engine on http://127.0.0.1:{PORT} — reading {bus.SESSIONS}")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
