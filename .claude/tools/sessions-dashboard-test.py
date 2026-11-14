#!/usr/bin/env python3
"""Check the System page draws whatever outsource.json holds, and that its
presses answer what they did: a refusal in one sentence, or success.

The gate refuses each fault it was grown for. Given this session's
number, a restart whose gate is red leaves the server it would replace
as it was: 1100's own code, serving the made-up folder on this session's
port, 11NN.

  sessions-dashboard-test.py [NN] [Test...]
  sessions-dashboard-test.py serve --port P    1100's code, serving lib/trial.py's made-up folder
"""

import contextlib
import http.client
import importlib.util
import io
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("sessions_dashboard_test", os.path.join(HERE, "sessions-dashboard.py"))
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)

# This session's number, when given: the restart check serves on its port.
NN = next((a for a in sys.argv[1:] if re.fullmatch(r"\d{2}", a)), "")
# Set to a folder, `serve` makes its made-up folder inside that one, which
# the test removes, so a server killed leaves nothing behind.
MADE_UP = "SESSIONS_DASHBOARD_TEST_MADE_UP"
# Set, the gate's own program, sessions-dashboard.py check, runs with
# GateTest's fault in memory: a transcript's task notice read against a
# table. SITE, put on PYTHONPATH from the test's folder, puts it there
# before the gate reads a line. One it cannot put in ends the gate red,
# saying so, which the check refuses as the wrong red.
FAULT = "SESSIONS_DASHBOARD_TEST_FAULT"
SITE = """import os, sys
if os.environ.get({fault!r}) and os.path.basename(sys.argv[0]) == "sessions-dashboard.py" and sys.argv[1:2] == ["check"]:
    try:
        sys.path.insert(0, {lib!r})
        import transcripts
        transcripts.USED = {{}}
    except BaseException as e:
        sys.exit(f"The fault could not be put in: {{e!r}}")
"""

BROKEN = {"no engines": {"default": "codex"}, "an engine missing": {"engines": {}},
          "a model missing": {"engines": {"codex": {"effort": "max"}}},
          "engines a list": {"engines": []}, "the file a list": [1]}


class EnginesTest(unittest.TestCase):
    def test_a_broken_file_shows_no_engine_card(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "outsource.json")
            for name, got in BROKEN.items():
                with self.subTest(name), open(path, "w") as f:
                    json.dump(got, f)
                with self.subTest(name), patch.object(tool.engines, "CONFIG", path):
                    self.assertEqual(tool.engines_seen(), {})
                    self.assertNotIn('class="eng"', tool.system.drawn())

    def test_a_whole_file_shows_the_codex_card(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "outsource.json")
            with open(path, "w") as f:
                json.dump({"engines": {"codex": {"model": "m", "effort": "max"}}}, f)
            with patch.object(tool.engines, "CONFIG", path):
                self.assertEqual(sorted(tool.engines_seen()), ["codex"])


A = tool.accounts.KNOWN[0]
SEEN = {"codex": {"set": {"model": "m"}, "models": {"m": (["low", "high"], "low"), "bare": ([], "")}}}
SAVES = [(tool.accounts, "save"), (tool.accounts, "save_effort"), (tool.accounts, "save_model"),
         (tool.accounts, "save_own"), (tool.engines, "save"), (tool.context, "save")]


