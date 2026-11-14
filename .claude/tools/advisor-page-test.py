#!/usr/bin/env python3
"""Check the advisor's panel: its list on seats in a folder of their own, never a real seat, its presses,
what it draws on the contract, and its page in WebKit and Chromium.

Drawn: on lib/trial.py's made-up folder, 1100 draws the panel's rows with
no script, and names the files that move them.

Browser: transcript-page-test.py's server, on this session's port, 11NN,
draws the advisor 01's Transcript tab on the contract. Each engine checks:

  A changed panel, put in place, equals the page drawn fresh, state by state.
  The panel keeps how I left it, a Type pressed types, and my typing
  holds, while its rows change, in one load.

  advisor-page-test.py [NN] [Lists|Groups|Presses|Drawn|Browser]
"""

import importlib.util
import os
import re
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "lib"))
import panes  # noqa: E402
import registry  # noqa: E402
import trial  # noqa: E402

spec = importlib.util.spec_from_file_location("advisor_page_test", os.path.join(HERE, "advisor-page.py"))
advisor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(advisor)
# The transcript page's own test: its made-up server, its states, its browser run.
found = importlib.util.spec_from_file_location("transcript_page_test", os.path.join(HERE, "transcript-page-test.py"))
tt = importlib.util.module_from_spec(found)
found.loader.exec_module(tt)


class Seats(unittest.TestCase):
    def setUp(self):
        work = tempfile.TemporaryDirectory()
        self.addCleanup(work.cleanup)
        self.held = {n: {"number": n, "title": f"{n}-test", "session_id": f"sid-{n}"}
                     for n in ("01", "02", "04", "05", "06")}
        for p in (patch.object(registry, "WORK", work.name),
                  patch.object(registry, "entries", side_effect=lambda: self.held),
                  patch.object(registry, "claude_records", return_value={}),
                  patch.object(panes, "ids", return_value=set()),
                  patch.object(advisor.page, "shown", side_effect=lambda n, *_: (f"{n}-test", "", "green", "", ""))):
            p.start()
            self.addCleanup(p.stop)


class Lists(Seats):
    def numbers(self, nn):
        return [r[0] for r in advisor.seen(nn)]

    def test_no_list_sees_every_session_but_itself(self):
        self.assertEqual(self.numbers("06"), ["01", "02", "04", "05"])

    def test_a_list_shows_only_its_sessions(self):
        advisor.keep_list("06", ["02", "04", "05"])
        self.assertEqual(self.numbers("06"), ["02", "04", "05"])

    def test_one_advisors_list_leaves_the_general_alone(self):
        advisor.keep_list("06", ["02"])
        self.assertEqual(self.numbers("01"), ["02", "04", "05", "06"])

    def test_a_reused_number_drops_out_and_the_list_stays_a_list(self):
        advisor.keep_list("06", ["02"])
        self.held["02"] = {**self.held["02"], "session_id": "sid-new"}
        self.assertEqual(self.numbers("06"), [])
        self.assertTrue(advisor.listing("06"))

    def test_an_empty_replacement_makes_it_general(self):
        advisor.keep_list("06", ["02"])
        advisor.keep_list("06", [])
        self.assertEqual(self.numbers("06"), ["01", "02", "04", "05"])


class Groups(Seats):
    def setUp(self):
        super().setUp()
        self.station = advisor.page.tool("workstation")
        self.plan = {"10": {"stages": [{}]}}
        p = patch.object(self.station.plans, "plan", side_effect=lambda h: self.plan.get(h, {}))
        p.start()
        self.addCleanup(p.stop)
        self.held["10"] = {"number": "10", "title": "10-lead", "session_id": "sid-10"}
        self.held["11"] = {"number": "11", "title": "11-member", "session_id": "sid-11"}
        self.real = self.station.views.advisor
        self.teams = [("01", []), ("02", []), ("04", []), ("05", []), ("06", []), ("10", ["11"])]
        self.seats = {"01": {"role": "advisor"}, "06": {"role": "advisor"}}

    def grouped(self):
        with patch.object(self.real, "listed", side_effect=lambda nn, held: {"06": ["02", "04", "10", "11"]}.get(nn, [])):
            return self.station.advisor_groups(self.teams, self.held, {**{n: {} for n in self.held}, **self.seats})

    def test_the_advisor_heads_its_group_whatever_its_number(self):
        self.assertIn(("06", ["02", "04"]), self.grouped())

    def test_a_grouped_session_leaves_the_rail_as_its_own_hub(self):
        heads = [h for h, _ in self.grouped()]
        self.assertNotIn("02", heads)
        self.assertIn("05", heads)

    def test_a_team_keeps_its_sessions(self):
        self.assertIn(("10", ["11"]), self.grouped())

    def test_a_general_advisor_stands_alone(self):
        self.assertIn(("01", []), self.grouped())


