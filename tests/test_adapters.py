"""Adapter contract tests (mirrors docs/adapter-contract.md checklist)."""

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))  # `adapters` package

import adapters  # noqa: E402

TRIGGERS = ("natural", "style", "profile", "compar")
BOUNDARIES = ("fabricat",)  # fabrication ban must be stated...
REFUSALS = ("bypass", "undetectable", "Turnitin", "GPTZero")


class TestDiscovery(unittest.TestCase):
    def test_listed(self):
        self.assertEqual(adapters.list_adapters(), ["chatgpt", "claude", "codex", "opencode"])

    def test_skill_paths(self):
        for name in adapters.list_adapters():
            path = adapters.adapter_skill_path(name)
            self.assertTrue(path.is_file())

    def test_unknown_raises(self):
        with self.assertRaises(ValueError):
            adapters.adapter_skill_path("nope")


class TestContract(unittest.TestCase):
    def test_frontmatter(self):
        for name in adapters.list_adapters():
            text = adapters.adapter_skill_path(name).read_text(encoding="utf-8")
            match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
            self.assertIsNotNone(match, name)
            frontmatter = match.group(1)
            self.assertIn("name: natural-voice", frontmatter)
            self.assertIn("description:", frontmatter)

    def test_triggers_and_core_references(self):
        for name in adapters.list_adapters():
            text = adapters.adapter_skill_path(name).read_text(encoding="utf-8").lower()
            for trigger in TRIGGERS:
                self.assertIn(trigger, text, f"{name}: {trigger}")
            # Points at shared core/CLI, never a forked methodology.
            self.assertTrue("core/" in text or "natural-voice" in text, name)

    def test_boundaries_and_privacy(self):
        for name in adapters.list_adapters():
            text = adapters.adapter_skill_path(name).read_text(encoding="utf-8")
            lowered = text.lower()
            for word in BOUNDARIES:
                self.assertIn(word, lowered, f"{name}: {word}")
            self.assertTrue(any(word in text for word in REFUSALS), name)
            self.assertTrue("never commit" in lowered or "do not commit" in lowered,
                              f"{name}: commit prohibition")

    def test_version_and_thinness(self):
        for name in adapters.list_adapters():
            text = adapters.adapter_skill_path(name).read_text(encoding="utf-8")
            self.assertIn("0.7", text, name)  # current ADAPTER_VERSION
            self.assertLess(len(text.splitlines()), 400, f"{name} too thick")


if __name__ == "__main__":
    unittest.main()
