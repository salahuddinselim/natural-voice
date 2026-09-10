"""Minimal CLI: ``python -m natural_voice_profile build <files...>``.

Builds a voice profile from sample files (UTF-8) and prints JSON to stdout or
writes it to ``--output``. Shell glob patterns (e.g. ``samples/*.txt``) are
expanded by this CLI itself so it works on shells without globbing. Sample text
is measured only — it never appears in output or logs.
"""

from __future__ import annotations

import argparse
import glob
import sys

from natural_voice_analyzer.output import to_json

from .builder import CONTEXTS, build_profile_from_files


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build an Author Voice Profile from writing-sample files.")
    sub = parser.add_subparsers(dest="command", required=True)
    build = sub.add_parser("build", help="Build a profile from sample files.")
    build.add_argument("inputs", nargs="+",
                       help="Sample files or glob patterns (UTF-8 text).")
    build.add_argument("--output", default=None,
                       help="Write profile JSON to this path instead of stdout.")
    build.add_argument("--context", default="general", choices=CONTEXTS,
                       help="Profile context label (default: general).")
    build.add_argument("--pretty", action="store_true",
                       help="Pretty-print the JSON output.")
    build.add_argument("--top-k", type=int, default=30,
                       help="Inventory depth per sample (default: 30).")
    return parser


def _expand(inputs: list[str]) -> list[str]:
    expanded: list[str] = []
    for pattern in inputs:
        matches = sorted(glob.glob(pattern))
        expanded.extend(matches if matches else [pattern])
    # De-duplicate while preserving order for determinism.
    return list(dict.fromkeys(expanded))


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "build":
        files = _expand(args.inputs)
        try:
            profile = build_profile_from_files(
                files, context=args.context, top_k=args.top_k)
        except (ValueError, TypeError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        text = to_json(profile, pretty=args.pretty)
        if args.output:
            from pathlib import Path
            Path(args.output).write_text(text + "\n", encoding="utf-8")
        else:
            print(text)
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
