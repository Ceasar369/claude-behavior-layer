#!/usr/bin/env python3
"""Check follows, drives and their one wait on seats in a folder of their own, never a real seat."""

import importlib.util
import io
import json
import os
import sys
import tempfile
import time
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "lib"))
import drive  # noqa: E402
import finish  # noqa: E402
import follow  # noqa: E402
import handover  # noqa: E402
import hear  # noqa: E402
import registry  # noqa: E402
import successor  # noqa: E402
import transcripts  # noqa: E402


def tool(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


wait_tool = tool("transcript_tool_test", os.path.join(HERE, "transcript.py"))
follow_tool = tool("follow_tool_test", os.path.join(HERE, "follow.py"))
clarify = tool("clarify_page_test", os.path.join(HERE, "clarify-page.py"))
unwatched = tool("unwatched_test", os.path.join(os.path.dirname(HERE), "hooks", "unwatched.py"))

SID = {"01": "aaaaaaaa-0000-0000-0000-000000000001", "10": "aaaaaaaa-0000-0000-0000-000000000010",
       "11": "aaaaaaaa-0000-0000-0000-000000000011", "12": "aaaaaaaa-0000-0000-0000-000000000012"}
NEW = "bbbbbbbb-0000-0000-0000-000000000010"
TURNS = [("User", "17:00", ["go"], "2026-10-29T17:00:00"),
         ("Session 10", "17:01", ["asked"], "2026-10-29T17:01:00"),
         ("User", "17:02", ["yes"], "2026-10-29T17:02:00"),
         ("Session 10", "17:03", ["done it"], "2026-10-29T17:03:00")]


class Seats(unittest.TestCase):
    def setUp(self):
        self.work = tempfile.TemporaryDirectory()
        self.addCleanup(self.work.cleanup)
        self.held = {n: {"number": n, "title": f"{n}-test", "session_id": SID[n],
                         "transcript": os.path.join(self.work.name, f"{SID[n]}.jsonl"), "claimed": "2026-10-29T16:00:00"}
                     for n in SID}
        for n, rec in self.held.items():
            os.makedirs(os.path.join(self.work.name, n), exist_ok=True)
            with open(rec["transcript"], "w") as f:
                f.write("{}\n")
        for p in (patch.object(registry, "WORK", self.work.name),
                  patch.object(registry, "entries", side_effect=lambda: self.held),
                  patch.object(registry, "claude_records", return_value={}),
                  patch.object(transcripts, "turns", return_value=TURNS),
                  patch.object(drive, "state", return_value="")):
            p.start()
            self.addCleanup(p.stop)
        for n, rec in self.held.items():
            with open(os.path.join(registry.folder(n), registry.RECORD), "w") as f:
                json.dump(rec, f)

    def claim(self, nn, sid, title=""):
        """Another session claims NN: its record, written as a claim writes it."""
        self.held[nn] = {**self.held[nn], "session_id": sid, "title": title or self.held[nn]["title"]}
        with open(os.path.join(registry.folder(nn), registry.RECORD), "w") as f:
            json.dump(self.held[nn], f)

    def handed(self, nn, old_sid, new_sid):
        """Seat NN handed over: its successor holds it, its copy names the old session."""
        os.makedirs(os.path.join(registry.folder(nn), handover.HANDOVERS), exist_ok=True)
        with open(os.path.join(registry.folder(nn), handover.HANDOVERS, "1.md"), "w") as f:
            f.write(f"# {nn}-test\n\nTranscript: /x/{old_sid}.jsonl\nTurns: 4.\n")
        self.claim(nn, new_sid)


class RecordsTest(Seats):
    def test_a_follow_reads_only_what_comes_after_its_newest_turn(self):
        got = follow.take("01", "10", "approve checks", "10 reports")
        self.assertEqual(got["bookmark"], "2026-10-29T17:03:00")
        self.assertEqual(got["session"], SID["10"])
        self.assertEqual(set(follow.following("01")), {"10"})

    def test_a_follow_taken_again_keeps_its_place_and_takes_the_new_words(self):
        follow.take("01", "10", "a", "b")
        follow.update("01", follow.path("01"), lambda d: d["10"].update({"bookmark": "2026-10-29T17:05:00"}))
        got = follow.take("01", "10", "c", "d")
        self.assertEqual((got["for"], got["bookmark"]), ("c", "2026-10-29T17:05:00"))

    def test_a_handover_successor_is_the_same_session(self):
        follow.take("01", "10", "a", "b")
        self.handed("10", SID["10"], NEW)
        self.assertEqual(set(follow.following("01")), {"10"})

    def test_a_reused_number_is_another_session_even_with_the_same_title(self):
        follow.take("01", "10", "a", "b")
        self.claim("10", NEW)
        self.assertEqual(follow.following("01"), {})

    def test_a_stopped_session_drops_out(self):
        follow.take("01", "10", "a", "b")
        del self.held["10"]
        self.assertEqual(follow.following("01"), {})

    def test_what_the_same_session_read_moves_its_bookmark_on_its_next_arming(self):
        follow.take("01", "10", "a", "b")
        follow.read("01", follow.path("01"), {"10": "2026-10-29T17:09:00"}, SID["01"])
        self.assertEqual(follow.records(follow.path("01"))["10"]["bookmark"], "2026-10-29T17:03:00")
        follow.armed("01", follow.path("01"), SID["01"])
        got = follow.records(follow.path("01"))["10"]
        self.assertEqual(got["bookmark"], "2026-10-29T17:09:00")
        self.assertNotIn("read", got)

    def test_a_successor_reads_again_what_its_predecessor_read(self):
        follow.take("01", "10", "a", "b")
        follow.read("01", follow.path("01"), {"10": "2026-10-29T17:09:00"}, SID["01"])
        follow.armed("01", follow.path("01"), NEW)
        got = follow.records(follow.path("01"))["10"]
        self.assertEqual(got["bookmark"], "2026-10-29T17:03:00")
        self.assertNotIn("read", got)


class DriveTest(Seats):
    def test_a_drive_reads_from_the_newest_turn_and_replaces_the_follow(self):
        follow.take("01", "11", "a", "b")
        self.assertEqual(successor.take("01", ["11"], "fix the typos"), [])
        self.assertEqual(follow.following("01"), {})
        got = successor.taken("01")["11"]
        self.assertEqual((got["topic"], got["bookmark"], got["session"]),
                         ("fix the typos", "2026-10-29T17:02:00", SID["11"]))

    def test_a_reused_number_is_never_shown_driven(self):
        successor.take("01", ["11"], "t")
        self.assertEqual(successor.drivers(), {"11": "01"})
        self.claim("11", NEW)
        self.assertEqual(successor.drivers(), {})

    def test_a_take_from_before_identities_were_kept_still_drives(self):
        with open(successor.path("01"), "w") as f:
            json.dump({"11": {"topic": "", "taken": "2026-10-29T16:52:13"}}, f)
        self.assertEqual(successor.drivers(), {"11": "01"})

    def test_a_follow_of_a_driven_session_is_refused(self):
        successor.take("01", ["11"], "t")
        self.assertIn("you drive it", follow_tool.refused("01", "11"))
        self.assertIn("this seat", follow_tool.refused("01", "01"))
        self.assertIn("no session", follow_tool.refused("01", "44"))
        self.assertEqual(follow_tool.refused("01", "12"), "")

    def test_a_seat_that_only_follows_hands_itself_over(self):
        self.assertFalse(successor.driving("01"))
        follow.take("01", "10", "a", "b")
        self.assertTrue(successor.driving("01"))
        wrap = tool("wrap_up_test", os.path.join(os.path.dirname(HERE), "hooks", "wrap-up.py"))
        out = io.StringIO()
        with patch.object(wrap.context, "last", return_value=(1, 1)), \
                patch.object(wrap.context, "share", return_value=90), patch.object(wrap.context, "wrapup", return_value=80), \
                patch("sys.stdin", io.StringIO(json.dumps({"session_id": SID["01"], "transcript_path": "x"}))), \
                redirect_stdout(out):
            wrap.main()
        self.assertIn("hand yourself over", json.loads(out.getvalue())["hookSpecificOutput"]["additionalContext"])

    def test_the_successor_arms_the_one_wait(self):
        follow.take("01", "10", "a", "b")
        self.assertIn(successor.WAIT, handover.message("01"))

    def test_a_partial_drive_band_names_its_topic(self):
        self.assertEqual(clarify.band("01", "fix the typos"),
                         "01 drives this session on fix the typos. Items off it are yours.")
        self.assertEqual(clarify.band("01", ""), "01 drives this session, and answers this wave.")
        self.assertEqual(clarify.band("", "x"), "")


class CapTest(Seats):
    def test_a_seat_that_follows_is_resumed_with_its_own_line(self):
        follow.take("01", "10", "a", "b")
        with patch.object(registry, "tail", return_value=[]):
            self.assertEqual(finish.driving(), {"01": 0})
        self.assertEqual(finish.line("01"), finish.LIFTED)
        with patch.object(drive, "state", return_value="running"):
            self.assertEqual(finish.line("01"), drive.RESUME)

    def test_a_paused_drive_is_never_typed_into(self):
        follow.take("01", "10", "a", "b")
        with patch.object(drive, "state", return_value="paused"), patch.object(registry, "tail", return_value=[]):
            self.assertEqual(finish.driving(), {})


class WaitTest(Seats):
    def run_wait(self, kinds, limit=0):
        """The one wait, its finishes read off `kinds`, every hear answered at once."""
        def read(n, mark=""):
            k = kinds.get(n, "working")
            return finish.found(k, "2026-10-29T17:10:00" if k in ("asking", "done") else None)
        out = io.StringIO()
        with patch.object(finish, "read", side_effect=read), \
                patch.object(hear, "until", side_effect=lambda check, *a, **k: check()), \
                patch.dict(os.environ, {"CLAUDE_CODE_SESSION_ID": SID["01"]}), redirect_stdout(out):
            wait_tool.seat_main("01", SID["01"], limit)
        return out.getvalue()

    def test_a_finish_wakes_it_and_is_kept_as_read(self):
        follow.take("01", "10", "approve checks", "10 reports")
        successor.take("01", ["11"], "fix the typos")
        said = self.run_wait({"10": "asking"})
        self.assertTrue(said.startswith("Woke on 10."))
        self.assertIn("you follow it for: approve checks. It ends when: 10 reports", said)
        self.assertIn("you drive it on: fix the typos", said)
        self.assertTrue(said.rstrip().endswith("Wait again."))
        got = follow.records(follow.path("01"))["10"]
        self.assertEqual(got["read"], {"to": "2026-10-29T17:10:00", "by": SID["01"]})

    def test_a_stopped_session_and_a_reused_number_are_released(self):
        follow.take("01", "10", "a", "b")
        successor.take("01", ["11"], "t")
        del self.held["10"]
        self.claim("11", NEW, "11-other")
        said = self.run_wait({})
        self.assertIn("State: stopped. The wait released it.", said)
        self.assertIn("another session holds 11 now, 11-other. The wait released it.", said)
        self.assertTrue(said.rstrip().endswith("Following and driving nothing."))
        self.assertEqual((follow.records(follow.path("01")), successor.taken("01")), ({}, {}))

    def test_a_number_claimed_while_it_read_stopped_is_told_as_another_session(self):
        follow.take("01", "10", "a", "b")
        on = wait_tool.seat("01")
        self.claim("10", NEW, "10-other")
        out = io.StringIO()
        with patch.object(wait_tool, "seat_wait", return_value=(
                on, {"10": ""}, {"10": finish.found("stopped")}, ["10"], False, [])), redirect_stdout(out):
            wait_tool.seat_run("01", SID["01"], 0)
        self.assertIn("another session holds 10 now, 10-other. The wait released it.", out.getvalue())
        self.assertEqual(follow.records(follow.path("01")), {})

    def test_a_gone_session_is_told_once(self):
        follow.take("01", "10", "a", "b")
        with patch.object(wait_tool, "GRACE", 0):
            said = self.run_wait({"10": "gone"})
            self.assertIn("Woke on 10.", said)
            self.assertIn("It stays yours until it is resumed", said)
            again = self.run_wait({"10": "gone"})
        self.assertIn("at its limit", again)
        self.assertIn("As told before.", again)

    def test_a_gone_session_told_before_never_spins_the_wait(self):
        follow.take("01", "10", "a", "b")
        follow.update("01", follow.path("01"), lambda d: d["10"].update({"gone": SID["10"]}))
        asked = []

        def until(check, files=(), pids=(), seconds=0):
            asked.append(seconds)
            time.sleep(min(seconds, 0.2))
            return check()
        out = io.StringIO()
        with patch.object(finish, "read", return_value=finish.found("gone")), \
                patch.object(hear, "until", side_effect=until), patch.object(wait_tool, "GRACE", 0.1), \
                redirect_stdout(out):
            wait_tool.seat_main("01", SID["01"], 1)
        self.assertIn("at its limit", out.getvalue())
        self.assertLess(len(asked), 15)

    def idle_run(self, mark, seed=True):
        """The one wait over a followed 10 and a driven 11, both idle since
        `mark`, IDLE two seconds. Each hear's seconds are kept in self.asked."""
        if seed:
            follow.take("01", "10", "a", "b")
            successor.take("01", ["11"], "t")
            for p in (follow.path("01"), successor.path("01")):
                follow.update("01", p, lambda d: [r.update({"bookmark": mark}) for r in d.values()])
        self.asked = []

        def until(check, files=(), pids=(), seconds=0):
            self.asked.append(seconds)
            time.sleep(min(seconds, 0.3))
            return check()
        out = io.StringIO()
        with patch.object(finish, "read", return_value=finish.found("idle")), \
                patch.object(hear, "until", side_effect=until), patch.object(wait_tool.wake, "IDLE", (2,)), \
                redirect_stdout(out):
            wait_tool.seat_main("01", SID["01"], 3)
        return out.getvalue()

    def test_driven_and_followed_sessions_both_wake_it_idle(self):
        said = self.idle_run(time.strftime(wait_tool.STAMP))
        self.assertTrue(said.startswith("Woke on 10, 11, idle."))

    def test_an_idle_stretch_due_while_no_wait_ran_wakes_it_at_once(self):
        said = self.idle_run(time.strftime(wait_tool.STAMP, time.localtime(time.time() - 3)))
        self.assertTrue(said.startswith("Woke on 10, 11, idle."))
        self.assertEqual(self.asked, [])

    def test_past_its_last_time_an_idle_stretch_wakes_nothing_again(self):
        mark = time.strftime(wait_tool.STAMP, time.localtime(time.time() - 3))
        self.idle_run(mark)
        said = self.idle_run(mark, seed=False)
        self.assertTrue(said.startswith("Woke at its limit"))
        self.assertLess(len(self.asked), 15)

    def test_a_followed_session_wakes_it_idle_no_more_once_i_wrote_to_its_follower(self):
        mark = time.strftime(wait_tool.STAMP, time.localtime(time.time() - 3))
        mine = time.strftime(wait_tool.STAMP, time.localtime(time.time() + 5))
        with patch.object(transcripts, "turns", return_value=TURNS + [("User", "", ["elsewhere"], mine)]):
            said = self.idle_run(mark)
        self.assertTrue(said.startswith("Woke on 11, idle."))

    def test_the_idle_times_are_2_5_10_30_60_120_minutes(self):
        self.assertEqual(wait_tool.wake.IDLE, tuple(m * 60 for m in (2, 5, 10, 30, 60, 120)))

    def test_each_wake_waits_for_the_next_time_never_a_cascade(self):
        now = time.time()
        stamp = time.strftime(wait_tool.STAMP, time.localtime(now - 400))
        base = time.mktime(time.strptime(stamp, wait_tool.STAMP))
        self.assertEqual(wait_tool.idle_at(stamp, 0), base + 120)
        self.assertEqual(wait_tool.idle_at(stamp, now), base + 600)
        self.assertEqual(wait_tool.idle_at(stamp, base + 7200), 0)
        self.assertEqual(wait_tool.idle_at("", now), 0)

    def test_a_second_wait_on_a_seat_is_refused(self):
        follow.take("01", "10", "a", "b")
        import fcntl
        fd = os.open(os.path.join(registry.folder("01"), "wakes.log"), os.O_RDWR | os.O_CREAT)
        fcntl.flock(fd, fcntl.LOCK_EX)
        try:
            self.assertIn("A wait already runs for seat 01", self.run_wait({"10": "asking"}))
        finally:
            os.close(fd)

    def test_a_seat_following_nothing_waits_on_nothing(self):
        self.assertEqual(self.run_wait({}).strip(), "Following and driving nothing.")

    def test_a_take_while_it_waits_joins_it(self):
        follow.take("01", "10", "a", "b")
        calls = []

        def until(check, *a, **k):
            if not calls:
                calls.append(1)
                follow.take("01", "12", "c", "d")
            return check()
        out = io.StringIO()
        with patch.object(finish, "read", side_effect=lambda n, m="": finish.found(
                "asking" if n == "12" else "working", "2026-10-29T17:10:00")), \
                patch.object(hear, "until", side_effect=until), redirect_stdout(out):
            wait_tool.seat_main("01", SID["01"], 60)
        self.assertTrue(out.getvalue().startswith("Woke on 12."))


class DrivenFinishTest(Seats):
    """A driven session's real transcript, read by the real finish: its turn
    over, nothing it sent to the background running, its move a Wait."""

    def finished(self, move: str, ago: int = 0, waits: bool = False) -> str:
        """Session 11 answers my last words, its turn over on MOVE, AGO
        seconds back, then the one wait, driven by 01, runs as
        session-control arms it. WAITS: its turn armed a wait of its own in
        the background, still running."""
        utc = lambda s: time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime(time.time() - ago - s))
        own = ({"type": "assistant", "uuid": "a0", "parentUuid": "u1", "timestamp": utc(50),
                "message": {"role": "assistant", "content": [
                    {"type": "tool_use", "id": "t1", "name": "Bash",
                     "input": {"command": "python3 .claude/tools/transcript.py wait --awake",
                               "run_in_background": True}}]}},
               {"type": "user", "uuid": "r1", "parentUuid": "a0", "timestamp": utc(40),
                "toolUseResult": {"backgroundTaskId": "b1"},
                "message": {"role": "user", "content": [
                    {"type": "tool_result", "tool_use_id": "t1",
                     "content": "Command running in background with ID: b1."}]}}) if waits else ()
        with open(self.held["11"]["transcript"], "w") as f:
            for d in ({"type": "user", "uuid": "u1", "parentUuid": None, "timestamp": utc(60),
                       "message": {"role": "user", "content": "Run /session-report as the mission says, then wait."}},
                      *own,
                      {"type": "assistant", "uuid": "a1", "parentUuid": "r1" if waits else "u1", "timestamp": utc(30),
                       "message": {"role": "assistant", "content": [
                           {"type": "text", "text": f"The report is written.\n\n**Your move**\n{move}"}]}},
                      {"type": "system", "subtype": "turn_duration", "uuid": "s1", "parentUuid": "a1",
                       "timestamp": utc(30)}):
                f.write(json.dumps(d) + "\n")
        registry.TAILS.pop(self.held["11"]["transcript"], None)
        successor.take("01", ["11"])
        follow.update("01", successor.path("01"), lambda d: d["11"].update(
            {"bookmark": time.strftime(wait_tool.STAMP, time.localtime(time.time() - ago - 45))}))
        out = io.StringIO()
        live = {SID["11"]: {"status": "idle", "pid": 999999, "startedAt": 0}}
        with patch.object(registry, "claude_records", return_value=live), \
                patch.object(hear, "until", side_effect=lambda check, *a, **k: check()), \
                patch.dict(os.environ, {"CLAUDE_CODE_SESSION_ID": SID["01"]}), redirect_stdout(out):
            wait_tool.seat_main("01", SID["01"], 0)
        return out.getvalue()

    def test_a_finish_waiting_on_its_own_stop_wakes_its_driver(self):
        # Session 61's own words, at 18:15 on 13 November: they once read
        # working forever, and its driver never woke.
        said = self.finished("Wait: nothing is running. Session 11 is finished. "
                             "Stop it with `/9-session-stop` when you are done.")
        self.assertTrue(said.startswith("Woke on 11."), said)
        self.assertIn("State: done", said)

    def test_a_wait_with_nothing_running_wakes_its_driver_idle(self):
        # Its turn ended three minutes back: its first idle time, two minutes on, has come.
        said = self.finished("Wait: session 05 speaks next.", ago=180)
        self.assertTrue(said.startswith("Woke on 11, idle."), said)

    def test_a_wait_on_its_own_background_wait_still_works(self):
        # A driver of its own, its wait armed: it works, and wakes nobody.
        said = self.finished("Wait: session 05 speaks next.", ago=180, waits=True)
        self.assertTrue(said.startswith("Woke at its limit"), said)
        self.assertIn("State: working", said)


