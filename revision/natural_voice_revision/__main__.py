"""Minimal CLI: revise a draft with the voice profile + comparison report.

Examples:
    python -m natural_voice_revision --draft draft.txt --profile profile.json --mock-echo
    python -m natural_voice_revision --draft draft.txt --profile profile.json \\
        --mock-file revised.txt --mode balanced --output revised.txt --report report.json

Provider selection: --mock-echo / --mock-text / --mock-file run offline with no
credentials. Real providers are injected in Python (see README); this CLI takes
no API keys. Saved reports strip the original text (privacy); --output holds the
revised text only. Files are written only when validation passes.
"""

from __future__ import annotations

import argparse
import difflib
import json
import sys
from pathlib import Path

from llm.mock import MockProvider

from .engine import MODES, revise
from .result import strip_original


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Revise a draft for clarity and voice consistency.")
    parser.add_argument("--draft", required=True, help="Path to a UTF-8 draft file.")
    parser.add_argument("--profile", required=True,
                        help="Path to a saved voice profile JSON file.")
    parser.add_argument("--comparison", default=None,
                        help="Optional saved Phase 6 report (recomputed if omitted).")
    parser.add_argument("--mode", default="conservative", choices=MODES)
    parser.add_argument("--user-request", default="",
                        help="Revision instruction (detector-evasion intent is refused).")
    parser.add_argument("--max-attempts", type=int, default=1)
    parser.add_argument("--output", default=None,
                        help="Write the revised text here (only when validation passes).")
    parser.add_argument("--report", default=None,
                        help="Write the result report JSON here (original text stripped).")
    parser.add_argument("--show-diff", action="store_true",
                        help="Print a unified diff of original vs revised to stdout.")
    mock = parser.add_mutually_exclusive_group(required=True)
    mock.add_argument("--mock-echo", action="store_true",
                      help="Offline mock: return the draft unchanged.")
    mock.add_argument("--mock-text", default=None,
                      help="Offline mock: use this literal text as the revision.")
    mock.add_argument("--mock-file", default=None,
                      help="Offline mock: read the revision from this file.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        draft = Path(args.draft).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        print(f"error: cannot read draft: {exc}", file=sys.stderr)
        return 1
    try:
        profile = json.loads(Path(args.profile).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        print(f"error: cannot load profile: {exc}", file=sys.stderr)
        return 1
    comparison = None
    if args.comparison:
        try:
            comparison = json.loads(Path(args.comparison).read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            print(f"error: cannot load comparison: {exc}", file=sys.stderr)
            return 1
    if args.mock_echo:
        provider = MockProvider.echo()
    elif args.mock_text is not None:
        provider = MockProvider.fixed(args.mock_text)
    else:
        try:
            provider = MockProvider.fixed(
                Path(args.mock_file).read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError) as exc:
            print(f"error: cannot read mock file: {exc}", file=sys.stderr)
            return 1
    try:
        result = revise(draft, profile, comparison, provider, mode=args.mode,
                        user_request=args.user_request,
                        max_attempts=args.max_attempts)
    except (ValueError, TypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if not result["validation"]["passed"]:
        print("revision rejected: "
              + "; ".join(result["validation"]["failures"]), file=sys.stderr)
        return 1
    if args.output:
        try:
            Path(args.output).write_text(result["revised_text"], encoding="utf-8")
        except OSError as exc:
            print(f"error: cannot write output: {exc}", file=sys.stderr)
            return 1
    else:
        print(result["revised_text"])
    if args.report:
        try:
            Path(args.report).write_text(
                json.dumps(strip_original(result), indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8")
        except OSError as exc:
            print(f"error: cannot write report: {exc}", file=sys.stderr)
            return 1
    if args.show_diff:
        print("".join(difflib.unified_diff(
            draft.splitlines(keepends=True), result["revised_text"].splitlines(keepends=True),
            fromfile="original", tofile="revised")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
