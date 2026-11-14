#!/usr/bin/env python3
"""drive.py — my assistant's drive, moment by moment: taking it, pausing it,
resuming it, keeping each session's work, closing a stage, ending it.

  drive.py take 90 plan            the plan, a stage's letter, or mission ids: what I hand it
  drive.py pause 90                "Pause the drive."
  drive.py resume 90               "Resume the drive."
  drive.py keep 90 B1              B1's session's folder, without screenshots, and transcript, into 90's reports/B1/
  drive.py close 90 B <<'EOF'      B's summary as said in chat, into summaries/B.md, then B closed
  drive.py end 90                  the drive ended, once its end holds
  drive.py show 90                 the finish list, the drive, then where it stands
  drive.py finish 90 <<'EOF'       each line I agreed joins the finish list, red
  drive.py green 90 2 <<'EOF'      line 2 green, its proof on stdin
  drive.py out 90 2 <<'EOF'        line 2 ruled out, my words on stdin
  drive.py point 90 A A1           a pause point after stage A, and after mission A1

A pause point fires by itself. Once its stage is closed, or its mission's
work kept, the next verb pauses the drive there, says what finished, and
where to look, and exits lib/drive.py's PAUSED. "Resume the drive." goes
on past it, as after my pause.

The drive itself is lib/drive.py's file. Every verb but keep ends on where
the drive stands, and its next step, read from the plan and the drive. A
plan run in order:

  paused                       nothing launches or stops until I resume it
  a stage stopped, not closed  close it
  a stage runs                 wait on its sessions, and prepare the next
                               stage's launch page
  no stage runs                kick off the next stage: the take of a plan
                               is my press of Launch
  every stage closed           end the plan

An open plan's drive never closes a stage, nor ends the plan, by itself.
Both come on my word alone. Paused, it holds still the same way:

  a mission ruled, no session  launch it while a seat is free
  a mission on its way         wait for its session to claim a number
  sessions run                 wait on them
  nothing runs                 wait for my next ruling

A mission is on its way while a session row of the assistant's launch
page carries its name, not failed, or for a claim's window after its
queue stamp, as tools/launch.py launches one alone.

Just resumed, each finish that came while paused is handled before the
wait. Before any wait, each answer written, unsent, and the assistant's
to send goes out. A drive of a stage or of missions waits on its
sessions, then ends once each has stopped.

A take of a plan run in order marks each stage already done as closed by
me, at when its last session stopped. That is read once, from each
mission's kept transcript.

A session's work is kept before its stop, while its folder stands. keep
refuses a mission whose session already stopped, since its number may
run another session by now.

The end holds once every stage is closed, every session stopped, and each
stage the drive closed has its summary and each of its missions' work
kept. A stage closed before the plan was taken was mine, so the drive
asks neither of it. In an open plan, a mission never launched holds
nothing, nor does a stage holding only such. A drive of the plan also
holds on each red line of the finish list. Anything else holds it, and is
named.

A stage closes once none of its sessions runs. In an open plan, a mission
never launched leaves it free to close, and the stage closes driven or
not.

A mission is stopped or running the assistant page's own way, never a copy.
"""

import argparse
import os
import sys
import time

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import drive  # noqa: E402
import page  # noqa: E402
import plans  # noqa: E402
import registry  # noqa: E402

assistant = page.tool("assistant-page")


def stages(nn: str) -> list:
    """The plan, as (letter, [(mission, stopped)]), each mission with the
    session it became."""
    held, live = registry.entries(), registry.claude_records()
    out = []
    for i, s in enumerate(plans.plan(nn).get("stages", [])):
        ms = [{**m, **plans.found(m, held, nn)} for m in s.get("missions", [])]
        out.append((chr(65 + i), [(m, assistant.state(m, held, live, None)[2] == " done") for m in ms]))
    return out


def tags(ms: list) -> str:
    """Each mission's tag, as the assistant page writes it, joined by commas."""
    return ", ".join(assistant.tag(m) for m in ms)


def coming(nn: str, m: dict) -> bool:
    """Whether queued mission M, with no session yet, is on its way: its
    session claims a number seconds after its launch."""
    if any(r.get("kind") != "browser" and registry.kebab(str(r.get("name", ""))) == registry.kebab(m["name"])
           and not str(r.get("status", "")).startswith("failed") for r in assistant.launcher.read(nn)):
        return True
    try:
        return time.time() - time.mktime(time.strptime(m["queued"], assistant.STAMP)) < registry.CLAIM
    except ValueError:
        return False


