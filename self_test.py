#!/usr/bin/env python3
"""Three-tier self test for awesome-funnel-design (funnelkit.py).

All fixtures are invented; no real list data or marketing copy is used.
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import funnelkit as fk  # noqa: E402

CLI = [sys.executable, os.path.join(HERE, "funnelkit.py")]


def run_cli(*args):
    return subprocess.run(CLI + list(args), capture_output=True, text=True)


def manifest(sponsored=False):
    return {
        "meta": {"title": "sample", "disclosure": {"sponsored_slots": 4,
                                                    "owned_products_listed": 1}},
        "categories": [{"name": "editors",
                        "entries": [{"name": "tool-a", "url": "https://a.example",
                                     "sponsored": sponsored, "owned_by_maintainer": False},
                                    {"name": "tool-b", "url": "https://b.example",
                                     "sponsored": False, "owned_by_maintainer": True}]}],
    }


class TestFunctional(unittest.TestCase):
    def test_valid_manifest_passes(self):
        self.assertEqual(fk.validate_manifest(manifest()), [])

    def test_funnel_math(self):
        events = [{"entry": "tool-a", "event": "exposure"},
                  {"entry": "tool-a", "event": "exposure"},
                  {"entry": "tool-a", "event": "click"},
                  {"entry": "tool-a", "event": "conversion"}]
        r = fk.compute_funnel(events)
        s = r["per_entry"]["tool-a"]
        self.assertEqual((s["exposure"], s["click"], s["conversion"]), (2, 1, 1))
        self.assertEqual(s["ctr"], 0.5)
        self.assertEqual(s["cvr"], 1.0)
        self.assertEqual(r["totals"]["ctr"], 0.5)

    def test_sponsored_overcount_warns(self):
        m = manifest()
        m["meta"]["disclosure"]["sponsored_slots"] = 0
        m["categories"][0]["entries"][0]["sponsored"] = True
        issues = fk.validate_manifest(m)
        self.assertTrue(any("sponsored" in i["msg"] and i["severity"] == "warning"
                            for i in issues))

    def test_track_cli_output(self):
        fd, path = tempfile.mkstemp(suffix=".jsonl")
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(json.dumps({"entry": "tool-a", "event": "exposure"}) + "\n")
        self.addCleanup(os.remove, path)
        res = run_cli("track", "--events", path)
        self.assertEqual(res.returncode, 0)
        self.assertIn("Funnel report", res.stdout)


class TestErrorPaths(unittest.TestCase):
    def test_missing_disclosure_is_error(self):
        m = manifest()
        del m["meta"]["disclosure"]
        issues = fk.validate_manifest(m)
        self.assertTrue(any(i["severity"] == "error" and "disclosure" in i["msg"]
                            for i in issues))

    def test_bad_url_is_error(self):
        m = manifest()
        m["categories"][0]["entries"][0]["url"] = "ftp://nope"
        issues = fk.validate_manifest(m)
        self.assertTrue(any("url" in i["msg"] and i["severity"] == "error"
                            for i in issues))

    def test_non_boolean_flag_is_error(self):
        m = manifest()
        m["categories"][0]["entries"][0]["sponsored"] = "yes"
        issues = fk.validate_manifest(m)
        self.assertTrue(any("boolean" in i["msg"] for i in issues))

    def test_cli_missing_manifest_exits_2(self):
        res = run_cli("validate", "--manifest", "Z:/none.json")
        self.assertEqual(res.returncode, 2)
        self.assertIn("error:", res.stderr)


class TestEdgeCases(unittest.TestCase):
    def _file(self, content, suffix):
        fd, path = tempfile.mkstemp(suffix=suffix)
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(content)
        self.addCleanup(os.remove, path)
        return path

    def test_empty_events_file(self):
        path = self._file("", ".jsonl")
        res = run_cli("track", "--events", path)
        self.assertEqual(res.returncode, 0)
        self.assertIn("exposure=0", res.stdout)
        self.assertIn("ctr=None", res.stdout)

    def test_corrupt_events_lines_skipped_and_counted(self):
        path = self._file('{"entry":"a","event":"exposure"}\n{broken\n', ".jsonl")
        res = run_cli("track", "--events", path)
        self.assertEqual(res.returncode, 0)
        self.assertIn("1 corrupt line(s)", res.stdout)

    def test_unknown_event_type_ignored(self):
        r = fk.compute_funnel([{"entry": "a", "event": "impression"}])
        self.assertEqual(r["totals"]["invalid_events"], 1)
        self.assertEqual(r["per_entry"], {})

    def test_overlong_entry_name(self):
        events = [{"entry": "x" * 100_000, "event": "click"}]
        r = fk.compute_funnel(events)
        self.assertIn("x" * 100, list(r["per_entry"])[0])

    def test_corrupt_manifest(self):
        path = self._file("{broken", ".json")
        res = run_cli("validate", "--manifest", path)
        self.assertEqual(res.returncode, 2)
        self.assertIn("not valid JSON", res.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=1)
