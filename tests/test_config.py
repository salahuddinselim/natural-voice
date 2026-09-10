"""Tests for natural_voice_config: loader precedence, versions, logging."""

import json
import logging
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from natural_voice_config import (  # noqa: E402
    check_profile_compatibility,
    get_logger,
    load_config,
    setup_logging,
)
from natural_voice_config import versions as versions_mod  # noqa: E402


class TestLoader(unittest.TestCase):
    def test_defaults(self):
        config = load_config(env={})
        self.assertEqual(config.provider.provider, "mock")
        self.assertIsNone(config.provider.model)
        self.assertEqual(config.mode, "conservative")
        self.assertFalse(config.verbose)

    def test_env_override(self):
        config = load_config(env={"NATURAL_VOICE_PROVIDER": "anthropic",
                                  "NATURAL_VOICE_MODEL": "m",
                                  "NATURAL_VOICE_TEMPERATURE": "0.5",
                                  "NATURAL_VOICE_MAX_TOKENS": "100",
                                  "NATURAL_VOICE_VERBOSE": "true"})
        self.assertEqual(config.provider.provider, "anthropic")
        self.assertEqual(config.provider.model, "m")
        self.assertAlmostEqual(config.provider.temperature, 0.5)
        self.assertEqual(config.provider.max_tokens, 100)
        self.assertTrue(config.verbose)

    def test_invalid_env_value(self):
        with self.assertRaises(ValueError):
            load_config(env={"NATURAL_VOICE_TEMPERATURE": "hot"})

    def test_file_and_precedence(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json"
            path.write_text(json.dumps(
                {"provider": {"provider": "openai-compatible", "model": "file-model"},
                 "mode": "balanced"}), encoding="utf-8")
            # file alone
            config = load_config(env={}, file_path=str(path))
            self.assertEqual(config.provider.model, "file-model")
            self.assertEqual(config.mode, "balanced")
            # env beats file
            config = load_config(env={"NATURAL_VOICE_MODEL": "env-model"},
                                 file_path=str(path))
            self.assertEqual(config.provider.model, "env-model")
            # CLI beats env
            config = load_config(cli_args={"model": "cli-model"},
                                 env={"NATURAL_VOICE_MODEL": "env-model"},
                                 file_path=str(path))
            self.assertEqual(config.provider.model, "cli-model")

    def test_unknown_keys_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text(json.dumps({"provider_name": "x"}), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_config(env={}, file_path=str(path))

    def test_secret_file_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "evil.json"
            path.write_text(json.dumps({"provider": {"api_key": "sk-live"}}),
                            encoding="utf-8")
            with self.assertRaises(ValueError):
                load_config(env={}, file_path=str(path))

    def test_missing_file(self):
        with self.assertRaises(ValueError):
            load_config(env={}, file_path="/nonexistent/nv.json")


class TestVersions(unittest.TestCase):
    def test_mirrors_package_constants(self):
        sys.path.insert(0, str(ROOT / "analyzer"))
        sys.path.insert(0, str(ROOT / "profile"))
        sys.path.insert(0, str(ROOT / "comparison"))
        sys.path.insert(0, str(ROOT / "revision"))
        import natural_voice_analyzer
        import natural_voice_comparison
        import natural_voice_profile
        import natural_voice_revision
        self.assertEqual(versions_mod.ANALYZER_VERSION,
                         natural_voice_analyzer.ANALYZER_VERSION)
        self.assertEqual(versions_mod.PROFILE_VERSION,
                         natural_voice_profile.PROFILE_VERSION)
        self.assertEqual(versions_mod.COMPARISON_VERSION,
                         natural_voice_comparison.COMPARISON_VERSION)
        self.assertEqual(versions_mod.REVISION_VERSION,
                         natural_voice_revision.REVISION_VERSION)

    def test_compatibility(self):
        status, _ = check_profile_compatibility({"profile_version": "0.1.0",
                                                 "metadata": {}})
        self.assertEqual(status, "compatible")
        status, _ = check_profile_compatibility({"metadata": {}})
        self.assertEqual(status, "unsupported")
        status, notes = check_profile_compatibility({"profile_version": "9.9"})
        self.assertEqual(status, "unsupported")
        self.assertTrue(notes)
        self.assertEqual(check_profile_compatibility("nope")[0], "unsupported")


class TestLogging(unittest.TestCase):
    def test_no_content_in_logs(self):
        logger = get_logger("test")
        records = []

        class _Sink(logging.Handler):
            def emit(self, record):
                records.append(record.getMessage())

        setup_logging(verbose=True)
        logging.getLogger("natural_voice").addHandler(_Sink())
        try:
            sys.path.insert(0, str(ROOT / "profile"))
            from natural_voice_profile import build_profile
            secret = "The zebra committee quantifies juxtaposed phenomena."
            build_profile([secret + " Extra words here to analyze."])
        finally:
            logging.getLogger("natural_voice").handlers = [
                h for h in logging.getLogger("natural_voice").handlers
                if not isinstance(h, _Sink)]
        blob = "\n".join(records)
        self.assertNotIn("zebra committee", blob)


if __name__ == "__main__":
    unittest.main()