class SettingsTest(unittest.TestCase):
    def press(self, form, model="claude-opus-5-5"):
        """The system page's press, every save a mock: its answer, and the mocks."""
        mocks = {}
        with contextlib.ExitStack() as stack:
            for owner, name in SAVES:
                mocks[(owner.__name__, name)] = stack.enter_context(patch.object(owner, name))
            stack.enter_context(patch.object(tool, "engines_seen", return_value=SEEN))
            stack.enter_context(patch.object(tool.models, "families", return_value=[("opus", "claude-opus-5-5")]))
            stack.enter_context(patch.object(tool.accounts, "settings", return_value={}))
            stack.enter_context(patch.object(tool.accounts, "own", return_value={"model": model}))
            return tool.take(form, "/"), mocks

    def test_a_bad_value_is_refused_in_one_sentence_and_saves_nothing(self):
        bad = {"order": ({"order": ["9x"]}, f"Order '9x' is refused. Use only accounts "),
               "effort": ({"effort": ["huge"]}, "Effort 'huge' is refused. Choose low, medium, high, xhigh or max."),
               "model": ({"model": ["no good"]}, "Model 'no good' is refused. "),
               "account": ({"own": ["x"]}, "Account 'x' is refused. "),
               "own model": ({"own": [A], "own_model": ["nope"]}, f"Model 'nope' is refused for claude-{A}. Choose opus."),
               "own effort": ({"own": [A], "own_effort": ["max"]},
                              f"Effort 'max' is refused for claude-{A}. Choose low, medium, high or xhigh."),
               "engine": ({"engine": ["nope"]}, "Engine 'nope' is refused. Choose codex."),
               "engine model": ({"engine": ["codex"], "engine_model": ["nope"]},
                                "Model 'nope' is refused for codex. Choose m or bare."),
               "engine effort": ({"engine": ["codex"], "engine_effort": ["max"]},
                                 "Effort 'max' is refused for codex's m. Choose low or high."),
               "no effort": ({"engine": ["codex"], "engine_model": ["bare"], "engine_effort": ["low"]},
                             "Effort 'low' is refused. codex's bare takes no effort."),
               "threshold": ({"threshold": ["150"]}, "Threshold '150' is refused. Choose a whole percent from 1 to 99."),
               "wrapup": ({"wrapup": ["0"]}, "Wrap-up '0' is refused. Choose a whole percent from 1 to 99.")}
        for name, (form, said) in bad.items():
            with self.subTest(name):
                why, mocks = self.press(form)
                self.assertTrue(why.startswith(said), why)
                self.assertFalse([k for k, m in mocks.items() if m.called])
        why, mocks = self.press({"own": [A], "own_effort": ["high"]}, model="")
        self.assertEqual(why, f"claude-{A} has no model saved. Pick its model first, then its effort.")
        self.assertFalse([k for k, m in mocks.items() if m.called])

    def test_a_good_value_saves_as_before(self):
        good = [({"order": [A]}, ("accounts", "save"), ([A],)),
                ({"effort": ["high"]}, ("accounts", "save_effort"), ("high",)),
                ({"model": ["opus"]}, ("accounts", "save_model"), ("opus",)),
                ({"own": [A], "own_model": ["opus"]}, ("accounts", "save_own"), (A, "opus", "")),
                ({"own": [A], "own_effort": ["high"]}, ("accounts", "save_own"), (A, "", "high")),
                ({"engine": ["codex"], "engine_effort": ["high"]}, ("engines", "save"), ("codex", "", "high")),
                ({"threshold": ["40"]}, ("context", "save"), ("threshold", "40")),
                ({"wrapup": ["60"]}, ("context", "save"), ("wrapup", "60"))]
        for form, which, args in good:
            with self.subTest(form):
                why, mocks = self.press(form)
                self.assertEqual(why, "")
                mocks[which].assert_called_once_with(*args)


FOUND = [{"id": "f1", "buttons": [{"verb": "dismiss"}]}]


class GuardTest(unittest.TestCase):
    def guard(self, code, out, err=""):
        """A finding's button, posted to /system as 1100's table takes it."""
        done = subprocess.CompletedProcess([], code, out, err)
        with patch.object(tool.system, "findings", return_value=FOUND), \
                patch.object(tool.subprocess, "run", return_value=done):
            return tool.served().take({"act": ["dismiss"], "finding": ["f1"]}, "/system").run()

    def test_the_guard_buttons_act_from_the_system_page(self):
        self.assertEqual(self.guard(0, "dismissed f1\n"), "dismissed f1")
        self.assertEqual(tool.take({"act": ["dismiss"]}, "/elsewhere"), tool.NO_PRESS)

    def test_a_guard_that_acted_answers_success_with_its_line(self):
        self.assertIsInstance(self.guard(0, "dismissed f1\n"), tool.serve.Said)

    def test_a_guard_that_failed_is_refused(self):
        why = self.guard(1, "", "Traceback\nValueError: broken")
        self.assertEqual(why, "ValueError: broken")
        self.assertNotIsInstance(why, tool.serve.Said)
        closed = tool.system.act("f1", "dismiss", read=lambda: [])
        self.assertEqual(closed, "This finding is already closed. Nothing was done.")
        self.assertNotIsInstance(closed, tool.serve.Said)


