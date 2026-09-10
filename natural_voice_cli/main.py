"""Unified `natural-voice` CLI: profile / compare / revise / providers / validate / version.

Thin dispatcher over the existing package APIs — no duplicated methodology.
Provider for `revise` comes from `--provider` (default "mock", which needs one
of the --mock-* flags) plus `natural_voice_config` (CLI > env > file > default).
Console entry point (see pyproject.toml): ``natural-voice = natural_voice_cli.main:main``.
"""

from __future__ import annotations

import argparse
import difflib
import glob
import json
import sys
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="natural-voice",
                                     description="Natural Voice: voice-consistent writing tools.")
    parser.add_argument("--config", default=None, help="JSON config file path.")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging.")
    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser("profile", help="Build a voice profile (use: profile build ...).")
    build_sub = build.add_subparsers(dest="profile_command", required=True)
    build_cmd = build_sub.add_parser("build", help="Build a profile from sample files.")
    build_cmd.add_argument("inputs", nargs="+", help="Sample files or glob patterns (UTF-8).")
    build_cmd.add_argument("--output", default=None, help="Write profile JSON here.")
    build_cmd.add_argument("--context", default=None, help="Profile context label.")
    build_cmd.add_argument("--top-k", type=int, default=None, help="Inventory depth.")

    compare = sub.add_parser("compare", help="Compare a draft against a profile.")
    compare.add_argument("--draft", required=True)
    compare.add_argument("--profile", required=True)
    compare.add_argument("--output", default=None)
    compare.add_argument("--pretty", action="store_true")
    compare.add_argument("--draft-context", default=None)
    compare.add_argument("--weights", default=None, help="JSON dimension weights.")

    revise = sub.add_parser("revise", help="Revise a draft for voice consistency.")
    revise.add_argument("--draft", required=True)
    revise.add_argument("--profile", required=True)
    revise.add_argument("--comparison", default=None)
    revise.add_argument("--mode", default=None, help="conservative|balanced|expressive")
    revise.add_argument("--user-request", default="")
    revise.add_argument("--max-attempts", type=int, default=None)
    revise.add_argument("--output", default=None, help="Write revised text here (on pass).")
    revise.add_argument("--report", default=None, help="Write stripped report here (on pass).")
    revise.add_argument("--show-diff", action="store_true")
    revise.add_argument("--provider", default=None, help="mock|openai-compatible|anthropic")
    revise.add_argument("--model", default=None)
    revise.add_argument("--mock-echo", action="store_true")
    revise.add_argument("--mock-text", default=None)
    revise.add_argument("--mock-file", default=None)

    sub.add_parser("providers", help="List available LLM providers.")
    validate = sub.add_parser("validate", help="Validate a saved profile file.")
    validate.add_argument("profile", help="Path to profile JSON.")
    sub.add_parser("version", help="Show component versions.")
    return parser


def main(argv: list[str] | None = None) -> int:
    from natural_voice_config import load_config, setup_logging

    args = build_parser().parse_args(argv)
    cli_config = _cli_config_values(args)
    try:
        config = load_config(cli_args=cli_config,
                             file_path=getattr(args, "config", None))
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.verbose or config.verbose:
        setup_logging(verbose=True)
    handlers = {"profile": _cmd_profile, "compare": _cmd_compare,
                "revise": _cmd_revise, "providers": _cmd_providers,
                "validate": _cmd_validate, "version": _cmd_version}
    try:
        return handlers[args.command](args, config)
    except (ValueError, TypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


def _cli_config_values(args) -> dict:
    values: dict = {}
    for key in ("provider", "model", "mode"):
        value = getattr(args, key, None)
        if value is not None:
            values[key] = value
    if getattr(args, "verbose", False):
        values["verbose"] = True
    return values


def _expand(inputs: list[str]) -> list[str]:
    expanded: list[str] = []
    for pattern in inputs:
        matches = sorted(glob.glob(pattern))
        expanded.extend(matches if matches else [pattern])
    return list(dict.fromkeys(expanded))


def _write_json(path: str | None, payload: dict, pretty: bool) -> None:
    from natural_voice_analyzer.output import to_json
    text = to_json(payload, pretty=pretty)
    if path:
        Path(path).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)


