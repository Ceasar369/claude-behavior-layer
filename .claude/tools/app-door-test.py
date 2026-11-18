#!/usr/bin/env python3
"""Check every press on 1100 has its door tool in app-door.py's PRESSES,
or sits in DISPLAY_ONLY, and every page its read in READS. It reads each
page's take() as written, which pages take a press from each tool's
contract, LIVE, and the prototype page's act from its own script, so a
press added to a page and not to the door fails here. A key the door
maps that no page takes any more fails too. Tools, below, checks each
tool's arguments become the right press or command, and each read its
text, stubbed."""

import ast
import json
import os
import re
import sys
import tempfile
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
LIB = os.path.join(ROOT, ".claude", "lib")


def source(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def tool(name: str) -> str:
    return source(os.path.join(HERE, name))


def func(text: str, name: str = "take") -> str:
    """The first function of that name, nested or not, as written."""
    for node in ast.walk(ast.parse(text)):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return ast.get_source_segment(text, node)
    return ""


def constant(text: str, name: str):
    """A module-level literal, read without running the module."""
    for node in ast.parse(text).body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == name for t in node.targets):
            return ast.literal_eval(node.value)
    raise KeyError(name)


def names(group: str) -> set:
    """The acts a tuple names: each string, and each `mod.NAME` read from lib/mod.py."""
    found = set(re.findall(r'"(\w+)"', group))
    for mod, attr in re.findall(r"\b([a-z_]+)\.([A-Z_]+)\b", group):
        found.add(constant(source(os.path.join(LIB, f"{mod}.py")), attr))
    return found


def acts(body: str, var: str) -> set:
    """Every act a take compares `var` to: ==, !=, in (...), not in (...)."""
    found = set(re.findall(var + r' [!=]= "(\w+)"', body))
    for group in re.findall(var + r" (?:not )?in \(([^)]*)\)", body):
        found |= names(group)
    return found


def takers() -> set:
    """Every tool whose page on the contract takes a press, by its name,
    the -page aside: its LIVE, lib/live.py's, states a take, as written."""
    found = set()
    for name in (n for n in os.listdir(HERE) if n.endswith(".py")):
        for node in ast.parse(tool(name)).body:
            named = node.targets if isinstance(node, ast.Assign) else [getattr(node, "target", None)]
            if any(getattr(t, "id", "") == "LIVE" for t in named) and any(
                    isinstance(c, ast.Call) and ast.unparse(c.func) == "live.Page"
                    and any(k.arg == "take" for k in c.keywords) for c in ast.walk(node)):
                found.add(name[:-3].removesuffix("-page"))
    return found


def sent(kind: str) -> set:
    """Every act a page's own script, .claude/pages/scripts/<kind>.js, names in a
    press it sends, as live.post({act: 'send'}) does."""
    script = source(os.path.join(ROOT, ".claude", "pages", "scripts", f"{kind}.js"))
    return set(re.findall(r"""\bact:\s*['"]([^'"]+)['"]""", script))


def presses() -> tuple:
    """Every press found, as (page, act or field), and each problem in reading them."""
    found, wrong = set(), []

    def page(name: str, got: set) -> None:
        found.update((name, a) for a in got)

    # 1100's own take(): its routes, then the system page's fields at /.
    dash = func(tool("sessions-dashboard.py"))
    routes = set(re.findall(r"if (?:\w+ := )?\(?(?:\w+ := )?(\w+)\.fullmatch\(path\)", dash))
    routes |= set(re.findall(r'if path == "/(\w+)"', dash))
    known = {"TRANSCRIPT", "push", "EXPLANATION", "app"}
    wrong += [f"1100's take() has a route this test does not read: {r}." for r in sorted(routes - known)]
    if "documents.zip" in dash:
        found.add(("explanation", "download"))
    if "app" in routes:
        page("app", set(re.findall(r'if "(\w+)" in form', func(tool("sessions-dashboard.py"), "app_home"))))
    if "push.keep(form)" in dash:
        found.add(("push", "subscribe"))
    page("system", set(re.findall(r'if "(\w+)" in form', dash)))
    # A finding's act posts to /system itself, which System's pressed() takes.
    if '"act" not in form' in func(tool("system-page.py"), "pressed"):
        found.add(("system", "act"))

    # Each page on the contract that takes a press, by its tool's LIVE. The
    # system page's presses are read above, as its fields.
    read = {"transcript", "clarify", "assistant", "launch", "handover", "jury", "agenda", "library", "prototype",
            "system", "teams"}
    wrong += [f"1100 draws a page this test does not read: {n}." for n in sorted(takers() - read)]

    transcript = func(tool("transcript-page.py"))
    page("transcript", acts(transcript, r'get\("act"\)'))
    advisor = tool("advisor-page.py")
    how = re.search(r"how not in \(([^)]*)\)", func(advisor)).group(1)
    page("advisor", names(how) | (set(constant(advisor, "LINES")) if "*LINES" in how else set()))
    page("clarify", acts(func(tool("clarify-page.py")), "act"))
    page("assistant", acts(func(tool("assistant-page.py")), "act"))
    launch = func(tool("launch-page.py"))
    page("launch", acts(launch, r'get\("act"\)') | ({"rows"} if 'get("rows")' in launch else set()))
    if func(tool("handover-page.py")):
        found.add(("handover", "press"))
    page("jury", acts(func(tool("jury-page.py")), "act"))
    page("agenda", set(re.findall(r'"(\w+)" (?:not )?in form', func(tool("agenda-page.py")))))
    if func(tool("library-page.py")):
        found.add(("library", "review"))
    page("teams", acts(func(tool("teams-page.py"), "pressed"), r'get\("act"\)'))

    # The prototype page's Send, as its own script sends it.
    page("prototype", sent("prototype"))
    return found, wrong


# ---- each tool's arguments, as the press or command they become --------------------
# The door loaded as a module, with pressed(), the launch and the reaper
# stubbed: nothing here reaches 1100, iTerm or a session.