class AnswerTest(unittest.TestCase):
    def test_said_is_200_with_its_line_a_refusal_409_and_nothing_303(self):
        answers = {"said": tool.serve.Said("dismissed f1"), "refused": "Effort 'huge' is refused.", "done": ""}
        with socket.socket() as s:
            s.bind(("127.0.0.1", 0))
            port = s.getsockname()[1]
        folder = tempfile.mkdtemp()
        with patch.object(tool.serve, "pidfile", return_value=os.path.join(folder, "pid")):
            threading.Thread(target=tool.serve.run, args=("said-test", port, lambda: ""),
                             kwargs={"take": lambda form: answers[form["k"][0]]}, daemon=True).start()
            got = {}
            for k in answers:
                for _ in range(50):
                    try:
                        conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
                        conn.request("POST", "/", f"k={k}", {"Host": f"127.0.0.1:{port}"})
                        r = conn.getresponse()
                        got[k] = (r.status, r.read().decode())
                        break
                    except ConnectionRefusedError:
                        time.sleep(0.1)
        self.assertEqual(got, {"said": (200, "dismissed f1"), "refused": (409, "Effort 'huge' is refused."),
                               "done": (303, "")})


class GateTest(unittest.TestCase):
    """The gate before every restart: it passes today's code, and refuses each fault it was grown for."""

    def bound_twice(self, source: str):
        seen = {}
        for node in tool.ast.parse(source).body:
            for name in tool.bound(node):
                if name in seen:
                    return name
                seen[name] = node.lineno
        return ""

    def refused(self) -> str:
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(Exception) as caught:
            tool.made_up()
        return str(caught.exception)

    def test_the_made_up_folder_holds_every_kind_of_page_and_all_draw(self):
        drawn = tool.made_up()
        for kind in ("assistant", "clarify", "explanation", "handover", "jury", "launch", "shots", "transcript", "walk"):
            self.assertTrue(any(path.startswith(f"made-up /p/{kind}/") for path in drawn), kind)
        self.assertIn("made-up /", drawn)

    def test_a_name_bound_twice_is_found_and_imports_and_keys_are_not(self):
        self.assertEqual(self.bound_twice("import re\nUSED = re.compile('x')\nUSED: dict = {}\n"), "USED")
        self.assertEqual(self.bound_twice("def a(): pass\ndef a(): pass\n"), "a")
        self.assertEqual(self.bound_twice("import urllib.error\nimport urllib.parse\nPATHS = {}\nPATHS['other'] = 1\n"), "")
        tool.twice()

    def test_a_draw_leaning_on_the_clock_is_refused(self):
        with patch.object(tool.views.assistant, "quiet", side_effect=lambda m, held: int(time.time())):
            self.assertIn("draws differently once the clock moves", self.refused())

    def test_a_draw_that_logs_an_error_is_refused(self):
        with patch.object(tool.transcript.transcripts, "USED", {}):
            self.assertIn("logged an error", self.refused())

    def test_a_press_that_is_not_refused_in_a_sentence_is_refused(self):
        for took in (lambda nn, form: "", lambda nn, form: {}["act"]):
            with patch.object(tool.views.jury.LIVE, "take", took):
                self.refused()

    def test_a_draw_that_starts_a_program_is_refused(self):
        was = tool.views.walk_list.LIVE.draw
        started = lambda nn: (subprocess.run(["/bin/ls"], capture_output=True), was(nn))[1]
        with patch.object(tool.views.walk_list.LIVE, "draw", started):
            self.assertIn("started a program", self.refused())

    def test_a_shared_script_that_does_not_parse_is_refused(self):
        if not tool.node():
            self.skipTest("this Mac holds no Node")
        tool.parsed({})
        with tempfile.TemporaryDirectory() as folder, patch.object(tool.live, "SCRIPTS", folder):
            with open(os.path.join(folder, "broken.js"), "w") as f:
                f.write("(() => { const live = ; })();\n")
            with self.assertRaises(SyntaxError) as caught:
                tool.parsed({})
        self.assertIn("broken.js", str(caught.exception))