def _cmd_profile(args, config) -> int:
    from natural_voice_profile import build_profile_from_files, save_profile
    files = _expand(args.inputs)
    try:
        profile = build_profile_from_files(
            files, context=args.context or "general")
    except (ValueError, TypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if args.output:
        save_profile(profile, args.output)
        print(f"profile written to {args.output} "
              f"({profile['metadata']['sample_count']} samples, "
              f"confidence {profile['confidence']['overall']})")
    else:
        _write_json(None, profile, pretty=True)
    return 0


def _cmd_compare(args, config) -> int:
    from natural_voice_comparison import compare_draft_file
    try:
        weights = json.loads(args.weights) if args.weights else None
        report = compare_draft_file(args.draft, args.profile,
                                    weights=weights,
                                    draft_context=args.draft_context)
    except (ValueError, TypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    _write_json(args.output, report, pretty=args.pretty)
    return 0


def _cmd_revise(args, config) -> int:
    from natural_voice_revision import revise
    from natural_voice_revision.result import strip_original
    provider_name = args.provider or config.provider.provider
    try:
        provider = _build_provider(provider_name, args, config)
        draft = Path(args.draft).read_text(encoding="utf-8")
        profile = json.loads(Path(args.profile).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        print(f"error: cannot load input: {exc}", file=sys.stderr)
        return 1
    comparison = None
    if args.comparison:
        try:
            comparison = json.loads(Path(args.comparison).read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            print(f"error: cannot load comparison: {exc}", file=sys.stderr)
            return 1
    try:
        result = revise(draft, profile, comparison, provider,
                        mode=args.mode or config.mode,
                        user_request=args.user_request, max_attempts=1)
    except (ValueError, TypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if not result["validation"]["passed"]:
        print("revision rejected: " + "; ".join(result["validation"]["failures"]),
              file=sys.stderr)
        return 1
    if args.output:
        Path(args.output).write_text(result["revised_text"], encoding="utf-8")
    else:
        print(result["revised_text"])
    if args.report:
        Path(args.report).write_text(
            json.dumps(strip_original(result), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8")
    if args.show_diff:
        print("".join(difflib.unified_diff(
            draft.splitlines(keepends=True),
            result["revised_text"].splitlines(keepends=True),
            fromfile="original", tofile="revised")))
    return 0


def _build_provider(provider_name: str, args, config):
    import providers
    if provider_name == "mock":
        from llm.mock import MockProvider
        if args.mock_echo:
            return MockProvider.echo()
        if args.mock_text is not None:
            return MockProvider.fixed(args.mock_text)
        if args.mock_file is not None:
            return MockProvider.fixed(
                Path(args.mock_file).read_text(encoding="utf-8"))
        raise ValueError("mock provider needs --mock-echo, --mock-text, or --mock-file")
    provider_config = config.provider
    return providers.get_provider(
        provider_name, model=args.model or provider_config.model,
        base_url=provider_config.base_url,
        temperature=provider_config.temperature,
        max_tokens=provider_config.max_tokens,
        timeout_seconds=provider_config.timeout_seconds,
        max_retries=provider_config.max_retries)


def _cmd_providers(args, config) -> int:
    import providers
    from llm.capabilities import ProviderCapabilities
    for name in providers.list_providers():
        print(f"- {name}")
    _ = ProviderCapabilities  # capability details: see docs/providers.md
    print(f"(default: {config.provider.provider}; credentials via environment only)")
    return 0


def _cmd_validate(args, config) -> int:
    from natural_voice_config import check_profile_compatibility
    from natural_voice_profile import validate_profile
    try:
        profile = json.loads(Path(args.profile).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        print(f"error: cannot load profile: {exc}", file=sys.stderr)
        return 1
    errors = validate_profile(profile)
    if errors:
        print("invalid profile:")
        for error in errors:
            print(f"  - {error}")
        return 1
    status, notes = check_profile_compatibility(profile)
    print(f"profile valid; compatibility: {status}")
    for note in notes:
        print(f"  note: {note}")
    return 0 if status != "unsupported" else 1


def _cmd_version(args, config) -> int:
    from natural_voice_config import COMPONENT_VERSIONS
    for component in sorted(COMPONENT_VERSIONS):
        print(f"{component}: {COMPONENT_VERSIONS[component]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
