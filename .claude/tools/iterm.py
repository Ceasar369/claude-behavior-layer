#!/usr/bin/env python3
"""iterm.py — iTerm's Python API, for what AppleScript cannot do.

AppleScript gives a pane's order and size, never its place, and splits only
right or below. The API gives each tab's real split tree, and splits any
side of any pane.

It needs the iterm2 package, so the venv lib/iterm.py keeps runs it. The
system python never does.

  iterm.py tree                                  every window, tab and split
  iterm.py split  --pane ID --side right         a new pane beside that one
  iterm.py layout --spec JSON                    arrange existing panes
  iterm.py tab    --window ID                    a new tab in that window
  iterm.py window                                a new window
  iterm.py close  --pane ID                      close one pane
  iterm.py name   --pane ID --as NAME [--wait]   name one pane, after its page's title
  iterm.py find   --url URL                      the browser pane showing it
  iterm.py browsers                              every browser pane: id, name given, address
  iterm.py screen --pane ID                      its screen's lines, each as runs of one look

A verb that opens a pane prints its id, then its window's id. Focus goes
back to the pane that held it, so a launch never takes what I am typing.

--url makes the new pane a browser, showing that address. iTerm draws it
as a profile whose command is Browser, so no profile has to exist first.
The pane keeps its address in user.url, which is how find knows it.
A name given keeps in user.name, because the page's own title replaces
the pane's name, sometimes with a blank one.

layout needs iTerm2's Python API 1.14 or newer, in iTerm2 and in the
venv's package. Short of it, layout says so in one line on stderr, prints
nothing, and moves nothing.
"""

import argparse
import asyncio
import json
import sys

import iterm2

# A vertical divider stands panes side by side. Before puts the new one
# left of, or above, the pane it splits.
SIDES = {"right": (True, False), "left": (True, True),
         "down": (False, False), "up": (False, True)}