class RestartTest(unittest.TestCase):
    """Code that fails the gate never reaches 1100: restart() keeps the server it runs.

    restart() names its port and its pid file by this file's PORT and
    SKILL, so here they are this session's: 11NN, and the folder
    `serve --port 11NN` keeps its pid in. Nothing keeps the server, so a
    stop would show."""

    def test_a_red_gate_leaves_the_running_server_its_pid_its_port_and_its_answer(self):
        if not NN:
            self.skipTest("no session number given, so no port of its own to serve on")
        port = 1100 + int(NN) + tool.ports.SHIFT
        skill = f"{tool.SKILL}-{port % 100:02d}"
        self.assertFalse(tool.ports.answering(port), f"{port} already answers, so it is not this test's to serve on")
        folder = tempfile.mkdtemp(prefix="sessions-dashboard-test-")
        site = os.path.join(folder, "site")
        os.makedirs(site)
        # usercustomize, since Homebrew's Python finds its own packages through its sitecustomize.
        with open(os.path.join(site, "usercustomize.py"), "w") as f:
            f.write(SITE.format(fault=FAULT, lib=os.path.join(os.path.dirname(HERE), "lib")))
        started = tool.serve.start
        # Should the gate pass all the same, the code it starts serves the made-up folder too.
        made_up = lambda s, p, script: started(s, p, os.path.abspath(__file__))
        searched = os.pathsep.join(p for p in (site, os.environ.get("PYTHONPATH", "")) if p)
        try:
            with patch.dict(os.environ, {MADE_UP: folder}):
                self.assertEqual(started(skill, port, os.path.abspath(__file__)), "")
                before = (tool.serve.holder(port), tool.serve.kept(skill), tool.serve.healthy(port))
                began = time.time()
                with patch.dict(os.environ, {"PYTHONPATH": searched, FAULT: "1"}), \
                        patch.object(tool, "PORT", port), patch.object(tool, "SKILL", skill), \
                        patch.object(tool.serve, "start", made_up):
                    said = tool.restart()
                took = time.time() - began
                after = (tool.serve.holder(port), tool.serve.kept(skill), tool.serve.healthy(port))
            print(f"With its gate red, restart() took {took:.1f} s and said: {said} On {port}, before "
                  f"(listener, pid file, /health): {before}; after: {after}.", file=sys.stderr)
            self.assertTrue(before[0] and before[0] == before[1] and before[2], before)
            self.assertTrue(said.startswith("1100 kept its old code. The new code fails to draw:"), said)
            self.assertIn("logged an error", said)
            self.assertEqual(after, before)
        finally:
            # The port was free before, so whatever holds it now is this test's.
            tool.serve.stop(skill, port)
            for _ in range(50):
                if not tool.ports.answering(port):
                    break
                time.sleep(0.1)
            shutil.rmtree(folder, ignore_errors=True)


def serving(port: int) -> None:
    """1100's own code, its serve verb, on PORT over lib/trial.py's made-up folder."""
    tempfile.tempdir = os.environ.get(MADE_UP) or None
    with tool.trial.world():
        sys.argv = [os.path.join(HERE, "sessions-dashboard.py"), "serve", "--port", str(port)]
        tool.main()


class ModelTest(unittest.TestCase):
    """Home's model on the contract: the table keeps it until a file or a look it names moves."""

    def test_it_is_drawn_again_only_once_a_file_or_a_look_it_names_moved(self):
        home, drawn = tool.workstation, []
        real = home.model
        read = lambda table: json.loads(table.route("/model")[0])
        # No pulse beats here, so a picture's first moments are read like any other: YOUNG.
        with tool.trial.world() as w, patch.object(home, "model", lambda: drawn.append(1) or real()), \
                patch.object(tool.live, "YOUNG", 0):
            table = tool.live.Table([home.LIVE])
            first = table.keyof("/model")
            self.assertEqual((table.keyof("/model"), len(drawn)), (first, 1), "nothing written, nothing drawn")
            self.assertIn("launch:05", read(table)["pages"])
            w.put("05", "launch.json", json.dumps({"rows": []}))
            second = table.keyof("/model")
            self.assertNotEqual(second, first, "a launch page emptied")
            self.assertNotIn("launch:05", read(table)["pages"])
            was = read(table)["sessions"]["11"]["colour"]
            self.assertEqual(len(drawn), 2)
            gone = lambda pids, fresh=False: {int(p): "" for p in pids if int(p) != 40011}
            with patch.object(tool.ports, "started", gone):
                tool.trial.forget()
                self.assertNotEqual(table.keyof("/model"), second, "a program ended, with no file written")
                self.assertNotEqual(read(table)["sessions"]["11"]["colour"], was)
                self.assertEqual(len(drawn), 3)


if __name__ == "__main__":
    if sys.argv[1:2] == ["serve"]:
        serving(int(sys.argv[sys.argv.index("--port") + 1]))
    else:
        unittest.main(argv=[sys.argv[0]] + [a for a in sys.argv[1:] if a != NN])
