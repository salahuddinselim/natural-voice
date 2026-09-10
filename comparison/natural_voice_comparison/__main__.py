"""Minimal CLI: compare a draft file against a saved voice profile.

Example:
    python -m natural_voice_comparison --draft draft.txt --profile profile.json
    python -m natural_voice_comparison --draft draft.txt --profile profile.json \\
        --output report.json --pretty

Only the derived report leaves this process; draft text is never logged.
"""

from __future__ import annotations

import argparse
import json
import sys

from natural_voice_analyzer.output import to_json

from .comparator import compare_draft_file


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare a draft against an Author Voice Profile.")
    parser.add_argument("--draft", required=True, help="Path to a UTF-8 draft file.")
    parser.add_argument("--profile", required=True,
                        help="Path to a saved voice profile JSON file.")
    parser.add_argument("--output", default=None,
                        help="Write report JSON here instead of stdout.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON.")
    parser.add_argument("--draft-context", default=None,
                        help="Draft context label (e.g. casual) for mismatch warnings.")
    parser.add_argument("--weights", default=None,
                        help="JSON object of dimension weights, e.g. '{\"ngrams\": 0.5}'.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    weights = None
    if args.weights:
        try:
            weights = json.loads(args.weights)
        except json.JSONDecodeError as exc:
            print(f"error: --weights is not valid JSON: {exc}", file=sys.stderr)
            return 2
    try:
        report = compare_draft_file(args.draft, args.profile,
                                    weights=weights,
                                    draft_context=args.draft_context)
    except (ValueError, TypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    text = to_json(report, pretty=args.pretty)
    if args.output:
        from pathlib import Path
        try:
            Path(args.output).write_text(text + "\n", encoding="utf-8")
        except OSError as exc:
            print(f"error: cannot write {args.output}: {exc}", file=sys.stderr)
            return 1
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