def loaded():
    import importlib.util
    spec = importlib.util.spec_from_file_location("app_door", os.path.join(HERE, "app-door.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class Tools(unittest.TestCase):

    def stub(self, owner, name, value):
        """A shared module's name replaced for one test, then put back."""
        p = mock.patch.object(owner, name, value)
        p.start()
        self.addCleanup(p.stop)

    def setUp(self):
        self.v = loaded()
        self.stub(self.v.door, "shut", lambda: False)
        self.stub(self.v.door, "log", lambda *a: None)
        # Every order a test makes lands in a folder of its own, never on my 1100.
        orders = tempfile.mkdtemp()
        self.stub(self.v.show, "FOLDER", orders)
        self.stub(self.v.show, "ORDER", os.path.join(orders, "order.json"))
        self.posts, self.answer = [], (200, "")
        self.v.pressed = lambda path, form: (self.posts.append((path, form)), self.answer)[1]
        self.gets = []
        self.v.fetched = lambda path: (self.gets.append(path), "")[1]
        # What the chat last read lives in a folder of its own, read up to date.
        self.v.READ = os.path.join(tempfile.mkdtemp(), "read.json")
        self.v.mark_read(rules=self.v.rules_now(), tools=self.v.tools_now())

    def call(self, tool_name, **args):
        return self.v.call(tool_name, args)

    def test_every_tool_listed_is_called(self):
        listed = {t["name"] for t in self.v.TOOLS}
        self.assertTrue({"draft_reply", "write_launch", "stop_session"} <= listed)
        for name in listed:
            self.assertFalse(self.call(name)[0].startswith("No tool"), name)

    def test_the_served_list_is_numbered_in_its_two_groups(self):
        served = self.v.answer({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})["result"]["tools"]
        self.assertEqual([t["name"] for t in served], [
            "read_rules", "list_sessions", "read_session", "read_session_files", "read_file", "list_folder",
            "read_wave", "read_agenda", "read_system", "read_skills", "read_launch", "read_explanation",
            "read_library", "search_library", "read_word", "read_graph", "show_page", "draft_reply",
            "mark_library_review", "write_launch", "launch_rows", "stop_session", "set_system", "answer_item",
            "send_message"])
        for n, t in enumerate(served, 1):
            self.assertTrue(t["annotations"]["title"].startswith(f"{n:02d} "), t["name"])
            self.assertIs(t["annotations"]["readOnlyHint"], n <= 19, t["name"])
        self.assertEqual(served[0]["annotations"]["title"], "01 Read my rules")
        # The app sorts each group by title: two digits keep my order.
        titles = [t["annotations"]["title"] for t in served]
        self.assertEqual(titles[:19], sorted(titles[:19]))
        self.assertEqual(titles[19:], sorted(titles[19:]))

    def test_no_tool_is_marked_destructive(self):
        for t in self.v.TOOLS:
            self.assertFalse(t["annotations"].get("destructiveHint"), t["name"])

    # ---- the desktop extension ----

    def piped(self, text: str):
        """The app's pipe holding TEXT, and the door's answers, as lines."""
        import io
        self.stub(self.v.sys, "stdin", io.TextIOWrapper(io.BufferedReader(io.BytesIO(text.encode()))))
        pipe = io.StringIO()
        self.stub(self.v.sys, "stdout", pipe)
        self.stub(self.v.sys, "stderr", io.StringIO())
        return pipe

    def test_stdio_answers_each_line_and_nothing_stray_reaches_the_pipe(self):
        lines = [{"jsonrpc": "2.0", "id": 1, "method": "ping"},
                 {"jsonrpc": "2.0", "method": "notifications/initialized"},
                 {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}]
        pipe = self.piped("\n".join(map(json.dumps, lines)) + "\nnot json\n")
        self.v.stdio()
        got = [json.loads(line) for line in pipe.getvalue().splitlines()]
        self.assertEqual([g["id"] for g in got], [1, 2, None])
        self.assertEqual(len(got[1]["result"]["tools"]), len(self.v.TOOLS))
        self.assertEqual(got[2]["error"]["code"], -32700)

    def test_a_changed_account_list_restarts_the_door_with_the_message_it_holds(self):
        ping = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "ping"}) + "\n"
        pipe = self.piped(ping + ping)
        self.stub(self.v.accounts, "changed", lambda: True)
        execs = []

        def execve(path, argv, env):
            execs.append((argv[1:], env[self.v.PENDING]))
            self.assertEqual(os.path.basename(argv[1]), "app-door.py")
            raise SystemExit
        self.stub(self.v.os, "execve", execve)
        with self.assertRaises(SystemExit):
            self.v.stdio()
        self.assertEqual([(argv[1:], held) for argv, held in execs], [(["stdio"], ping)])
        self.assertEqual(pipe.getvalue(), "")
        # The second message still waits on the pipe, for the door that follows.
        self.assertEqual(self.v.sys.stdin.buffer.raw.read().decode(), ping)

    def test_a_restarted_door_answers_the_message_it_was_handed_first(self):
        pipe = self.piped(json.dumps({"jsonrpc": "2.0", "id": 2, "method": "ping"}) + "\n")
        self.stub(self.v.os, "environ", {self.v.PENDING: json.dumps({"jsonrpc": "2.0", "id": 1, "method": "ping"})})
        self.v.stdio()
        self.assertEqual([json.loads(line)["id"] for line in pipe.getvalue().splitlines()], [1, 2])
        self.assertNotIn(self.v.PENDING, self.v.os.environ)

    def test_the_extension_packs_its_manifest_and_starter(self):
        import zipfile
        self.stub(self.v.door, "STATE", tempfile.mkdtemp())
        with zipfile.ZipFile(self.v.extension()) as z:
            manifest = json.loads(z.read("manifest.json"))
            starter = z.read("server/main.py").decode()
        self.assertEqual(manifest["display_name"], f"{self.v.project.NAME} sessions")
        self.assertEqual(manifest["server"]["mcp_config"]["args"], ["${__dirname}/server/main.py"])
        self.assertEqual([t["name"] for t in manifest["tools"]], [t["name"] for t in self.v.TOOLS])
        self.assertIn(repr(os.path.join(HERE, "app-door.py")), starter)
        self.assertIn('"stdio"', starter)

    # ---- what the chat last read ----

    def test_a_rules_change_refuses_each_call_until_read_rules(self):
        self.stub(self.v.page, "colours", lambda: {})
        self.v.mark_read(rules="older")
        refused = ("My rules changed since you read them. Call read_rules, then make this call again.", True)
        self.assertEqual(self.call("list_sessions"), refused)
        self.assertEqual(self.call("stop_session", session="04"), refused)
        self.assertEqual(self.posts, [])
        words, failed = self.call("read_rules")
        self.assertFalse(failed)
        self.assertEqual(words, source(self.v.RULES).strip())
        self.assertEqual(self.call("list_sessions"), ("No session is running.", False))

    def test_a_tools_change_is_said_once_until_a_new_list(self):
        self.stub(self.v.page, "colours", lambda: {})
        self.v.mark_read(tools="older")
        note = "No session is running.\n\nMy tools changed since this chat began. Quit and reopen the Claude app to get them."
        self.assertEqual(self.call("list_sessions"), (note, False))
        self.assertEqual(self.call("list_sessions"), ("No session is running.", False))
        self.v.answer({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
        self.assertEqual(self.v.last_read()["tools"], self.v.tools_now())

    def test_a_session_tool_needs_two_digits(self):
        for name in ("read_session", "stop_session"):
            self.assertEqual(self.call(name, session="x"), ("Name the session by its two digits.", True))
        self.assertEqual(self.posts, [])

    # ---- my own launch page ----

    def fake_mine(self, rows):
        """My own launch page holding these rows, read afresh at each load."""
        lp = type("L", (), {})()
        lp.load = lambda nn: [dict(r) for r in rows] if nn == "00" else []
        lp.scheduled = lambda nn: ""
        lp.system = lambda row, key: {"account": "1", "model": "claude-opus-5-5", "effort": "medium"}[key]
        self.stub(self.v.page, "tool", lambda name: {"launch-page": lp}[name])
        self.stub(self.v.launch, "line", lambda row: "claude ...")
        self.shown = []
        self.stub(self.v.show, "show", lambda target, place="", mark="", stay=False: self.shown.append((target, stay))
                  or f"1100 shows {target}.")

    def test_write_launch_adds_a_row_the_app_chat_wrote_and_moves_no_page(self):
        self.fake_mine([{"uid": 1, "name": "mine", "message": "Go."}])
        self.assertEqual(self.call("write_launch", name="cache", message="Check the cache.", account="2",
                                   effort="max", self_drive=True),
                         ("Row 2 on your launch page holds cache. It waits there for you to fine-tune, "
                          "and launches on your press or your word.", False))
        self.assertEqual(self.posts, [("/p/launch/00", {"act": "save", "seen": "[1]", "rows": json.dumps([
            {"uid": 1, "name": "mine", "message": "Go."},
            {"uid": 2, "by": "app", "name": "cache", "message": "Check the cache.", "account": "2",
             "effort": "max", "drive": True}])})])
        self.assertEqual(self.shown, [("launch", True)])

    def test_write_launch_keeps_the_number_out_of_the_name_and_takes_settings_as_spoken(self):
        """My app chat wrote "09 session-03-mistake", so the page showed 09 twice."""
        self.fake_mine([])
        self.stub(self.v.models, "families", lambda: [("opus", "claude-opus-5-5"), ("sonnet", "claude-sonnet-5-5")])
        self.stub(self.v.models, "catalog", lambda: {"models": [{"id": "claude-opus-5-5"}, {"id": "claude-sonnet-5-5"}]})
        self.assertFalse(self.call("write_launch", name="09 session-03-mistake", message="Go.", account="account 2",
                                   model="Sonnet", effort="High", self_drive=False)[1])
        self.assertEqual(json.loads(self.posts[-1][1]["rows"]), [
            {"uid": 1, "by": "app", "name": "session-03-mistake", "message": "Go.", "n": "09", "account": "2",
             "model": "claude-sonnet-5-5", "effort": "high", "drive": False}])
        self.call("write_launch", name="Session 07 - cache", number="11", message="Go.", model="opus 5.5")
        self.assertEqual({k: json.loads(self.posts[-1][1]["rows"])[0][k] for k in ("name", "n", "model")},
                         {"name": "cache", "n": "11", "model": "claude-opus-5-5"})

    def test_write_launch_places_a_row_where_i_say(self):
        """I said "under session 04", and dragged the row there myself."""
        self.fake_mine([{"uid": 1, "name": "mine", "win": "L:w1", "tab": "L:t1"}])
        self.stub(self.v.iterm, "tree", lambda: [{"window": "w1", "tabs": [
            {"tab": "t1", "root": {"split": "v", "children": [{"pane": "P4"}, {"pane": "P5"}]}}]}])
        self.stub(self.v.panes, "pane_of", lambda nn: {"04": "P4"}.get(nn, ""))
        rows = lambda: json.loads(self.posts[-1][1]["rows"])
        self.assertEqual(self.call("write_launch", message="Go.", near="04", side="below")[0].split(". ")[1],
                         "It lands below session 04")
        self.assertEqual({k: rows()[1][k] for k in ("win", "tab", "at")},
                         {"win": "L:w1", "tab": "L:t1", "at": {"anchor": "p:P4", "side": "down"}})
        self.call("write_launch", message="Go.", near="row 1", side="right")
        self.assertEqual(rows()[1]["at"], {"anchor": "r:1", "side": "right"})
        self.call("write_launch", message="Go.", side="new window")
        self.assertEqual({k: rows()[1][k] for k in ("win", "tab", "at")}, {"win": "N1", "tab": "N1", "at": None})
        self.call("write_launch", message="Go.", near="04", side="new tab")
        self.assertEqual({k: rows()[1][k] for k in ("win", "tab", "at")}, {"win": "L:w1", "tab": "N1", "at": None})
        count = len(self.posts)
        self.assertEqual(self.call("write_launch", message="Go.", near="07"),
                         ("Session 07 has no pane open, so nothing was placed. Nothing was written.", True))
        self.assertEqual(self.call("write_launch", message="Go.", near="04", side="behind")[1], True)
        self.assertEqual(len(self.posts), count)

    def test_write_launch_changes_or_removes_only_rows_the_app_chat_wrote(self):
        self.fake_mine([{"uid": 1, "name": "mine"},
                        {"uid": 2, "by": "app", "name": "cache", "message": "Go.", "model": "claude-opus-5-5"}])
        self.assertEqual(self.call("write_launch", row="1", account="2"),
                         ("Row 1 is yours, not the app chat's. It stays as it is.", True))
        self.assertEqual(self.call("write_launch", row="9", account="2"),
                         ("Your launch page has no row 9. Nothing was written.", True))
        self.assertEqual(self.posts, [])
        self.assertFalse(self.call("write_launch", row="2", model="system", account="3")[1])
        self.assertEqual(json.loads(self.posts[-1][1]["rows"])[1],
                         {"uid": 2, "by": "app", "name": "cache", "message": "Go.", "model": "claude-opus-5-5",
                          "account": "3"})
        self.assertEqual(self.call("write_launch", row="2", remove=True),
                         ("Row 2 is gone from your launch page.", False))
        self.assertEqual((json.loads(self.posts[-1][1]["rows"]), self.posts[-1][1]["seen"]),
                         ([{"uid": 1, "name": "mine"}], "[1, 2]"))

    def test_write_launch_writes_a_clone_and_refuses_one_with_no_conversation(self):
        self.fake_mine([])
        self.stub(self.v.launch, "cloned", lambda nn: {"session_id": "34c5-abcd"} if nn == "01" else {})
        self.assertFalse(self.call("write_launch", message="/clone-session", clone="1")[1])
        self.assertEqual(json.loads(self.posts[-1][1]["rows"])[0]["clone"], "01")
        count = len(self.posts)
        self.assertEqual(self.call("write_launch", message="/clone-session", clone="77"),
                         ("Session 77 has no conversation to clone.", True))
        self.assertEqual(len(self.posts), count)

    def test_write_launch_refuses_no_words_a_bad_number_or_value(self):
        self.fake_mine([])
        self.assertEqual(self.call("write_launch", name="x"),
                         ("No words to open the session with. Nothing was written.", True))
        self.assertEqual(self.call("write_launch", message="Go.", number="2"),
                         ("A number is two digits, like 02. Nothing was written.", True))
        self.stub(self.v.launch, "line", lambda row: "")
        self.assertEqual(self.call("write_launch", message="Go.", effort="huge"),
                         ("That account, model or effort is refused. Nothing was written.", True))
        self.assertEqual((self.posts, self.shown), ([], []))
        self.answer = (200, "A launch is booting on this page, so nothing was saved.")
        self.stub(self.v.launch, "line", lambda row: "claude ...")
        self.assertEqual(self.call("write_launch", message="Go."),
                         ("A launch is booting on this page, so nothing was saved.", True))

    def test_launch_rows_on_my_page_launches_only_rows_the_app_chat_wrote(self):
        rows = [{"uid": 1, "name": "mine", "n": "04"}, {"uid": 2, "by": "app", "name": "cache", "n": "05"}]
        self.fake_mine(rows)
        self.assertEqual(self.call("read_launch", session="00"), (
            "Session 00's launch page, 2 rows.\nRow 1: session 04, mine.\n"
            "Row 2: session 05, cache, the app chat wrote it.", False))
        self.assertEqual(self.call("launch_rows", session="00"), (
            "Launching the 1 row the app chat wrote on your launch page. Your other rows stay as they are.", False))
        self.assertEqual(self.posts, [("/p/launch/00", {"act": "launch", "rows": json.dumps(rows),
                                                        "seen": "[1, 2]", "only": "[2]"})])
        self.fake_mine(rows[:1])
        self.assertEqual(self.call("launch_rows", session="00"), (
            "No row on your launch page is one the app chat wrote. Yours wait for your own press. Nothing launched.",
            True))
        self.assertEqual(len(self.posts), 1)

    # ---- a reply drafted in a session's box ----

    def test_draft_reply_fills_the_box_and_never_sends(self):
        orders = []
        self.stub(self.v.show, "show", lambda target, place="", draft="", mark="", stay=False:
                  orders.append((target, place, draft, mark, stay)) or f"1100 shows {target}.")
        self.assertEqual(self.call("draft_reply", session="05", text="Fold in item 3."),
                         ("Your reply to session 05 waits in its box, unsent.", False))
        self.assertEqual(orders, [("05:transcript", "", "Fold in item 3.", "#words", True)])
        self.assertEqual(self.posts, [])
        self.assertEqual(self.call("draft_reply", session="05", text="  "), ("Nothing to draft.", True))
        self.assertEqual(len(orders), 1)

    def test_send_message_types_into_each_session_named_or_none(self):
        typed = []
        ok = {"02": "", "05": "", "08": "Session 08 sits at a dialog. Nothing was typed."}
        self.stub(self.v.page, "typable", lambda nn, statuses: (ok.get(nn, "none"), {}, f"pane-{nn}"))
        self.stub(self.v.panes, "say", lambda pane, line: typed.append((pane, line)) or True)
        self.assertEqual(self.call("send_message", sessions="02, 5", text="Fix gap 1."),
                         ("Sent to sessions 02 and 05.", False))
        self.assertEqual(self.call("send_message", sessions="02", text="One."), ("Sent to session 02.", False))
        self.assertEqual(self.call("send_message", sessions="02 08", text="Two."),
                         ("Session 08 sits at a dialog. Nothing was sent. No session got it.", True))
        self.assertEqual(self.call("send_message", sessions="02", text="  "), ("Nothing to send.", True))
        self.assertEqual(self.call("send_message", sessions="all", text="Hi."),
                         ("Name each session by its two digits. Nothing was sent.", True))
        self.assertEqual(typed, [("pane-02", "Fix gap 1."), ("pane-05", "Fix gap 1."), ("pane-02", "One.")])

    def test_answer_item_presses_agree_or_feedback_and_never_send(self):
        self.assertEqual(self.call("answer_item", session="02", item="1", answer="agree"),
                         ("Item 1: agree saved on session 02's Clarify tab. Send stays yours.", False))
        self.call("answer_item", session="02", item="2", answer="feedback", text="Drop the formal name.")
        self.assertEqual(self.posts, [("/p/clarify/02", {"act": "agree", "n": "1", "on": "yes"}),
                                      ("/p/clarify/02", {"act": "feedback", "n": "2", "text": "Drop the formal name."})])
        self.assertEqual(self.call("answer_item", session="02", item="3", answer="feedback"),
                         ("Feedback needs its words. Nothing was saved.", True))
        self.answer = (409, "Wave 1 has no item 9. Nothing was saved.")
        self.assertEqual(self.call("answer_item", session="02", item="9", answer="agree"),
                         ("Wave 1 has no item 9. Nothing was saved.", True))
        self.assertEqual(len(self.posts), 3)

    def test_stop_session_ends_as_the_reaper_does(self):
        ended, closed = [], []
        record = {"session_id": "abc"}
        self.stub(self.v.registry, "entries", lambda: {"05": record})
        self.stub(self.v.registry, "pid_of", lambda r: 4242)
        fake = type("R", (), {})()
        fake.panes = type("P", (), {"pane": staticmethod(lambda r: "pane-5")})()
        fake.end = lambda n, r: (ended.append((n, r)), (4242, []))[1]
        fake.close = lambda pids, shut: closed.append((pids, shut))
        self.v.reaper = lambda: fake
        self.stub(self.v.threading, "Thread", lambda target, args, daemon: type(
            "T", (), {"start": lambda s: target(*args)})())
        self.assertEqual(self.call("stop_session", session="5"),
                         ("Session 05 ended. Its folder was deleted.", False))
        self.assertEqual((ended, closed), ([("05", record)], [([4242], ["pane-5"])]))

    def test_stop_session_refuses_a_session_not_running(self):
        self.v.reaper = lambda: self.fail("the reaper is never loaded")
        self.stub(self.v.registry, "entries", lambda: {"05": {"session_id": "abc"}})
        self.stub(self.v.registry, "pid_of", lambda r: 0)
        self.assertEqual(self.call("stop_session", session="05"),
                         ("Session 05 is not running. Nothing was ended.", True))
        self.assertEqual(self.call("stop_session", session="06"),
                         ("Session 06 is not running. Nothing was ended.", True))

    def test_the_reaper_loads_with_end_and_close(self):
        r = self.v.reaper()
        self.assertTrue(callable(r.end) and callable(r.close) and callable(r.panes.pane))

    # ---- clarify ----

    def fake_clarify(self, head, items, waves=(3,)):
        """Waves 1 to 3, each file empty: parse hands back head and items."""
        c = type("C", (), {})()
        empty = tempfile.NamedTemporaryFile("w", suffix=".md", delete=False)
        empty.close()
        self.addCleanup(os.unlink, empty.name)
        c.waves = lambda nn: [(n, empty.name) for n in waves]
        c.parse = lambda text: (head, items)
        c.then = lambda h: "/clarify-items"
        c.answered = lambda it: bool(it.get("feedback")) or it.get("agree") == "yes"
        c.opinions = lambda it: [{"v": "agree", "by": "30", "words": ""}] if it.get("proposed") else []
        c.proposes = lambda it: it.get("proposed", "").startswith("agree")
        self.stub(self.v.page, "tool", lambda name: {"clarify-page": c}[name])
        self.stub(self.v.page, "colours", lambda: {})

    def test_read_wave_names_each_helper_still_silent_on_an_item(self):
        self.fake_clarify({"sent": ""}, [
            {"n": "12", "title": "Cap retries", "question": "Cap at three?", "decision": "Cap at three."},
            {"n": "14", "title": "Open", "question": "Open?", "decision": "Yes.", "proposed": "agree"}])
        self.stub(self.v.page, "colours", lambda: {"30": ("green", "working", "helper")})
        words, _ = self.call("read_wave", session="04")
        self.assertEqual(words.count("No opinion yet from session 30, still working."), 1)
        self.assertTrue(self.call("read_wave", session="04", item="12")[0].endswith(
            "No opinion yet from session 30, still working."))
        self.stub(self.v.page, "colours", lambda: {"30": ("red", "waits", "helper")})
        self.assertIn("No opinion yet from session 30, which waits on you.", self.call("read_wave", session="04")[0])
        self.stub(self.v.page, "colours", lambda: {})
        self.assertNotIn("No opinion yet", self.call("read_wave", session="04")[0])

    def test_read_wave_reads_each_item_as_text(self):
        self.fake_clarify({"sent": ""}, [
            {"n": "12", "title": "Cap retries", "question": "Cap at three?", "decision": "Cap at three.",
             "agree": "yes"},
            {"n": "13", "title": "Name it", "question": "Which name?", "decision": "message", "feedback": "Call it say."},
            {"n": "14", "title": "Open", "question": "Open?", "decision": "Yes.", "proposed": "agree"}])
        words, failed = self.call("read_wave", session="04")
        self.assertFalse(failed)
        self.assertTrue(words.startswith("Session 04's wave 3 of 3, 3 items, ready to send."))
        for line in ("Send types /clarify-items.", "Item 12, Cap retries.", "Question: Cap at three?",
                     "Decision: Cap at three.", "My answer: agreed.", "My answer: feedback: Call it say.",
                     "My answer: none yet.", "Session 30 proposed: agree."):
            self.assertIn(line, words)
        self.assertNotIn("<", words)

    def test_read_wave_reads_a_sent_wave_and_one_item_whole(self):
        self.fake_clarify({"sent": "yes"}, [{"n": "12", "title": "Cap retries", "question": "Cap at three?",
                                             "why": "One row retried forty thousand times.", "agree": "yes"}], (1, 2))
        words, failed = self.call("read_wave", session="04", wave="1")
        self.assertFalse(failed)
        self.assertTrue(words.startswith("Session 04's wave 1 of 2, 1 item, sent."))
        self.assertNotIn("Send types", words)
        whole = ("Wave 2, item 12, Cap retries.\nQuestion: Cap at three?\nWhy: One row retried forty thousand "
                 "times.\nMy answer: agreed.", False)
        self.assertEqual(self.call("read_wave", session="04", wave="2", item="12"), whole)
        # No wave named: the newest wave holding the item.
        self.assertEqual(self.call("read_wave", session="04", item="12"), whole)
        self.assertEqual(self.call("read_wave", session="04", item="99"),
                         ("No wave of session 04 holds item 99.", True))
        self.assertEqual(self.call("read_wave", session="04", wave="9"),
                         ("Session 04 has no wave 9. Its waves run 1 to 2.", True))

    # ---- the agenda ----

    def fake_agenda(self):
        self.stub(self.v.agenda, "PHASES", ("1", "2"))
        self.stub(self.v.agenda, "HEADINGS", {"1": "Phase 1: First Launch"})
        self.stub(self.v.agenda, "NAMES", ("Money", "Docs"))
        items = [
            {"id": "dark-mode", "title": "Dark mode", "phase": "1", "after": [], "topics": ["Docs"],
             "note": "What: Do, small: Dark mode.\nMine: the Apple account."},
            {"id": "export-button", "title": "Export button", "phase": "1", "after": ["dark-mode"], "topics": ["Money"],
             "note": "What: Fix, large: Acme and Globex."},
            {"id": "search", "title": "Search", "phase": "2", "after": [], "topics": ["Money"],
             "note": "What: Do, medium: search."}]
        self.stub(self.v.agenda, "world", lambda: {"broken": [], "items": items})
        self.stub(self.v.agenda, "read", lambda: ({it["id"]: it for it in items}, []))

    def test_read_agenda_sums_each_phase(self):
        self.fake_agenda()
        self.assertEqual(self.call("read_agenda"), (
            "Phase 1: First Launch: 2 items, 1 waits on you.\nMine: Dark mode.\nOthers: Export button.\n\n"
            "Phase 2: 1 item, 0 wait on you.\nOthers: Search.\n\nTopics: Money, Docs. Orders: 1 to 2.", False))

    def test_read_agenda_reads_an_item_a_topic_and_an_order(self):
        self.fake_agenda()
        self.assertEqual(self.call("read_agenda", item="Export button"), (
            "Export button. File export-button. Order 2. Phase 1: First Launch.\nTopics: Money.\n"
            "Waits on: Dark mode.\nWaiting on it: nothing.\n\nWhat: Fix, large: Acme and Globex.", False))
        self.assertEqual(self.call("read_agenda", topic="money"), (
            "Topic money: 2 items.\nSearch, order 1.\nExport button, order 2.", False))
        self.assertEqual(self.call("read_agenda", order="1"), (
            "Order 1: 2 items.\nDark mode, order 1, waits on you.\nSearch, order 1.", False))
        self.assertEqual(self.call("read_agenda", item="Nope"), ("No agenda item Nope.", True))

    def test_read_agenda_finds_by_title_and_note(self):
        self.fake_agenda()
        self.assertEqual(self.call("read_agenda", query="globex"),
                         ("1 item matches globex.\n\nExport button\nWhat: Fix, large: Acme and Globex.", False))
        self.assertEqual(self.call("read_agenda", query="zebra"), ("No agenda item matches zebra.", False))

    # ---- System ----

    def fake_dash(self):
        d = type("D", (), {})()
        d.PLANS, d.DATABASE, d.LEVELS = {"1": "20x"}, ("Database", [(6543, "Store")]), {"stop": ("red", "Stopped")}
        d.BAND = [("Shop", [(8100, "Backend"), (8200, "Frontend")])]
        d.clock = lambda epoch: "18:00"
        d.usage = lambda held: {"1": {"read": 1, "on": ["05"], "five": (36.0, 0), "week": (17.0, 0)}}
        d.seen = lambda: ({6543: True, 8100: True, 8200: False}, [(8205, "node"), (9000, "Slack")])
        d.other = lambda titles, listening: [(8205, "node", "05-login"), (9000, "Slack", "")]
        d.findings = lambda: [{"id": "stop-0001", "level": "stop", "title": "Memory guard: ended a browser",
                               "line": "Ended session 21's browser.", "buttons": [{"verb": "tell", "label": "Tell 21"}]}]
        d.engines_seen = lambda: {"codex": {"set": {"model": "gpt-6", "effort": "max"}}}
        d.engines = type("E", (), {"NAMES": {"codex": "Codex"}})
        d.size = lambda n: f"{n} B"
        self.v.dash = lambda: d
        self.stub(self.v.registry, "entries", lambda: {})
        self.stub(self.v.ports, "in_scheme", lambda p: p == 8205)
        self.stub(self.v.accounts, "read", lambda: {"order": ["2", "1"], "next": 1})
        self.stub(self.v.accounts, "effort", lambda: "high")
        self.stub(self.v.accounts, "model", lambda: "claude-opus-5-5")
        self.stub(self.v.accounts, "KNOWN", ["1"])
        self.stub(self.v.accounts, "own", lambda a: {"saved": "", "model": "", "effort": ""})
        self.stub(self.v.models, "name", lambda m: "Opus 5.5")
        self.stub(self.v.context, "threshold", lambda: 70)
        self.stub(self.v.context, "wrapup", lambda: 80)

    def test_read_system_reads_each_part_as_text(self):
        self.fake_dash()
        for part, line in [("usage", "claude-1, 20x: 5-hour 36% used; 7-day 17% used."),
                           ("ports", "Shop: 8100 Backend up, 8200 Frontend down."),
                           ("ports", "Port 8205, node, 05-login."), ("ports", "And 1 port of other apps."),
                           ("guard", "Finding stop-0001, Stopped: Ended session 21's browser."),
                           ("guard", "Its acts: tell, Tell 21."),
                           ("settings", "Account order: 2 1, the next launch takes 1."),
                           ("settings", "Started by hand: claude-1 nothing saved."),
                           ("settings", "Outsource engines: Codex gpt-6, max."),
                           ("settings", "Handover at 70% of context, wrap-up at 80%.")]:
            words, failed = self.call("read_system", part=part)
            self.assertFalse(failed, part)
            self.assertIn(line, words, part)
        words, failed = self.call("read_system")
        self.assertIn("Band 00: 2 of 3 up; down: 8200 Frontend.", words)
        self.assertIn("Memory guard: 1 finding open.\nended a browser.", words)
        self.assertNotIn("<", words)
        self.assertTrue(self.call("read_system", part="nope")[1])

    def test_set_system_posts_systems_field(self):
        for args, form, said in [
                ({"setting": "effort", "value": "high"}, {"effort": "high"}, "The default effort is now high."),
                ({"setting": "order", "value": "2 1"}, {"order": "2 1"}, "The account order is now 2 1."),
                ({"setting": "threshold", "value": "65"}, {"threshold": "65"}, "The handover threshold is now 65."),
                ({"setting": "own_model", "value": "opus", "account": "2"}, {"own": "2", "own_model": "opus"},
                 "claude-2's own model is now opus."),
                ({"setting": "engine_effort", "value": "max", "engine": "codex"},
                 {"engine": "codex", "engine_effort": "max"}, "Codex's effort is now max.")]:
            self.posts.clear()
            self.assertEqual(self.call("set_system", **args), (said, False))
            self.assertEqual(self.posts, [("/", form)])

    def test_set_system_refuses_the_door_switch_and_passes_refusals(self):
        words, failed = self.call("set_system", setting="door", value="shut")
        self.assertTrue(failed)
        self.assertIn("app door", words)
        self.assertTrue(self.call("set_system", setting="own_model", value="opus")[1])
        self.assertTrue(self.call("set_system", setting="engine_model", value="x")[1])
        self.assertTrue(self.call("set_system", setting="colour", value="red")[1])
        self.assertEqual(self.posts, [])
        self.answer = (409, "Effort 'huge' is refused. Choose low, medium, high, xhigh or max.")
        self.assertEqual(self.call("set_system", setting="effort", value="huge"),
                         ("Effort 'huge' is refused. Choose low, medium, high, xhigh or max.", True))

    # ---- files ----

    def fake_project(self):
        root = os.path.realpath(tempfile.mkdtemp())
        os.makedirs(os.path.join(root, "docs", "deep"))
        for rel, data in [("README.md", b"one\ntwo\nthree\n"), ("docs/a.md", b"a\n"), ("docs/deep/b.md", b"b\n"),
                          ("pic.png", b"\x89PNG\0\0"), ("secret.env", b"KEY=1\n")]:
            with open(os.path.join(root, rel), "wb") as f:
                f.write(data)
        outside = tempfile.mkdtemp()
        with open(os.path.join(outside, "x.md"), "w") as f:
            f.write("outside\n")
        os.symlink(os.path.join(outside, "x.md"), os.path.join(root, "link.md"))
        self.stub(self.v.door, "ROOT", root)
        self.v.tracked = lambda: {"README.md", "docs/a.md", "docs/deep/b.md", "pic.png", "link.md"}
        self.v.dash = lambda: type("D", (), {"size": staticmethod(lambda n: f"{n} B")})

    def test_list_folder_lists_only_tracked(self):
        self.fake_project()
        self.assertEqual(self.call("list_folder"), (
            "The project: 1 folder, 3 files.\ndocs/, folder, 2 files\nREADME.md, md file, 14 B\n"
            "link.md, md file, 8 B\npic.png, picture, 6 B", False))
        self.assertEqual(self.call("list_folder", path="docs/"),
                         ("docs: 1 folder, 1 file.\ndeep/, folder, 1 file\na.md, md file, 2 B", False))
        self.assertTrue(self.call("list_folder", path="../")[1])
        self.assertTrue(self.call("list_folder", path="README.md")[1])

    def test_read_file_reads_lines_and_refuses_untracked_or_escaping(self):
        self.fake_project()
        self.assertEqual(self.call("read_file", path="README.md", start=2, lines=1),
                         ("README.md, lines 2 to 2 of 3.\n\ntwo", False))
        self.assertEqual(self.call("read_file", path="pic.png"),
                         ("pic.png is a picture, image/png, 6 B. It holds no text.", False))
        for path in ("secret.env", "../x.md", "/etc/passwd", "docs/../../x.md", "link.md", "docs"):
            words, failed = self.call("read_file", path=path)
            self.assertTrue(failed, path)
            self.assertTrue(words.startswith("Git tracks no file"), path)
        self.assertTrue(self.call("read_file", path="README.md", start=9)[1])

    def test_tracked_never_holds_the_doors_folder(self):
        self.assertFalse(any(f.startswith(".claude/state/door/") for f in loaded().tracked()))

    # ---- the library, skills, explanations ----

    def fake_library(self):
        lib = self.v.page.tool("library-page")
        root = tempfile.mkdtemp()
        os.makedirs(os.path.join(root, "graphs"))
        for rel, text in [
                ("library-MOC.md", "## Our API\n### Who may call\n- Graph: [[how-a-call-goes|How is a call answered?]]\n"
                                   "- [[api-key|API key]]\n"),
                ("api-key.md", "# API key\n\n## What it is\n\nA string sent with each `call`, see [[idempotency|keys]].\n\n"
                               "Source: https://docs.example.com/keys\n"),
                ("graphs/how-a-call-goes.md", "## The text\n\nSeries: Calls, 1 of 2\n\nA call is checked.\n\n"
                                              "- **Key** — who calls\n\n## The graph\n\n"
                                              "1. The call lands [[api-key]]\n   - no: Refused\n2. It is answered\n"
                                              "Figure: one call.\n")]:
            with open(os.path.join(root, rel), "w") as f:
                f.write(text)
        self.stub(lib, "LIBRARY", root)
        # Files named from the fake library's root, as the project's are from its own.
        self.stub(self.v.door, "ROOT", root)

    def test_library_searches_and_reads_words_and_graphs(self):
        self.fake_library()
        self.assertEqual(self.call("search_library", query="call"), (
            "2 matches for call.\nGraph A of subchapter 1.1, How is a call answered?\nWord 1.1.1, API key.", False))
        self.assertEqual(self.call("search_library", query="call", start=2), (
            "2 matches for call.\n2 to 2 of 2.\nWord 1.1.1, API key.", False))
        word = ("Word 1.1.1, API key.\n\nWhat it is.\nA string sent with each call, see keys.\n\n"
                "Explained in graph A of subchapter 1.1, How is a call answered?\n\n"
                "Source: https://docs.example.com/keys\n\nBefore it: Graph A of subchapter 1.1, How is a call answered?")
        for said in ("API key", "api-key", "1.1.1"):
            self.assertEqual(self.call("read_word", slug=said), (word, False))
        graph = ("Graph A of subchapter 1.1, How is a call answered?\nSeries: Calls, 1 of 2.\nA call is checked.\n"
                 "Key: who calls\n\nThe graph.\nStep 1: The call lands (word 1.1.1, API key). If no: Refused.\n"
                 "Step 2: It is answered.\nFigure: one call.\n\nAfter it: Word 1.1.1, API key.")
        for said in ("how-a-call-goes", "1.1.a"):
            self.assertEqual(self.call("read_graph", slug=said), (graph, False))
        self.assertTrue(self.call("read_word", slug="nothing")[1])
        self.assertTrue(self.call("search_library")[1])

    def test_mark_library_review_marks_as_the_page_button_does(self):
        self.fake_library()
        rv = self.v.page.tool("library-review")
        state = tempfile.mkdtemp()
        self.stub(rv, "FOLDER", state)
        self.stub(rv, "RECORD", os.path.join(state, "reviews.json"))
        self.assertEqual(self.call("mark_library_review", at="1.1.1", to="reviewed"),
                         ("Word 1.1.1, API key, is marked reviewed.", False))
        self.assertEqual(list(rv.load()), ["api-key"])
        self.assertEqual(self.call("mark_library_review", at="API key", to="not-reviewed"),
                         ("Word 1.1.1, API key, is marked not reviewed.", False))
        self.assertEqual(rv.load(), {})
        self.assertTrue(self.call("mark_library_review", at="9.9", to="reviewed")[1])

    def test_read_library_walks_the_contents_by_number(self):
        self.fake_library()
        self.assertEqual(self.call("read_library"), (
            "The library, 1 chapter.\nChapter 1, Our API, 2 items.\nSubchapter 1.1, Who may call, 2 items.", False))
        self.assertEqual(self.call("read_library", at="1"), (
            "Chapter 1, Our API, 2 items.\nSubchapter 1.1, Who may call, 2 items.", False))
        self.assertEqual(self.call("read_library", at="1.1"), (
            "Subchapter 1.1, Who may call, 2 items.\nGraph A of subchapter 1.1, How is a call answered?\n"
            "Word 1.1.1, API key.", False))
        self.assertEqual(self.call("read_library", at="1.1.1"), self.call("read_word", slug="api-key"))
        self.assertEqual(self.call("read_library", at="1.1.A"), self.call("read_graph", slug="how-a-call-goes"))
        self.assertTrue(self.call("read_library", at="7.2")[1])

    def test_read_skills_lists_families_and_finds(self):
        sk = self.v.page.tool("skills-page")
        self.stub(sk, "heads", lambda: [("6-agenda", "Calls the agenda skill. More.", ""),
                                        ("agenda-write", "Writes my agenda.", "[words]"), ("snippet", "Reads a paste.", "")])
        self.assertEqual(self.call("read_skills"), ("3 skills.\nNo family: /snippet.\n"
                                                    "Agenda, family 6: /6-agenda, /agenda-write.", False))
        self.assertEqual(self.call("read_skills", query="writes"),
                         ("1 skill for writes.\n/agenda-write, arguments: [words]. Writes my agenda.", False))
        self.assertEqual(self.call("read_skills", family="6", start=2), (
            "Agenda, family 6, 2 skills.\n2 to 2 of 2.\n/agenda-write, arguments: [words]. Writes my agenda.", False))
        self.assertTrue(self.call("read_skills", family="9")[1])

    def test_launch_rows_reads_and_presses_the_pages_launch(self):
        lp = type("L", (), {})()
        rows = [{"uid": "u1", "kind": "session", "n": "31", "name": "search", "message": "Go.", "account": "2"}]
        lp.load = lambda nn: rows
        lp.scheduled = lambda nn: ""
        self.stub(self.v.page, "tool", lambda name: {"launch-page": lp}[name])
        self.assertEqual(self.call("read_launch", session="20"), (
            "Session 20's launch page, 1 row.\nRow 1: session 31, search, account 2. First message: Go.", False))
        self.assertEqual(self.call("launch_rows", session="20"), ("Launching session 20's page: 1 row.", False))
        self.assertEqual(self.posts, [("/p/launch/20", {"act": "launch", "rows": json.dumps(rows),
                                                        "seen": json.dumps(["u1"])})])
        self.answer = (200, "Nothing launched. 31 is held by another launch.")
        self.assertEqual(self.call("launch_rows", session="20"),
                         ("Nothing launched. 31 is held by another launch.", True))

    def test_show_page_opens_one_item_inside_a_page(self):
        self.fake_library()
        ordered = []
        self.stub(self.v.show, "show", lambda target, place="", view="":
                  ordered.append((target, place, view)) or f"1100 shows {target}, in view {view}.")
        self.assertEqual(self.call("show_page", target="library", at="1.1.1", view="1"),
                         ("1100 shows library, in view 1. It opens 1.1.1.", False))
        self.call("show_page", target="library", at="1.1.A", view="2")
        self.call("show_page", target="05:jury", at="2026-11-05-1600", view="1")
        self.call("show_page", target="05:prototype", at="g2/v3", view="1")
        self.call("show_page", target="05:shots", at="4", view="1")
        self.call("show_page", target="05:clarify", at="12", view="1")
        self.assertEqual(ordered, [("library", "#api-key", "1"), ("library", "#graph:how-a-call-goes", "2"),
                                   ("05:jury", "?run=2026-11-05-1600", "1"), ("05:prototype", "#2/v3", "1"),
                                   ("05:shots", "#4", "1"), ("05:clarify", "#12", "1")])
        self.assertTrue(self.call("show_page", target="library", at="9.9", view="1")[1])
        self.assertTrue(self.call("show_page", target="system", at="x", view="1")[1])
        self.assertTrue(self.call("show_page", target="05:clarify", at="twelve", view="1")[1])
        self.assertEqual(len(ordered), 6)

    def test_show_page_naming_no_view_is_refused_and_orders_nothing(self):
        ordered = []
        self.stub(self.v.show, "show", lambda *a, **k: ordered.append(a) or "1100 shows system, in view 1.")
        for view in ({}, {"view": ""}, {"view": "0"}, {"view": "100"}, {"view": "two"}):
            self.assertEqual(self.call("show_page", target="system", **view), (self.v.show.NO_VIEW, True))
        self.assertEqual(ordered, [])

    def test_show_page_warns_once_another_panel_holds_its_view(self):
        self.stub(self.v.show, "show", lambda target, place="", view="": f"1100 shows {target}, in view {view}.")
        self.v.fetched = lambda path: (self.gets.append(path), '{"1": 1, "12": 2}')[1]
        self.assertEqual(self.call("show_page", target="system", view="12"),
                         ("1100 shows system, in view 12. View 12 is already open.", False))
        self.assertEqual(self.call("show_page", target="system", view="1"), ("1100 shows system, in view 1.", False))
        self.assertEqual(self.call("show_page", target="system", view="3"), ("1100 shows system, in view 3.", False))
        self.assertEqual(self.gets, ["/views"] * 3)
        # 1100 not answering, or answering no JSON, warns of nothing.
        for said in ("", "not json", "[]"):
            self.v.fetched = lambda path, said=said: said
            self.assertEqual(self.call("show_page", target="system", view="12"), ("1100 shows system, in view 12.", False))

    def test_read_explanation_lists_and_reads(self):
        base = tempfile.mkdtemp()
        with open(os.path.join(base, "whose-look.md"), "w") as f:
            f.write("# Whose look\n\nThe lede.\n")
        ep = type("E", (), {})()
        ep.numbered = lambda nn: [(2, "whose-look", os.path.join(base, "whose-look.md"), 0)]
        ep.heading = lambda p: ("Whose look", "The lede.")
        ep.when = lambda p, made: "Written Nov 5, 17:21"
        ep.text = source
        self.stub(self.v.page, "tool", lambda name: {"explanation-page": ep}[name])
        with open(os.path.join(base, "whose-look.md"), "a") as f:
            f.write("\n## Mine wins\n\nOne line.\n\n## Theirs follows\n\nTwo lines.\n")
        self.assertEqual(self.call("read_explanation", session="01"), (
            "Session 01's 1 document, newest first:\n"
            "Document 2, Whose look, named whose-look. The lede. Written Nov 5, 17:21.", False))
        for name in ("whose-look", "2", "whose-look.md"):
            self.assertEqual(self.call("read_explanation", session="01", name=name), (
                "Document 2 of 2, Whose look.\nThe lede.\n\nSection 1, Mine wins.\nSection 2, Theirs follows.\n\n"
                "Read one with its section number, or all.", False))
        self.assertEqual(self.call("read_explanation", session="01", name="2", section="2"),
                         ("Document 2, section 2 of 2.\n\n## Theirs follows\n\nTwo lines.", False))
        self.assertTrue(self.call("read_explanation", session="01", name="2", section="all")[0].startswith("# Whose"))
        self.assertTrue(self.call("read_explanation", session="01", name="2", section="3")[1])
        self.assertTrue(self.call("read_explanation", session="01", name="other")[1])


def pages() -> set:
    """Every page 1100 and 1400 draw: each tab kind, each rail tool, and
    the kinds show.py adds, as the team tab."""
    show = source(os.path.join(LIB, "show.py"))
    extra = re.search(r"^KINDS = \((.*)\)$", show, re.M).group(1)
    return (set(constant(source(os.path.join(LIB, "page.py")), "TAB_KINDS")) | set(constant(show, "TOOLS"))
            | set(re.findall(r'"(\w+)"', extra)))


class Reads(unittest.TestCase):
    """Each page names the door tool reading what it shows, and each is a tool."""

    def test_every_page_has_a_door_read(self):
        reads = constant(tool("app-door.py"), "READS")
        self.assertEqual(sorted(pages() - set(reads)), [], "A page no door tool reads.")
        self.assertEqual(sorted(set(reads) - pages()), [], "The door names a page 1100 no longer draws.")
        names = {t["name"] for t in loaded().TOOLS}
        self.assertEqual(sorted(set(reads.values()) - names - {None}), [], "A read names no door tool.")


def main() -> None:
    result = unittest.main(argv=[sys.argv[0]], exit=False, verbosity=1).result
    if not result.wasSuccessful():
        sys.exit("FAILED: the tool tests.")
    door = tool("app-door.py")
    mapped, skipped = constant(door, "PRESSES"), constant(door, "DISPLAY_ONLY")
    found, wrong = presses()
    wrong += [f"No door tool maps the press {k}." for k in sorted(found - set(mapped) - skipped)]
    wrong += [f"The door maps {k}, which no page takes." for k in sorted((set(mapped) | skipped) - found)]
    wrong += [f"{k} is both mapped and display only." for k in sorted(set(mapped) & skipped)]
    for line in wrong:
        print(line)
    if wrong:
        sys.exit(f"FAILED: {len(wrong)} problem{'s' * (len(wrong) > 1)}.")
    print(f"OK: {len(found)} presses, {len(mapped)} mapped, {len(skipped)} display only.")


if __name__ == "__main__":
    main()