class HoldTest(Seats):
    def test_the_one_wait_covers_everything_and_a_named_one_its_own(self):
        procs = {500: (100, "python3 .claude/tools/transcript.py wait --awake"),
                 501: (100, "python3 .claude/tools/transcript.py wait 12 --since 2026-10-29T17:08:34 --awake")}
        with patch.object(unwatched.ports, "table", return_value=procs):
            self.assertEqual(unwatched.waits(100), [None, {"12"}])

    def test_a_follower_with_no_wait_is_held_once(self):
        follow.take("01", "10", "a", "b")
        live = {SID["01"]: {"pid": 100}, SID["10"]: {"pid": 200}}
        out = io.StringIO()
        with patch.object(registry, "claude_records", return_value=live), \
                patch.object(unwatched, "waits", return_value=[{"12"}]), \
                patch.object(unwatched.handover, "progress", return_value={}), \
                patch("sys.stdin", io.StringIO(json.dumps({"session_id": SID["01"]}))), redirect_stdout(out):
            unwatched.main()
        said = json.loads(out.getvalue())
        self.assertEqual(said["decision"], "block")
        self.assertIn("session 10", said["reason"])
        self.assertIn(successor.WAIT, said["reason"])

    def test_the_one_wait_running_passes(self):
        follow.take("01", "10", "a", "b")
        live = {SID["01"]: {"pid": 100}, SID["10"]: {"pid": 200}}
        out = io.StringIO()
        with patch.object(registry, "claude_records", return_value=live), \
                patch.object(unwatched, "waits", return_value=[None]), \
                patch.object(unwatched.handover, "progress", return_value={}), \
                patch("sys.stdin", io.StringIO(json.dumps({"session_id": SID["01"]}))), redirect_stdout(out):
            with self.assertRaises(SystemExit):
                unwatched.main()
        self.assertEqual(out.getvalue(), "")

    def ended(self, said, covers=(), title=""):
        """What the hook prints for seat 01's turn ending on `said`."""
        if title:
            self.held["01"]["title"] = title
        live = {SID[n]: {"pid": 100 + int(n)} for n in SID}
        event = {"session_id": SID["01"], "last_assistant_message": said}
        out = io.StringIO()
        with patch.object(registry, "claude_records", return_value=live), \
                patch.object(unwatched, "waits", return_value=list(covers)), \
                patch.object(unwatched.handover, "progress", return_value={}), \
                patch("sys.stdin", io.StringIO(json.dumps(event))), redirect_stdout(out):
            try:
                unwatched.main()
            except SystemExit:
                pass
        return out.getvalue()

    def test_a_wait_line_names_every_session(self):
        self.assertEqual(unwatched.waited_on("Done.\n\n**Your move**\n\nWait: sessions 10, 11 and 12 answer. "
                                             "I then launch stage B."), ["10", "11", "12"])
        self.assertEqual(unwatched.waited_on("Wait: this session's 3 agents finish near 15:40."), [])
        self.assertEqual(unwatched.waited_on("I read session 10.\n\nRuling: keep it."), [])

    def test_a_wait_with_no_step_of_mine_passes(self):
        """Told to stay idle, a seat waits on the one that stops it: no wake."""
        self.assertEqual(unwatched.waited_on("Wait: session 01 keeps my folder, then stops this session."), [])
        self.assertEqual(self.ended("Wait: session 01 stops this session. It sits idle until then."), "")

    def test_a_wait_on_a_session_nothing_watches_is_held(self):
        said = json.loads(self.ended("Wait: session 10 reworks its wave. I then fold its items."))
        self.assertEqual(said["decision"], "block")
        self.assertIn("session 10", said["reason"])
        self.assertIn("`follow`", said["reason"])

    def test_a_wait_on_a_watched_session_passes(self):
        self.assertEqual(self.ended("Wait: session 12 answers.", [{"12"}]), "")
        follow.take("01", "10", "a", "b")
        self.assertEqual(self.ended("Wait: session 10 reworks its wave.", [None]), "")

    def test_an_advisor_waits_with_no_follow(self):
        self.assertEqual(self.ended("Wait: session 10 reworks its wave.", title="01-advisor"), "")


if __name__ == "__main__":
    unittest.main()