def sends(nn: str, live: list) -> str:
    """Each answer written, not yet sent, and the assistant's to send, read
    through the assistant page's own need(), as the words before the wait.
    None gives ""."""
    held = registry.entries()
    got = [f"{m['id']}'s answer to {m['session']}" for m in live if assistant.need(nn, m, held) == "send"]
    return f"send {' and '.join(got)}, through `session-control` Step 2, then " if got else ""


def finish_lines(nn: str) -> list:
    """The finish list, numbered, its state beside each line, with its proof or my words."""
    return [f"{i} · {l['state']} · {l['line']}" + (f" · {l['said']}" if l.get("said") else "")
            for i, l in enumerate(plans.plan(nn).get("finish", []), 1)]


def finish_count(nn: str) -> list:
    """How many of the list's lines are green, those ruled out uncounted. No list says nothing."""
    left = [l for l in plans.plan(nn).get("finish", []) if l["state"] != "out"]
    return [f"Finish list: {sum(l['state'] == 'green' for l in left)} of {len(left)} green."] if left else []


def stands(nn: str, d: dict, resumed: bool = False) -> list:
    """Where the drive stands, then its next step, one line each. Just
    resumed, a finish that came while paused is handled before the wait."""
    said = [f"Drive: {d.get('drive') or 'nothing'}, {d.get('state') or 'not taken'}."] + finish_count(nn)
    if d.get("state") == "paused":
        return said + ['Next: nothing launches or stops until "Resume the drive."']
    if not drive.driving(d):
        return said
    first = "handle each finish that came while paused, by the states, then " if resumed else ""
    wait = lambda live, pre="": (f"Next: {first}{pre}{sends(nn, live)}"
                                 f"wait on {' '.join(m['session'] for m in live)}.")
    plan, keys = stages(nn), drive.words(d)
    if drive.PLAN not in keys:
        held = [(m, gone) for at, ms in plan for m, gone in ms if at in keys or m["id"] in keys]
        live = [m for m, gone in held if m.get("session") and not gone]
        said += [f"{m['id']} has no session yet." for m, _ in held if not m.get("session")]
        if not live:
            return said + ["Every session it drives has stopped.", "Next: end the drive."]
        return said + [f"It drives {tags(live)}.", wait(live)]
    if plans.opened(plans.plan(nn)):
        live = [m for _, ms in plan for m, gone in ms if m.get("session") and not gone]
        queued = [m for _, ms in plan for m, _ in ms if m.get("queued") and not m.get("session")]
        on_way = [m["id"] for m in queued if coming(nn, m)]
        ruled = [m["id"] for m in queued if m["id"] not in on_way]
        said += ([f"Ruled, with no session yet: {' '.join(ruled)}."] if ruled else []) + (
            [f"On its way, no number claimed yet: {' '.join(on_way)}."] if on_way else []) + [
            f"It runs {tags(live)}." if live else "Nothing runs."]
        steps = ([f"launch {' '.join(ruled)} while a seat is free"] if ruled else []) + (
            [f"wait for {' '.join(on_way)} to claim a number"] if on_way else [])
        if live:
            return said + [wait(live, "".join(f"{s}, then " for s in steps))]
        return said + [f"Next: {', then '.join(steps)}." if steps else
                       "Next: wait for my next ruling. A stage closes, and the plan ends, on my word alone."]
    for at, ms in plan:
        if all(gone for _, gone in ms) and at not in d["closed"]:
            return said + [f"Stage {at} has stopped.", f"Next: close stage {at}."]
    now = next(((i, at, ms) for i, (at, ms) in enumerate(plan) if not all(gone for _, gone in ms)), None)
    if now is None:
        return said + ["Every stage is closed.", "Next: end the plan."]
    i, at, ms = now
    live = [m for m, gone in ms if m.get("session") and not gone]
    if not live:
        return said + ["No stage runs.",
                       f"Next: kick off stage {at}. Write its missions, queue them, fire its launch page."]
    after = f" Prepare stage {plan[i + 1][0]}'s launch page, if not done." if i + 1 < len(plan) else ""
    return (said + [f"Stage {at} runs: {tags(live)}."]
            + [f"{m['id']} has no session yet." for m, _ in ms if not m.get("session")]
            + [wait(live) + after])


