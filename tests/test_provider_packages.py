"""Tests for providers/: registry, mock, openai-compatible, anthropic (stubbed transport)."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))  # `llm`, `providers`

import providers  # noqa: E402
from llm import errors as errors_mod  # noqa: E402
from llm.interface import LLMProvider  # noqa: E402
from providers.anthropic.provider import AnthropicProvider  # noqa: E402
from providers.openai_compatible.provider import OpenAICompatibleProvider  # noqa: E402


def openai_ok(url, payload, headers, timeout):
    openai_ok.calls.append((url, payload, headers, timeout))
    return {"choices": [{"message": {"content": "stubbed revision"}}]}


def anthropic_ok(url, payload, headers, timeout):
    anthropic_ok.calls.append((url, payload, headers, timeout))
    return {"content": [{"type": "text", "text": "stubbed revision"}]}


class TestRegistry(unittest.TestCase):
    def test_builtins_listed(self):
        self.assertEqual(providers.list_providers(),
                         ["anthropic", "mock", "openai-compatible"])

    def test_unknown_raises(self):
        with self.assertRaises(ValueError):
            providers.get_provider("nope")

    def test_register_custom(self):
        providers.register_provider("custom-test", lambda **kw: "x")
        try:
            self.assertEqual(providers.get_provider("custom-test"), "x")
            self.assertIn("custom-test", providers.list_providers())
        finally:
            del providers._FACTORIES["custom-test"]

    def test_mock_through_registry(self):
        provider = providers.get_provider("mock", handler="hi")
        self.assertIsInstance(provider, LLMProvider)
        self.assertEqual(provider.generate("anything"), "hi")

    def test_mock_rejects_options(self):
        with self.assertRaises(ValueError):
            providers.get_provider("mock", model="x")


class TestOpenAICompatible(unittest.TestCase):
    def setUp(self):
        openai_ok.calls = []

    def test_generate_shape(self):
        provider = OpenAICompatibleProvider(
            model="test-model", api_key="k", transport=openai_ok,
            temperature=0.2, max_tokens=50)
        self.assertEqual(provider.generate("Say hi", system_prompt="Be brief"),
                         "stubbed revision")
        url, payload, headers, timeout = openai_ok.calls[0]
        self.assertTrue(url.endswith("/chat/completions"))
        self.assertEqual(payload["model"], "test-model")
        self.assertEqual(payload["messages"][0], {"role": "system", "content": "Be brief"})
        self.assertEqual(payload["messages"][1], {"role": "user", "content": "Say hi"})
        self.assertEqual(payload["temperature"], 0.2)
        self.assertEqual(payload["max_tokens"], 50)
        self.assertIn("Bearer k", headers["Authorization"])

    def test_missing_key(self):
        import os
        env = {k: v for k, v in os.environ.items() if k != "OPENAI_API_KEY"}
        import unittest.mock as mock
        with mock.patch.dict(os.environ, env, clear=True):
            with self.assertRaises(errors_mod.ConfigurationError):
                OpenAICompatibleProvider(transport=openai_ok)

    def test_rate_limit_retried_then_succeeds(self):
        attempts = []
        def _flaky(url, payload, headers, timeout):
            attempts.append(1)
            if len(attempts) == 1:
                raise errors_mod.RateLimitError("slow")
            return {"choices": [{"message": {"content": "ok"}}]}
        provider = OpenAICompatibleProvider(api_key="k", transport=_flaky)
        import llm.retry as retry_mod
        original = retry_mod.time.sleep
        retry_mod.time.sleep = lambda s: None
        try:
            self.assertEqual(provider.generate("hi"), "ok")
        finally:
            retry_mod.time.sleep = original
        self.assertEqual(len(attempts), 2)

    def test_auth_not_retried(self):
        attempts = []
        def _auth(url, payload, headers, timeout):
            attempts.append(1)
            raise errors_mod.AuthenticationError("bad")
        provider = OpenAICompatibleProvider(api_key="k", transport=_auth)
        with self.assertRaises(errors_mod.AuthenticationError):
            provider.generate("hi")
        self.assertEqual(len(attempts), 1)

    def test_malformed_payload(self):
        provider = OpenAICompatibleProvider(
            api_key="k", transport=lambda *a: {"choices": []})
        with self.assertRaises(errors_mod.InvalidResponseError):
            provider.generate("hi")

    def test_capabilities_honest(self):
        caps = OpenAICompatibleProvider(api_key="k", transport=openai_ok).capabilities()
        self.assertTrue(caps.system_messages)
        self.assertFalse(caps.streaming)
        self.assertFalse(caps.structured_output)


class TestAnthropic(unittest.TestCase):
    def setUp(self):
        anthropic_ok.calls = []

    def test_generate_shape(self):
        provider = AnthropicProvider(model="m", api_key="k", transport=anthropic_ok)
        self.assertEqual(provider.generate("Say hi", system_prompt="Be brief"),
                         "stubbed revision")
        url, payload, headers, _ = anthropic_ok.calls[0]
        self.assertTrue(url.endswith("/v1/messages"))
        self.assertEqual(payload["model"], "m")
        self.assertEqual(payload["system"], "Be brief")
        self.assertEqual(payload["messages"], [{"role": "user", "content": "Say hi"}])
        self.assertEqual(payload["max_tokens"], 1024)
        self.assertEqual(headers["x-api-key"], "k")
        self.assertIn("anthropic-version", headers)

    def test_missing_key(self):
        import os
        import unittest.mock as mock
        env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
        with mock.patch.dict(os.environ, env, clear=True):
            with self.assertRaises(errors_mod.ConfigurationError):
                AnthropicProvider(transport=anthropic_ok)

    def test_no_sdk_imports(self):
        for path in [ROOT / "providers" / "anthropic" / "provider.py",
                     ROOT / "providers" / "openai_compatible" / "provider.py",
                     ROOT / "providers" / "_http.py"]:
            source = path.read_text(encoding="utf-8")
            for forbidden in ("import openai", "import anthropic", "import requests",
                              "import httpx", "import aiohttp"):
                self.assertNotIn(forbidden, source, f"{path.name}: {forbidden}")


class TestCrossProviderConsistency(unittest.TestCase):
    def test_equivalent_semantic_input(self):
        """Same prompt text reaches both providers (no per-model methodology fork)."""
        openai_ok.calls, anthropic_ok.calls = [], []
        prompt = "INSTRUCTIONS: revise\nAUTHOR PROFILE: x\nDRAFT: y"
        openai = OpenAICompatibleProvider(api_key="k", transport=openai_ok)
        anthropic = AnthropicProvider(api_key="k", transport=anthropic_ok)
        self.assertEqual(openai.generate(prompt), anthropic.generate(prompt))
        openai_user_text = openai_ok.calls[0][1]["messages"][-1]["content"]
        anthropic_user_text = anthropic_ok.calls[0][1]["messages"][0]["content"]
        self.assertEqual(openai_user_text, anthropic_user_text)
        self.assertEqual(openai_user_text, prompt)


if __name__ == "__main__":
    unittest.main()
