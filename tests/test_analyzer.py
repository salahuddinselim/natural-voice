"""Unit tests for the Natural Voice analyzer (stdlib unittest, no dependencies).

Run from the repository root:  python -m unittest discover -s tests -v
Tests verify actual calculations, not just that functions execute.
"""

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "analyzer"))

from natural_voice_analyzer import analyze_text, to_json  # noqa: E402
from natural_voice_analyzer import text_utils  # noqa: E402


class TestEmptyAndWhitespace(unittest.TestCase):
    def test_empty_string(self):
        result = analyze_text("")
        self.assertEqual(result["basic"]["words"], 0)
        self.assertEqual(result["basic"]["sentences"], 0)
        self.assertEqual(result["basic"]["paragraphs"], 0)
        self.assertIsNone(result["basic"]["average_sentence_length"])
        self.assertIsNone(result["vocabulary"]["type_token_ratio"])
        self.assertIsNone(result["punctuation"]["punctuation_density"])
        self.assertIsNone(result["readability"]["flesch_reading_ease"])
        self.assertEqual(result["ngrams"]["bigrams"], [])
        self.assertEqual(result["ngrams"]["trigrams"], [])

    def test_whitespace_only(self):
        result = analyze_text("   \n\t\n  ")
        self.assertEqual(result["basic"]["words"], 0)
        self.assertEqual(result["basic"]["sentences"], 0)

    def test_invalid_type_raises(self):
        with self.assertRaises(TypeError):
            analyze_text(None)
        with self.assertRaises(TypeError):
            analyze_text(123)


class TestBasicCounts(unittest.TestCase):
    def test_two_word_sentence(self):
        result = analyze_text("Hello world.")
        basic = result["basic"]
        self.assertEqual(basic["words"], 2)
        self.assertEqual(basic["sentences"], 1)
        self.assertEqual(basic["paragraphs"], 1)
        self.assertEqual(basic["characters"], len("Hello world."))
        self.assertEqual(basic["characters_no_spaces"], len("Helloworld."))
        self.assertAlmostEqual(basic["average_word_length"], 5.0)
        self.assertAlmostEqual(basic["average_sentence_length"], 2.0)
        self.assertEqual(basic["min_sentence_length"], 2)
        self.assertEqual(basic["max_sentence_length"], 2)

    def test_multiple_paragraphs(self):
        text = "First paragraph here.\n\nSecond paragraph here too."
        result = analyze_text(text)
        self.assertEqual(result["basic"]["paragraphs"], 2)
        self.assertEqual(result["basic"]["sentences"], 2)
        para = result["paragraph_structure"]
        self.assertEqual(para["count"], 2)
        self.assertAlmostEqual(para["average_sentences_per_paragraph"], 1.0)
        # "First paragraph here." = 3 words; "Second paragraph here too." = 4 words
        self.assertAlmostEqual(para["average_words_per_paragraph"], 3.5)


class TestSentenceStructure(unittest.TestCase):
    def test_buckets_and_variation(self):
        short = "Short one."
        medium = "This is a medium length sentence with some more words in it."
        long_text = (
            "This is a deliberately very long sentence that keeps going with many "
            "additional words well beyond the medium threshold for testing purposes."
        )
        result = analyze_text(f"{short} {medium} {long_text}")
        struct = result["sentence_structure"]
        self.assertEqual(struct["count"], 3)
        # medium sentence: This(1) is(2) a(3) medium(4) length(5) sentence(6) with(7)
        # some(8) more(9) words(10) in(11) it(12) -> 12 words -> medium bucket
        lengths = sorted(
            [len(text_utils.tokenize_words(s)) for s in text_utils.split_sentences(
                f"{short} {medium} {long_text}")]
        )
        self.assertEqual(struct["min_length"], lengths[0])
        self.assertEqual(struct["max_length"], lengths[-1])
        self.assertAlmostEqual(struct["short_ratio"] + struct["medium_ratio"]
                               + struct["long_ratio"], 1.0)
        self.assertGreater(struct["standard_deviation"], 0)
        self.assertGreater(struct["coefficient_of_variation"], 0)

    def test_abbreviation_guard(self):
        sentences = text_utils.split_sentences("Dr. Smith arrived. He sat down.")
        self.assertEqual(len(sentences), 2)


