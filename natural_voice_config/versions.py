"""Explicit versions and profile compatibility checking.

Component versions are NOT assumed identical: each package keeps its own
constant, mirrored here for single-point discovery. Profiles carry the version
that built them; newer code checks compatibility before use and fails clearly
instead of silently misreading an old profile.
"""

NATURAL_VOICE_VERSION = "0.8.0"
ANALYZER_VERSION = "0.1.0"
PROFILE_VERSION = "0.1.0"
COMPARISON_VERSION = "0.1.0"
REVISION_VERSION = "0.1.0"
ADAPTER_VERSION = "0.7"

COMPONENT_VERSIONS = {
    "natural_voice": NATURAL_VOICE_VERSION,
    "analyzer": ANALYZER_VERSION,
    "profile": PROFILE_VERSION,
    "comparison": COMPARISON_VERSION,
    "revision": REVISION_VERSION,
    "adapter": ADAPTER_VERSION,
}

# Profile versions this code knows how to read.
COMPATIBLE_PROFILE_VERSIONS = frozenset({"0.1.0"})


def check_profile_compatibility(profile: dict) -> tuple[str, list[str]]:
    """Return (status, notes) for a profile dict.

    Statuses: "compatible" (known version), "compatible_with_warning"
    (readable but superseded — none defined yet, reserved), "unsupported"
    (missing/unknown version: fail clearly, never silently misread).
    """
    if not isinstance(profile, dict):
        return "unsupported", ["profile is not a JSON object"]
    version = profile.get("profile_version")
    if version in COMPATIBLE_PROFILE_VERSIONS:
        notes = []
        analyzer = (profile.get("metadata") or {}).get("analyzer_version")
        if analyzer and analyzer != ANALYZER_VERSION:
            notes.append(f"profile built with analyzer {analyzer}; "
                         f"current analyzer is {ANALYZER_VERSION}")
        return "compatible", notes
    if version is None:
        return "unsupported", ["profile has no profile_version; refusing to guess"]
    return "unsupported", [f"profile_version {version!r} is not supported by "
                           f"this code (knows {sorted(COMPATIBLE_PROFILE_VERSIONS)})"]