def kept(nn: str, m: dict) -> bool:
    """Whether mission M's work sits in its report folder: its session's transcript at least."""
    return os.path.isfile(os.path.join(drive.report(nn, m["id"]), f"transcript-{m['session']}.md"))


def holds(nn: str, d: dict) -> list:
    """Everything holding the drive's end. None means it holds."""
    keys = drive.words(d)
    whole = drive.PLAN in keys
    opened = plans.opened(plans.plan(nn))
    out = []
    for at, ms in stages(nn):
        mine = [(m, gone) for m, gone in ms if whole or at in keys or m["id"] in keys]
        out += [f"{assistant.tag(m)} has not stopped." for m, gone in mine if m.get("session") and not gone]
        out += [f"{m['id']} never launched." for m, _ in mine if not m.get("session") and not opened]
        if whole and at not in d["closed"] and (not opened or any(m.get("session") for m, _ in mine)):
            out.append(f"Stage {at} is not closed.")
        # Work and summaries are the drive's to keep only for what it ran.
        # A stage closed before the plan was taken was mine.
        if (at in d["closed"] and d["closed"][at] >= d["taken"]) if whole else mine:
            out += [f"{m['id']}'s work is not in {os.path.relpath(drive.report(nn, m['id']), registry.ROOT)}/."
                    for m, _ in mine if m.get("session") and not kept(nn, m)]
            if whole and not os.path.isfile(drive.summary(nn, at)):
                out.append(f"Stage {at}'s summary is not in "
                           f"{os.path.relpath(drive.summary(nn, at), registry.ROOT)}.")
    if whole:
        out += [f"Finish line {i} is red: {l['line']}"
                for i, l in enumerate(plans.plan(nn).get("finish", []), 1) if l["state"] == "red"]
    return out


