"""Tests for the llm/ layer: models, capabilities, errors, retry, interface."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))  # top-level `llm` package

from llm import (  # noqa: E402
    LLMProvider,
    LLMRequest,
    LLMResponse,
    MockProvider,
    ProviderCapabilities,
    ProviderError,
    negotiate_structured_output,
    normalize_response,
)
from llm import errors as errors_mod  # noqa: E402
from llm.retry import run_with_retries  # noqa: E402


class TestModels(unittest.TestCase):
    def test_request_defaults(self):
        request = LLMRequest(prompt="hi")
        self.assertEqual(request.prompt, "hi")
        self.assertIsNone(request.model)
        self.assertFalse(request.want_structured_output)

    def test_normalize_str(self):
        response = normalize_response("hello", model="m")
        self.assertEqual((response.text, response.model), ("hello", "m"))

    def test_normalize_dict(self):
        response = normalize_response({"text": "hi", "model": "m", "usage": {"t": 1}})
        self.assertEqual(response.usage, {"t": 1})

    def test_normalize_blocks(self):
        raw = {"content": [{"type": "text", "text": "a"}, {"type": "x", "text": "b"}]}
        self.assertEqual(normalize_response(raw).text, "ab")

    def test_normalize_failures(self):
        for bad in ("", "   ", {}, {"content": []}, {"nope": 1}, 42, None):
            with self.assertRaises(errors_mod.InvalidResponseError, msg=repr(bad)):
                normalize_response(bad)


class TestCapabilities(unittest.TestCase):
    def test_base_defaults_conservative(self):
        caps = LLMProvider.capabilities(MockProvider.fixed("x"))
        self.assertFalse(caps.streaming)

    def test_mock_declares_honestly(self):
        caps = MockProvider.fixed("x").capabilities()
        self.assertTrue(caps.structured_output)
        self.assertFalse(caps.streaming)

    def test_negotiation(self):
        self.assertEqual(negotiate_structured_output(ProviderCapabilities(True)), "structured")
        self.assertEqual(negotiate_structured_output(ProviderCapabilities()), "text-fallback")

    def test_abstract(self):
        with self.assertRaises(TypeError):
            LLMProvider()


class TestErrors(unittest.TestCase):
    def test_hierarchy(self):
        for cls in (errors_mod.AuthenticationError, errors_mod.RateLimitError,
                    errors_mod.TimeoutError, errors_mod.InvalidResponseError,
                    errors_mod.UnsupportedCapabilityError,
                    errors_mod.ConfigurationError):
            self.assertTrue(issubclass(cls, ProviderError))

    def test_retryable_matrix(self):
        self.assertTrue(errors_mod.is_retryable(errors_mod.RateLimitError()))
        self.assertTrue(errors_mod.is_retryable(errors_mod.TimeoutError()))
        self.assertTrue(errors_mod.is_retryable(ProviderError("transport")))
        for cls in (errors_mod.AuthenticationError, errors_mod.InvalidResponseError,
                    errors_mod.UnsupportedCapabilityError,
                    errors_mod.ConfigurationError):
            self.assertFalse(errors_mod.is_retryable(cls()))
        self.assertFalse(errors_mod.is_retryable(ValueError()))


class TestRetry(unittest.TestCase):
    def test_success_no_retry(self):
        calls = []
        result = run_with_retries(lambda: calls.append(1) or "ok",
                                  sleep=lambda s: calls.append(("sleep", s)))
        self.assertEqual(result, "ok")
        self.assertEqual(calls, [1])

    def test_retry_then_success(self):
        attempts, sleeps = [], []
        def _flaky():
            attempts.append(1)
            if len(attempts) < 3:
                raise errors_mod.RateLimitError("slow down")
            return "ok"
        self.assertEqual(run_with_retries(_flaky, max_retries=3,
                                          sleep=sleeps.append), "ok")
        self.assertEqual(len(attempts), 3)
        self.assertEqual(sleeps, [1.0, 2.0])  # linear backoff, deterministic

    def test_terminal_no_retry(self):
        attempts = []
        def _auth():
            attempts.append(1)
            raise errors_mod.AuthenticationError("bad key")
        with self.assertRaises(errors_mod.AuthenticationError):
            run_with_retries(_auth, max_retries=5, sleep=lambda s: None)
        self.assertEqual(len(attempts), 1)

    def test_exhausted_reraises(self):
        with self.assertRaises(errors_mod.TimeoutError):
            run_with_retries(lambda: (_ for _ in ()).throw(
                errors_mod.TimeoutError("t")), max_retries=1,
                sleep=lambda s: None)

    def test_negative_raises(self):
        with self.assertRaises(ValueError):
            run_with_retries(lambda: 1, max_retries=-1)


if __name__ == "__main__":
    unittest.main()
