"""Tests for the Natural Voice profile builder (stdlib unittest).

Run from the repository root:  python -m unittest discover -s tests -v
"""

import json
import math
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "analyzer"))
sys.path.insert(0, str(ROOT / "profile"))

from natural_voice_analyzer import analyze_text  # noqa: E402
from natural_voice_profile import (  # noqa: E402
    build_profile,
    build_profile_from_files,
    is_valid,
    load_profile,
    save_profile,
    validate_profile,
)
from natural_voice_profile.aggregation import (  # noqa: E402
    aggregate_numeric,
    detect_outliers,
    sample_weight,
)
from natural_voice_profile.confidence import overall_confidence  # noqa: E402

SAMPLE_A = ("I take notes in short paragraphs. Each one holds a single idea. "
            "When an idea is complicated, I split it into steps. That order works well.")
SAMPLE_B = ("The function returns a dictionary with counts and statistics. "
            "It uses only the standard library, so nothing needs installing. "
            "Missing values are null rather than invented values.")
SAMPLE_C = ("This study examines sentence length across paragraphs. The method stays "
            "identical for every corpus in the collection. Results indicate a clear "
            "preference for medium sentences in explanatory writing.")


def long_sample(avg_target_words=20, sentences=30):
    filler = ("The committee reviewed the quarterly report carefully before the meeting "
              "continued with further discussion and additional review").split()
    words = (filler * ((avg_target_words // len(filler)) + 1))[:avg_target_words]
    sentence = " ".join(words) + "."
    return " ".join([sentence] * sentences)


class TestSingleAndMultiple(unittest.TestCase):
    def test_single_sample_builds(self):
        profile = build_profile([SAMPLE_A])
        self.assertEqual(profile["metadata"]["sample_count"], 1)
        self.assertEqual(profile["confidence"]["overall"], "low")  # 1 sample -> low
        self.assertTrue(is_valid(profile))

    def test_multiple_samples_aggregate(self):
        profile = build_profile([SAMPLE_A, SAMPLE_B, SAMPLE_C])
        self.assertEqual(profile["metadata"]["sample_count"], 3)
        agg = profile["sentence_structure"]["average_length"]
        per = [analyze_text(s)["sentence_structure"]["average_length"]
               for s in (SAMPLE_A, SAMPLE_B, SAMPLE_C)]
        self.assertGreaterEqual(agg["mean"], min(per))
        self.assertLessEqual(agg["mean"], max(per))
        self.assertEqual(agg["n"], 3)
        self.assertIsNotNone(agg["typical_range"])
        self.assertTrue(is_valid(profile))


class TestWeighting(unittest.TestCase):
    def test_weight_function(self):
        self.assertAlmostEqual(sample_weight(100), 10.0)
        self.assertAlmostEqual(sample_weight(1), 1.0)
        self.assertAlmostEqual(sample_weight(0), 1.0)

    def test_long_sample_does_not_fully_dominate(self):
        short = "Short words here. Brief notes follow. Keep it tight."
        long = long_sample(avg_target_words=30, sentences=40)
        profile = build_profile([short, long])
        mean = profile["sentence_structure"]["average_length"]["mean"]
        a_short = analyze_text(short)["sentence_structure"]["average_length"]
        a_long = analyze_text(long)["sentence_structure"]["average_length"]
        w_short = analyze_text(short)["basic"]["words"]
        w_long = analyze_text(long)["basic"]["words"]
        pooled = (a_short * w_short + a_long * w_long) / (w_short + w_long)
        self.assertGreater(mean, a_short)   # long pulls up...
        self.assertLess(mean, a_long)       # ...but within range...
        self.assertLess(mean, pooled)       # ...and damped vs raw word-weighting


class TestEmptyAndMissing(unittest.TestCase):
    def test_empty_list_raises(self):
        with self.assertRaises(ValueError):
            build_profile([])

    def test_all_empty_raises(self):
        with self.assertRaises(ValueError):
            build_profile(["", "   ", "\n\t"])

    def test_empty_samples_skipped(self):
        profile = build_profile(["", SAMPLE_A, "  "])
        self.assertEqual(profile["metadata"]["sample_count"], 1)
        self.assertEqual(profile["metadata"]["skipped_samples"], 2)

    def test_non_string_raises(self):
        with self.assertRaises(TypeError):
            build_profile([SAMPLE_A, 42])

    def test_aggregate_skips_missing(self):
        result = aggregate_numeric([None, 1.0, 3.0], [1.0, 1.0, 1.0])
        self.assertEqual(result["n"], 2)
        self.assertAlmostEqual(result["mean"], 2.0)
        empty = aggregate_numeric([None, None])
        self.assertEqual(empty["n"], 0)
        self.assertIsNone(empty["mean"])

    def test_short_sample_low_confidence(self):
        self.assertEqual(build_profile(["Hello world."])["confidence"]["overall"], "low")


class TestOutliers(unittest.TestCase):
    def test_detector_unit(self):
        notes = detect_outliers([12, 14, 11, 13, 15, 60], "average_sentence_length")
        self.assertTrue(any(n["sample_index"] == 5 for n in notes))

    def test_no_flag_below_minimum(self):
        self.assertEqual(detect_outliers([10, 10, 100], "x"), [])

    def test_extreme_sample_preserved(self):
        normals = [
            "I write short notes each day. They stay brief and clear.",
            "The method works for small tasks. Results arrive quickly.",
            "Short paragraphs hold single ideas. I move on after each one.",
            "Plain words carry the meaning. Extra decoration gets cut away.",
        ]
        extreme = long_sample(avg_target_words=40, sentences=25)
        profile = build_profile(normals + [extreme])
        self.assertTrue(is_valid(profile))
        self.assertEqual(profile["metadata"]["sample_count"], 5)
        self.assertIsInstance(profile["outlier_notes"], list)
        # Variation preserved, not collapsed: min/max span the samples.
        agg = profile["sentence_structure"]["average_length"]
        self.assertLess(agg["min"], agg["max"])


class TestConfidence(unittest.TestCase):
    def test_boundaries(self):
        self.assertEqual(overall_confidence(1, 50), "low")
        self.assertEqual(overall_confidence(3, 100), "low")
        self.assertEqual(overall_confidence(3, 800), "medium")
        self.assertEqual(overall_confidence(4, 2000), "high")
        self.assertEqual(overall_confidence(2, 2000), "medium")  # needs 4+ samples


class TestSerializationValidation(unittest.TestCase):
    def test_round_trip(self):
        profile = build_profile([SAMPLE_A, SAMPLE_B, SAMPLE_C])
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "profile.json"
            save_profile(profile, path)
            loaded = load_profile(path)
        self.assertEqual(loaded, profile)

    def test_save_invalid_raises(self):
        with self.assertRaises(ValueError):
            save_profile({"profile_version": "0.1.0"}, "x.json")

    def test_load_bad_json_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text("{not json", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_profile(path)

    def test_load_invalid_profile_raises(self):
        profile = build_profile([SAMPLE_A])
        profile["confidence"]["overall"] = "certain"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "p.json"
            path.write_text(json.dumps(profile), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_profile(path)

    def test_validation_cases(self):
        good = build_profile([SAMPLE_A, SAMPLE_B])
        self.assertEqual(validate_profile(good), [])
        cases = [
            ({}, "missing keys"),
            ({**good, "profile_version": "9.9.9"}, "version"),
            ({**good, "confidence": {**good["confidence"], "overall": "high!"}},
             "confidence level"),
            ({**good, "metadata": {**good["metadata"], "context": "blog"}},
             "context"),
        ]
        for mutated, _label in cases:
            self.assertTrue(validate_profile(mutated), _label)
        nan_profile = build_profile([SAMPLE_A])
        nan_profile["vocabulary"]["diversity"]["mean"] = math.nan
        self.assertTrue(any("non-finite" in e for e in validate_profile(nan_profile)))
        raw_profile = build_profile([SAMPLE_A])
        raw_profile["metadata"]["full_text"] = SAMPLE_A
        self.assertTrue(any("raw-sample" in e for e in validate_profile(raw_profile)))


class TestPrivacyDeterminismFiles(unittest.TestCase):
    def test_no_raw_text_in_profile(self):
        samples = [SAMPLE_A, SAMPLE_B, SAMPLE_C]
        blob = json.dumps(build_profile(samples), ensure_ascii=False)
        for sample in samples:
            self.assertNotIn(sample, blob)
            self.assertNotIn(sample[:80], blob)
        for forbidden in ("full_text", "raw_text", "original_sample", "raw_document"):
            self.assertNotIn(forbidden, blob)

    def test_deterministic(self):
        samples = [SAMPLE_A, SAMPLE_B, SAMPLE_C]
        self.assertEqual(build_profile(samples), build_profile(samples))

    def test_from_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = []
            for i, text in enumerate([SAMPLE_A, SAMPLE_B]):
                path = Path(tmp) / f"s{i}.txt"
                path.write_text(text, encoding="utf-8")
                paths.append(str(path))
            profile = build_profile_from_files(paths, context="technical")
        self.assertEqual(profile["metadata"]["context"], "technical")
        self.assertTrue(is_valid(profile))

    def test_from_files_missing_raises(self):
        with self.assertRaises(ValueError):
            build_profile_from_files(["/nonexistent_dir_xyz/s.txt"])

    def test_bad_context_raises(self):
        with self.assertRaises(ValueError):
            build_profile([SAMPLE_A], context="blog")

    def test_no_scores_in_profile(self):
        blob = json.dumps(build_profile([SAMPLE_A, SAMPLE_B])).lower()
        for forbidden in ("ai_probability", "human_probability", "detector",
                          "human_score", "authorship"):
            self.assertNotIn(forbidden, blob)


if __name__ == "__main__":
    unittest.main()