class Presses(Seats):
    def test_advising_on_itself_is_refused_and_types_nothing(self):
        with patch.object(advisor.page, "typable") as typable:
            said = advisor.take("06", {"act": ["advise"], "how": ["send"], "nn": ["06"]})
        self.assertEqual(said, "Session 06 cannot advise on itself. Nothing was typed.")
        self.assertFalse(typable.called)

    def test_an_unknown_button_is_refused_and_types_nothing(self):
        with patch.object(advisor.page, "typable") as typable:
            said = advisor.take("06", {"act": ["advise"], "how": ["shout"], "nn": ["02"]})
        self.assertEqual(said, "This page has no shout button. Nothing was typed.")
        self.assertFalse(typable.called)

    def test_a_malformed_number_is_refused_and_types_nothing(self):
        with patch.object(advisor.page, "typable") as typable:
            said = advisor.take("06", {"act": ["advise"], "how": ["send"], "nn": ["2x"]})
        self.assertEqual(said, "2x is not a session number. Nothing was typed.")
        self.assertFalse(typable.called)


class Drawn(unittest.TestCase):
    """What 1100 draws on the contract, from the made-up folder."""

    def setUp(self):
        world = trial.world()
        self.w = world.__enter__()
        self.addCleanup(world.__exit__, None, None, None)
        self.w.session("01", "advisor")

    def test_its_rows_draw_with_no_script(self):
        got = advisor.drawn("01")
        self.assertEqual(re.findall(r'class="row" data-nn="(\d\d)"', got), ["05", "10", "11"])
        self.assertNotIn("<script", got)

    def test_a_follow_and_a_drive_read_on_their_rows(self):
        tt.stand(self.w, "f")
        tt.stand(self.w, "g")
        got = advisor.drawn("01")
        self.assertIn('data-act="unfollow" title="Stop following session 05">Following</button>', got)
        self.assertIn('data-act="undrive" title="Stop driving session 11">Driving</button>', got)

    def test_its_files_name_its_list_follows_drives_and_every_record(self):
        named = advisor.files("01")
        for n in ("01", "05", "10", "11", "12"):
            self.assertIn(os.path.join(self.w.work, n, registry.RECORD), named)
        for f in (os.path.join(self.w.work, "01", advisor.LIST), advisor.follow.path("01"), advisor.successor.path("01")):
            self.assertIn(f, named)

    def test_it_has_no_page_of_its_own(self):
        self.assertEqual(advisor.LIVE, [])


BROWSERS = trial.SERVER + tt.SNAP + r"""
const url = base + '/p/transcript/01';

(async () => {
  for (const engine of engines) {
    ENGINE = engine.name();
    const browser = await engine.launch({headless: true});
    const context = await browser.newContext({viewport: {width: 1000, height: 760}});
    const open = opener(context);

    // A changed panel, put in place, equals the page drawn fresh, state by state.
    await state('0');
    const b = await open(), c = await open();
    await b.goto(url);
    await settled(b, '#adv.open');
    let same = [];
    for (const name of ['f', 'g', 'l', '0']) {
      await state(name);
      await wait(1800);
      await settled(b);
      await c.goto(url);
      await settled(c, '#adv.open');
      same.push(await snap(b) === await snap(c) ? name : name + ' differs');
    }
    said('fresh', same.every(s => !s.includes('differs')) && b.loads === 1, `put in place, then drawn fresh: ${same.join(', ')}; ${b.loads} load`);
    await b.close();
    await c.close();

    // Closed, it stays closed while its rows change; a Type pressed types;
    // my typing holds, in one load.
    await state('0');
    const t = await open();
    await t.goto(url);
    await settled(t, '#adv.open');
    await t.click('#atab');
    await t.click('#words');
    await t.keyboard.type('Which one');
    await state('f');
    await t.waitForSelector('#adv .btn.fo.on', {state: 'attached', timeout: 8000});
    await settled(t);
    const shut = await t.evaluate(() => !document.getElementById('adv').classList.contains('open'));
    await t.click('#atab');
    await t.click('#adv .row[data-nn="10"] button[data-act="type"]');
    await t.waitForFunction(() => document.querySelector('#adv .row[data-nn="10"] button[data-act="type"]').textContent === 'Typed',
                            null, {timeout: 6000}).catch(() => {});
    const line = await typedLine();
    const held = await t.evaluate(() => document.getElementById('words').value);
    said('panel', shut && line === 'Advise me on session 10. ' && held === 'Which one' && t.loads === 1,
         `closed through a change: ${shut}; Type typed "${line}"; the box read "${held}"; ${t.loads} load`);
    await t.close();
    await browser.close();
  }
})().catch(e => { console.error(e); process.exit(1); });
"""


class Browser(tt.Engines):
    SCRIPT = BROWSERS

    def test_a_changed_panel_put_in_place_equals_the_page_drawn_fresh(self):
        self.held("fresh")

    def test_the_panel_keeps_its_place_and_its_presses_while_it_changes(self):
        self.held("panel")


if __name__ == "__main__":
    unittest.main(argv=[sys.argv[0]] + [a for a in sys.argv[1:] if not re.fullmatch(r"\d{2}", a)])
