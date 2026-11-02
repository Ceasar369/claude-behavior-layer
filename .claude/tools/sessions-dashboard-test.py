#!/usr/bin/env python3
"""Check the System page draws whatever outsource.json holds."""

import importlib.util
import json
import os
import tempfile
import unittest
from unittest.mock import patch

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("sessions_dashboard_test", os.path.join(HERE, "sessions-dashboard.py"))
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)

BROKEN = {"no engines": {"default": "codex"}, "an engine missing": {"engines": {"codex": {"model": "m"}}},
          "a model missing": {"engines": {"codex": {"effort": "max"}, "grok": {"model": "g"}}},
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
                    self.assertNotIn('class="eng"', tool.system_page())

    def test_a_whole_file_shows_both_cards(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "outsource.json")
            with open(path, "w") as f:
                json.dump({"engines": {"codex": {"model": "m", "effort": "max"}, "grok": {"model": "g"}}}, f)
            with patch.object(tool.engines, "CONFIG", path):
                self.assertEqual(sorted(tool.engines_seen()), ["codex", "grok"])


if __name__ == "__main__":
    unittest.main()
