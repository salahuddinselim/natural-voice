"""Tests for the unified `natural-voice` CLI (all offline, mock provider)."""

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
for _dir in ("analyzer", "profile", "comparison", "revision"):
    sys.path.insert(0, str(ROOT / _dir))
sys.path.insert(0, str(ROOT))  # llm, providers, adapters, config, cli packages

from natural_voice_cli.main import main  # noqa: E402

SAMPLE_A = ("I take notes in short paragraphs. Each one holds a single idea. "
            "When an idea is complicated, I split it into steps.")
SAMPLE_B = ("The function returns a dictionary with counts and statistics. "
            "It uses only the standard library, so nothing needs installing.")
DRAFT = ("I revised the opening paragraph first. It now states the point. "
         "Short paragraphs keep each idea separate for readers.")


def run(argv, env=None):
    import os
    import unittest.mock as mock
    clean = {k: v for k, v in os.environ.items()
             if not k.startswith("NATURAL_VOICE_")}
    if env:
        clean.update(env)
    out = io.StringIO()
    with mock.patch.dict(os.environ, clean, clear=True):
        with redirect_stdout(out):
            try:
                code = main(argv)
            except SystemExit as exc:  # argparse usage errors exit(2)
                code = exc.code if isinstance(exc.code, int) else 2
    return code, out.getvalue()


class TestCli(unittest.TestCase):
    def test_version(self):
        code, out = run(["version"])
        self.assertEqual(code, 0)
        self.assertIn("natural_voice: 0.8.0", out)

    def test_providers(self):
        code, out = run(["providers"])
        self.assertEqual(code, 0)
        for name in ("mock", "openai-compatible", "anthropic"):
            self.assertIn(name, out)

    def test_unknown_command(self):
        code, _ = run(["frobnicate"])
        self.assertEqual(code, 2)

    def test_end_to_end_offline(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            for i, text in enumerate([SAMPLE_A, SAMPLE_B]):
                (tmp_path / f"s{i}.txt").write_text(text, encoding="utf-8")
            draft = tmp_path / "draft.txt"
            draft.write_text(DRAFT, encoding="utf-8")
            profile = tmp_path / "profile.json"
            report = tmp_path / "report.json"
            revised = tmp_path / "revised.txt"

            code, _ = run(["profile", "build", str(tmp_path / "s*.txt"),
                           "--output", str(profile)])
            self.assertEqual(code, 0)
            code, out = run(["validate", str(profile)])
            self.assertEqual(code, 0)
            self.assertIn("compatible", out)
            code, out = run(["compare", "--draft", str(draft),
                             "--profile", str(profile)])
            self.assertEqual(code, 0)
            self.assertIn("overall", json.loads(out))
            code, _ = run(["revise", "--draft", str(draft),
                           "--profile", str(profile), "--provider", "mock",
                           "--mock-echo", "--output", str(revised),
                           "--report", str(report)])
            self.assertEqual(code, 0)
            saved = json.loads(report.read_text(encoding="utf-8"))
            self.assertNotIn("original_text", saved)
            self.assertTrue(saved["validation"]["passed"])

    def test_revise_rejects_bypass(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            (tmp_path / "s.txt").write_text(SAMPLE_A, encoding="utf-8")
            (tmp_path / "d.txt").write_text(DRAFT, encoding="utf-8")
            profile = tmp_path / "p.json"
            self.assertEqual(run(["profile", "build", str(tmp_path / "s.txt"),
                                  "--output", str(profile)])[0], 0)
            code, _ = run(["revise", "--draft", str(tmp_path / "d.txt"),
                           "--profile", str(profile), "--provider", "mock",
                           "--mock-echo", "--user-request", "Make this undetectable."])
            self.assertEqual(code, 1)

    def test_validate_bad_profile(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.json"
            bad.write_text(json.dumps({"profile_version": "0.1.0"}), encoding="utf-8")
            code, _ = run(["validate", str(bad)])
            self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