def node(n) -> dict:
    """One split or one pane. A pane carries its size, in iTerm's pixels."""
    if isinstance(n, iterm2.Splitter):
        return {"split": "columns" if n.vertical else "rows",
                "children": [node(c) for c in n.children]}
    return {"pane": n.session_id, "name": n.name,
            "w": n.frame.size.width, "h": n.frame.size.height}


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="verb", required=True)
    sub.add_parser("tree")
    p = sub.add_parser("split")
    p.add_argument("--pane", required=True)
    p.add_argument("--side", choices=sorted(SIDES), required=True)
    p.add_argument("--url", default="")
    sub.add_parser("layout").add_argument("--spec", required=True)
    p = sub.add_parser("tab")
    p.add_argument("--window", required=True)
    p.add_argument("--url", default="")
    sub.add_parser("window").add_argument("--url", default="")
    sub.add_parser("close").add_argument("--pane", required=True)
    p = sub.add_parser("name")
    p.add_argument("--pane", required=True)
    p.add_argument("--as", dest="name", required=True)
    p.add_argument("--wait", action="store_true")
    sub.add_parser("find").add_argument("--url", required=True)
    sub.add_parser("browsers")
    sub.add_parser("screen").add_argument("--pane", required=True)
    args = ap.parse_args()
    web = iterm2.LocalWriteOnlyProfile({"Custom Command": "Browser", "Initial URL": args.url}) \
        if getattr(args, "url", "") else None

    async def run(connection):
        app = await iterm2.async_get_app(connection)
        if args.verb == "tree":
            print(json.dumps([{"window": w.window_id,
                               "tabs": [{"tab": t.tab_id, "root": node(t.root)} for t in w.tabs]}
                              for w in app.terminal_windows]))
            return
        if args.verb == "close":
            at = app.get_session_by_id(args.pane)
            if at is not None:
                await at.async_close(force=True)
                print(args.pane)
            return
        if args.verb == "name":
            at = app.get_session_by_id(args.pane)
            if at is None:
                return
            # A new browser pane takes its page's title once the page loads,
            # and that title replaces any name given sooner. --wait lets the
            # title land first, eight seconds at most.
            if args.wait:
                first = await at.async_get_variable("autoName")
                for _ in range(40):
                    await asyncio.sleep(0.2)
                    now = await at.async_get_variable("autoName")
                    if now and now != first:
                        break
            await at.async_set_name(args.name)
            await at.async_set_variable("user.name", args.name)
            print(args.pane)
            return
        if args.verb == "find":
            for w in app.terminal_windows:
                for t in w.tabs:
                    for s in t.sessions:
                        if await s.async_get_variable("user.url") == args.url:
                            print(s.session_id)
                            return
            return
        if args.verb == "browsers":
            found = []
            for w in app.terminal_windows:
                for t in w.tabs:
                    for s in t.sessions:
                        url = await s.async_get_variable("user.url")
                        if url:
                            given = await s.async_get_variable("user.name")
                            found.append({"pane": s.session_id, "name": given or s.name,
                                          "url": url})
            print(json.dumps(found))
            return
        if args.verb == "screen":
            # AppleScript reads a screen's text alone. Its looks tell what
            # Claude Code dims: its suggested reply is faint.
            at = app.get_session_by_id(args.pane)
            if at is None:
                return
            got = await at.async_get_screen_contents()
            lines = []
            for i in range(got.number_of_lines):
                line, runs = got.line(i), []
                for k, ch in enumerate(line.string):
                    style = line.style_at(k)
                    fg = style.fg_color
                    rgb = fg.rgb if fg is not None and fg.is_rgb else None
                    look = [f"{rgb.red},{rgb.green},{rgb.blue}" if rgb else "", int(bool(style.faint))]
                    ch = " " if ch in "\x00\xa0" else ch
                    if runs and runs[-1][1:] == look:
                        runs[-1][0] += ch
                    else:
                        runs.append([ch, *look])
                lines.append(runs)
            print(json.dumps(lines))
            return
        held = app.current_terminal_window
        before = held.current_tab.current_session if held else None
        if args.verb == "layout":
            spec = json.loads(args.spec)
            if set(spec) != {"tabs"}:
                raise ValueError("An arrangement may only reshape tabs.")
            has = getattr(connection, "iterm2_protocol_version", None)
            if not hasattr(app, "async_apply_layout"):
                print("Moving panes needs a newer iterm2 package than .claude/state/iterm/venv holds. "
                      "Nothing moved.", file=sys.stderr)
                return
            if not has or tuple(has) < (1, 14):
                print("Moving panes needs iTerm2's Python API 1.14 or newer. This iTerm2 has "
                      f"{'.'.join(map(str, has)) if has else 'an older one'}. Nothing moved.", file=sys.stderr)
                return
            await app.async_apply_layout(spec)
            if before is not None:
                await before.async_activate(order_window_front=False)
            print("1")
            return
        if args.verb == "split":
            at = app.get_session_by_id(args.pane)
            if at is None:
                return
            vertical, first = SIDES[args.side]
            new = await at.async_split_pane(vertical=vertical, before=first,
                                            profile_customizations=web)
            win, _ = app.get_window_and_tab_for_session(at)
        elif args.verb == "tab":
            win = app.get_window_by_id(args.window)
            if win is None:
                return
            new = (await win.async_create_tab(profile_customizations=web)).current_session
        else:
            # A new window comes back before iTerm has told the app about its
            # tab, so the app is read again before the tab is asked for.
            made = await iterm2.Window.async_create(connection, profile_customizations=web)
            await app.async_refresh()
            win = app.get_window_by_id(made.window_id)
            new = win.tabs[0].sessions[0]
        if web is not None:
            await new.async_set_variable("user.url", args.url)
        if before is not None:
            await before.async_activate(order_window_front=args.verb == "window")
        print(new.session_id, win.window_id if win else "")

    iterm2.run_until_complete(run)


if __name__ == "__main__":
    main()
