#!/usr/bin/env python3
"""Check show.py's targets and its order files, one per view, in a folder of its own."""

import json
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import show  # noqa: E402


class Show(unittest.TestCase):
    def setUp(self):
        work = tempfile.TemporaryDirectory()
        self.addCleanup(work.cleanup)
        order = os.path.join(work.name, "show", "order.json")
        for p in (patch.object(show, "ORDER", order),
                  patch.object(show.launch, "live", return_value={"05", "12"})):
            p.start()
            self.addCleanup(p.stop)

    def written(self, file: str = "") -> dict:
        with open(file or show.ORDER) as f:
            return json.load(f)

    def files(self) -> list:
        folder = os.path.dirname(show.ORDER)
        return sorted(os.listdir(folder)) if os.path.isdir(folder) else []

    def test_every_tool_is_shown(self):
        for tool in show.TOOLS:
            self.assertEqual(show.show(tool, view="1"), f"1100 shows {tool}, in view 1.")
            self.assertEqual(self.written()["target"], tool)

    def test_a_running_session_and_its_tabs_are_shown(self):
        for target in ("05", "05:transcript", "12:clarify", "12:assistant"):
            self.assertEqual(show.show(target, view="1"), f"1100 shows {target}, in view 1.")
            self.assertEqual(self.written()["target"], target)

    def test_a_target_is_read_bare(self):
        show.show("  Agenda ", view=" 1 ")
        self.assertEqual(self.written()["target"], "agenda")

    def test_an_unknown_target_is_refused_and_writes_nothing(self):
        for target, said in (("dashboard", "is no page"), ("5", "is no page"), ("05:nope", "is no tab"),
                             ("07", "Session 07 is not running.")):
            got = show.show(target, view="1")
            self.assertIn(said, got)
            self.assertEqual(self.files(), [], target)

    def test_each_order_is_stamped_past_the_last(self):
        self.assertEqual(show.key(), "0")
        show.show("agenda", view="1")
        first = self.written()["at"]
        self.assertEqual(show.key(), str(first))
        with patch.object(show.time, "time", return_value=0):
            show.show("files", view="1")
        self.assertEqual(self.written(), {"target": "files", "place": "", "at": first + 1})
        self.assertEqual(show.read(), self.written())

    def test_an_unreadable_order_reads_empty(self):
        os.makedirs(os.path.dirname(show.ORDER))
        with open(show.ORDER, "w") as f:
            f.write("not json")
        self.assertEqual(show.read(), {})
        self.assertEqual(show.key(), "0")

    # ---- one view per app chat ----

    def test_an_order_moves_its_own_view_and_no_other(self):
        self.assertEqual(show.show("agenda", view="1"), "1100 shows agenda, in view 1.")
        one = show.key("1")
        self.assertEqual(show.show("files", view="2"), "1100 shows files, in view 2.")
        self.assertEqual((show.read("1")["target"], show.read("2")["target"]), ("agenda", "files"))
        self.assertEqual(show.key("1"), one)
        self.assertEqual(show.key("3"), "0")
        self.assertEqual(self.files(), ["order-2.json", "order.json"])

    def test_a_move_naming_no_view_is_refused_and_writes_nothing(self):
        for view in ("", "0", "100", "07", "two", "1.5", None):
            self.assertEqual(show.show("agenda", view=view), show.NO_VIEW, view)
        self.assertEqual(show.show("agenda"), show.NO_VIEW)
        self.assertEqual(self.files(), [])

    def test_a_view_takes_two_digits_up_to_99(self):
        for view in ("10", "42", "99"):
            self.assertEqual(show.show("agenda", view=view), f"1100 shows agenda, in view {view}.")
            self.assertEqual(show.read(view)["target"], "agenda")
            self.assertEqual(show.last(), int(show.key(view)))
        self.assertEqual(self.files(), ["order-10.json", "order-42.json", "order-99.json"])
        self.assertEqual(show.key("1"), "0")

    # ---- the panels open right now ----

    def test_homes_counts_each_panel_asking_now_and_forgets_one_gone(self):
        with patch.object(show, "HOMES", {}), patch.object(show.time, "time", return_value=1000.0):
            show.asked("2", "a")
            show.asked("2", "b")
            show.asked("2", "a")
            show.asked("12", "c")
            show.asked("1", "")
            show.asked("0", "d")
            self.assertEqual(show.homes(), {"2": 2, "12": 1})
            # Panel b stops asking: it is gone OPEN seconds on.
            show.time.time.return_value = 1000.0 + show.OPEN
            show.asked("2", "a")
            show.time.time.return_value = 1000.5 + show.OPEN
            self.assertEqual(show.homes(), {"2": 1})
            self.assertEqual(show.HOMES, {("2", "a"): 1000.0 + show.OPEN})

    def test_a_view_is_already_open_past_one_panel(self):
        self.assertEqual([show.already("2", n) for n in (0, 1, 2, 3)],
                         ["", "", "View 2 is already open.", "View 2 is already open."])

    def test_an_order_that_stays_names_no_view_and_reaches_every_view(self):
        show.show("agenda", view="1")
        show.show("files", view="2")
        self.assertEqual(show.show("05:transcript", draft="Go on.", mark="#words", stay=True),
                         "1100 shows 05:transcript.")
        stay = self.written(show.stays())
        self.assertEqual({k: stay[k] for k in ("target", "draft", "mark", "stay")},
                         {"target": "05:transcript", "draft": "Go on.", "mark": "#words", "stay": True})
        for view in ("1", "2", "3"):
            self.assertEqual(show.read(view), stay, view)
        # Each view's own page still stands in its own file.
        self.assertEqual((self.written()["target"], self.written(show.path("2"))["target"]), ("agenda", "files"))

    def test_a_views_own_order_wins_once_newer_than_the_one_that_stays(self):
        show.show("05:clarify", mark="#t-1", stay=True)
        show.show("system", view="2")
        self.assertEqual(show.read("2")["target"], "system")
        self.assertEqual(show.read("1")["target"], "05:clarify")

    def test_every_stamp_is_past_every_other_views(self):
        with patch.object(show.time, "time", return_value=0):
            show.show("agenda", view="1")
            show.show("files", view="2")
            show.show("05:clarify", stay=True)
            show.show("system", view="1")
        stamps = [self.written(show.path("1"))["at"], self.written(show.path("2"))["at"],
                  self.written(show.stays())["at"]]
        self.assertEqual(stamps, [4, 2, 3])
        self.assertEqual(show.last(), 4)


if __name__ == "__main__":
    unittest.main()