def reached(nn: str, d: dict) -> tuple:
    """The drive, paused at the first pause point it reached and has not
    passed, with what to say of it. A stage's is reached once it is closed,
    a mission's once its work is kept. Only a drive of the plan closes a
    stage; a mission's point holds in any drive holding it. Nothing reached
    says nothing."""
    if d.get("state") != "running":
        return d, []
    keys = drive.words(d)
    whole = drive.PLAN in keys
    for i, s in enumerate(plans.plan(nn).get("stages", [])):
        at = chr(65 + i)
        due = [(at, f"stage {at}", os.path.relpath(drive.summary(nn, at), registry.ROOT))
               ] if whole and s.get("pause") and at in d["closed"] else []
        due += [(m["id"], m["id"], os.path.relpath(drive.report(nn, m["id"]), registry.ROOT) + "/")
                for m in s.get("missions", []) if m.get("pause") and m.get("session") and kept(nn, m)
                and (whole or at in keys or m["id"] in keys)]
        for point, name, look in due:
            if point not in d["passed"]:
                done = [m["id"] for _, ms in stages(nn) for m, gone in ms if gone] + [
                    m["id"] for m in s.get("missions", []) if m.get("session") and kept(nn, m)]
                return drive.reach(nn, point), [
                    f"Pause point reached: after {name}. Nothing new launches.",
                    f"Finished: {', '.join(dict.fromkeys(done))}. Look at {look}."]
    return d, []


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("verb", choices=["take", "pause", "resume", "keep", "close", "end", "show", "finish", "green",
                                     "out", "point"])
    ap.add_argument("nn")
    ap.add_argument("keys", nargs="*")
    args = ap.parse_args()
    nn = f"{int(args.nn):02d}"
    plan = stages(nn)
    letters = [at for at, _ in plan]
    ids = {m["id"]: (m, gone) for _, ms in plan for m, gone in ms}
    d = drive.read(nn)

    if args.verb == "take":
        wrong = [k for k in args.keys if k != drive.PLAN and k not in letters and k not in ids]
        if not plan:
            sys.exit(f"Session {nn} holds no plan.")
        if not args.keys or wrong:
            sys.exit(f"take names the plan, a stage's letter or mission ids. Not {' '.join(wrong) or 'nothing'}.")
        # Each stage done before the plan was taken, not yet closed: when its last session stopped.
        # An open plan's stages close on my word alone, never at a take.
        done = {at: max((drive.stopped(nn, m["id"], m["session"]) for m, _ in ms if m.get("session")), default="")
                for at, ms in plan if all(gone for _, gone in ms) and at not in d.get("closed", {})
                } if drive.PLAN in args.keys + drive.words(d) and not plans.opened(plans.plan(nn)) else {}
        d = drive.take(nn, args.keys, done)
    elif args.verb == "pause":
        d = drive.pause(nn)
    elif args.verb == "resume":
        d = drive.resume(nn)
    elif args.verb == "keep":
        if len(args.keys) != 1 or args.keys[0] not in ids:
            sys.exit("keep names one mission id of the plan.")
        m, gone = ids[args.keys[0]]
        if not m.get("session"):
            sys.exit(f"{m['id']} has no session. Nothing to keep.")
        if gone or not os.path.isdir(registry.folder(m["session"])):
            sys.exit(f"{assistant.tag(m)} has stopped. Its folder went with it.")
        got = drive.keep(nn, m["id"], m["session"])
        print(f"Kept {assistant.tag(m)}: {len(got)} files, in "
              f"{os.path.relpath(drive.report(nn, m['id']), registry.ROOT)}/.")
        print("\n".join(os.path.relpath(p, registry.ROOT) for p in got))
        d, said = reached(nn, d)
        if said:
            print("\n".join(said + [f"Next: stop {assistant.tag(m)}, as its finish asks. Then nothing launches "
                                    f"or stops until \"Resume the drive.\""]))
            sys.exit(drive.PAUSED)
        return
    elif args.verb == "point":
        p = plans.plan(nn)
        if not plan:
            sys.exit(f"Session {nn} holds no plan.")
        wrong = [k for k in args.keys if k not in letters and k not in ids]
        if not args.keys or wrong:
            sys.exit(f"point names stage letters or mission ids. Not {' '.join(wrong) or 'nothing'}.")
        for i, s in enumerate(p["stages"]):
            if chr(65 + i) in args.keys:
                s["pause"] = True
            for m in s.get("missions", []):
                if m["id"] in args.keys:
                    m["pause"] = True
        plans.save(nn, p)
        print("Pause points: " + ", ".join(
            [f"after stage {chr(65 + i)}" for i, s in enumerate(p["stages"]) if s.get("pause")]
            + [f"after {m['id']}" for s in p["stages"] for m in s.get("missions", []) if m.get("pause")]) + ".")
        return
    elif args.verb == "close":
        # An open plan's stage closes on my word, driven or not.
        opened = plans.opened(plans.plan(nn))
        if not opened and (drive.PLAN not in drive.words(d) or not drive.driving(d)):
            sys.exit("Only a drive of the plan closes a stage of a plan run in order.")
        if len(args.keys) != 1 or args.keys[0] not in letters:
            sys.exit("close names one stage's letter.")
        at = args.keys[0]
        left = [m for a, ms in plan if a == at for m, gone in ms if not gone and (m.get("session") or not opened)]
        if left:
            sys.exit(f"Stage {at} still runs: {tags(left)}.")
        words = sys.stdin.read().strip()
        if not words:
            sys.exit(f"close takes stage {at}'s summary on stdin, the words said in chat.")
        print(f"Kept {os.path.relpath(drive.close(nn, at, words), registry.ROOT)}.")
        d = drive.read(nn)
    elif args.verb == "end":
        if not drive.driving(d):
            sys.exit(f"Session {nn} drives nothing.")
        held = holds(nn, d)
        if held:
            print("\n".join(held))
            sys.exit(1)
        d = drive.end(nn)
    elif args.verb in ("finish", "green", "out"):
        if not plan:
            sys.exit(f"Session {nn} holds no plan.")
        p = plans.plan(nn)
        got = p.setdefault("finish", [])
        words = sys.stdin.read().strip()
        if args.verb == "finish":
            if not words:
                sys.exit("finish takes the lines I agreed on stdin, one per line.")
            got += [{"line": w.strip(), "state": "red"} for w in words.splitlines() if w.strip()]
        else:
            if len(args.keys) != 1 or not args.keys[0].isdigit() or not 1 <= int(args.keys[0]) <= len(got):
                sys.exit(f"{args.verb} names one line of the finish list, 1 to {len(got)}.")
            if not words:
                sys.exit(f"{args.verb} takes {'its proof' if args.verb == 'green' else 'my words'} on stdin.")
            got[int(args.keys[0]) - 1].update(state=args.verb, said=words)
        plans.save(nn, p)
    listed = finish_lines(nn) if args.verb in ("show", "finish", "green", "out") else []
    d, said = reached(nn, d)
    print("\n".join(listed + said + stands(nn, d, args.verb == "resume")))
    if said:
        sys.exit(drive.PAUSED)


if __name__ == "__main__":
    main()
