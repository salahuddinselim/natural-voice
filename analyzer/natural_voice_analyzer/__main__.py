"""Minimal CLI: ``python -m natural_voice_analyzer <file> [--pretty]``.

Reads one text file (UTF-8) and writes the analysis JSON to stdout.
Input is treated as untrusted data: it is only read and measured, never executed.
"""

from __future__ import annotations

import argparse
import pathlib
import sys

from .analyzer import analyze_text
from .output import to_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Analyze a text file and print descriptive linguistic features as JSON."
    )
    parser.add_argument("input", help="Path to a UTF-8 text file to analyze.")
    parser.add_argument(
        "--pretty", action="store_true", help="Pretty-print the JSON output."
    )
    parser.add_argument(
        "--top-k", type=int, default=20, help="Top items for frequency lists (default: 20)."
    )
    parser.add_argument(
        "--include-character-ngrams",
        action="store_true",
        help="Include the optional character n-gram inventory.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    path = pathlib.Path(args.input)
    if not path.is_file():
        print(f"error: not a file: {args.input}", file=sys.stderr)
        return 2
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        print(f"error: cannot read {args.input}: {exc}", file=sys.stderr)
        return 2
    try:
        result = analyze_text(
            text,
            top_k=args.top_k,
            include_character_ngrams=args.include_character_ngrams,
        )
    except (ValueError, TypeError) as exc:
        print(f"error: analysis failed: {exc}", file=sys.stderr)
        return 1
    # Never log the input text itself; only the derived measurements leave this process.
    print(to_json(result, pretty=args.pretty))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