class TestVocabulary(unittest.TestCase):
    def test_diversity_and_repetition(self):
        result = analyze_text("Cat dog cat bird cat dog.")
        vocab = result["vocabulary"]
        self.assertEqual(vocab["total_words"], 6)
        self.assertEqual(vocab["unique_words"], 3)
        self.assertAlmostEqual(vocab["type_token_ratio"], 3 / 6)
        # repeated = count > 2 -> only "cat" (3x)
        self.assertEqual(vocab["repeated_words"], [["cat", 3]])
        self.assertEqual(vocab["top_words"][0], ["cat", 3])

    def test_ttr_length_note(self):
        # Same vocabulary, longer text -> lower TTR (documents length dependence).
        short = analyze_text("a b c d")
        long = analyze_text("a b c d " * 25)
        self.assertGreater(short["vocabulary"]["type_token_ratio"],
                           long["vocabulary"]["type_token_ratio"])
        self.assertIsNotNone(long["vocabulary"]["guiraud_r"])

    def test_normalization_keeps_contractions(self):
        tokens = text_utils.tokenize_words("Don't stop.")
        self.assertIn("Don't", tokens)


class TestPunctuation(unittest.TestCase):
    def test_counts_and_density(self):
        text = "Hello, world! How are you?"
        result = analyze_text(text)["punctuation"]
        self.assertEqual(result["counts"][","], 1)
        self.assertEqual(result["counts"]["!"], 1)
        self.assertEqual(result["counts"]["?"], 1)
        self.assertEqual(result["counts"][";"], 0)
        # 5 words ("Hello world How are you"), 3 marks -> density 0.6
        self.assertAlmostEqual(result["punctuation_density"], 3 / 5)
        self.assertAlmostEqual(result["per_100_words"][","], 1 / 5 * 100)


class TestReadability(unittest.TestCase):
    def test_normal_text_has_values(self):
        text = ("The analyzer reads plain text. It reports measurements. "
                "Longer sentences develop ideas with more room to conclude.")
        readability = analyze_text(text)["readability"]
        for key in ("flesch_reading_ease", "flesch_kincaid_grade",
                    "gunning_fog", "coleman_liau", "automated_readability_index"):
            self.assertIsInstance(readability[key], float)


class TestNgrams(unittest.TestCase):
    def test_bigrams_trigrams(self):
        text = "the analyzer reads text and the analyzer writes text"
        ngrams = analyze_text(text, top_k=5)["ngrams"]
        bigram_map = dict(ngrams["bigrams"])
        self.assertEqual(bigram_map.get("the analyzer"), 2)
        self.assertLessEqual(len(ngrams["bigrams"]), 5)

    def test_top_k_respected(self):
        text = "a b c d e f g h"
        ngrams = analyze_text(text, top_k=3)["ngrams"]
        self.assertLessEqual(len(ngrams["bigrams"]), 3)

    def test_character_ngrams_opt_in(self):
        result_default = analyze_text("hello world")
        self.assertNotIn("character_ngrams", result_default["ngrams"])
        result_opt = analyze_text("hello world", include_character_ngrams=True)
        self.assertIn("character_ngrams", result_opt["ngrams"])
        self.assertEqual(result_opt["ngrams"]["character_ngrams"]["n"], 3)


class TestLinguistic(unittest.TestCase):
    def test_pronouns_and_transitions(self):
        text = "I think we should stay because it matters. However, you decide."
        ling = analyze_text(text)["linguistic"]
        # I, we, it, you -> 4 pronouns
        self.assertEqual(ling["pronoun_count"], 4)
        # Output floats are rounded to 4 decimals; compare at that precision.
        self.assertAlmostEqual(ling["pronoun_ratio"], 4 / ling["total_words"], places=4)
        self.assertGreaterEqual(ling["transition_count"], 2)  # because, however

    def test_open_class_pos_not_fabricated(self):
        ling = analyze_text("Dogs run quickly.")["linguistic"]
        for key in ("nouns", "verbs", "adjectives", "adverbs", "named_entities"):
            self.assertIsNone(ling[key])


class TestUnicodeAndLongText(unittest.TestCase):
    def test_unicode(self):
        text = "Café naïve — über cool! Grüße aus München?"
        result = analyze_text(text)
        self.assertEqual(result["basic"]["words"], 7)
        self.assertEqual(result["basic"]["sentences"], 2)
        json.dumps(result, ensure_ascii=False)  # must serialize

    def test_long_text(self):
        text = ("Word " * 500 + ". ") * 20
        result = analyze_text(text.strip())
        self.assertEqual(result["basic"]["sentences"], 20)
        self.assertGreater(result["basic"]["words"], 9000)

    def test_json_round_trip(self):
        result = analyze_text("Hello world. Second sentence here.")
        serialized = to_json(result)
        parsed = json.loads(serialized)
        self.assertEqual(parsed["basic"]["words"], result["basic"]["words"])
        # No NaN/Infinity allowed in JSON output.
        self.assertNotIn("NaN", serialized)


class TestNoScores(unittest.TestCase):
    def test_no_authorship_outputs(self):
        result = analyze_text("This is a normal paragraph with several words in it.")
        blob = json.dumps(result).lower()
        for forbidden in ("ai_probability", "human_probability", "detector",
                          "human_score", "ai_score", "authorship"):
            self.assertNotIn(forbidden, blob)


if __name__ == "__main__":
    unittest.main()
