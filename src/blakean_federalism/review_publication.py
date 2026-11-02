# Copyright (c) 2026 Daniel Ari Friedman
"""Bind the approved person-specific audit into the source-checkout publication route."""

import subprocess
import sys
from pathlib import Path

from .models import ResearchError
from .review_audit_provenance import verify_review_producer_receipt
from .storage import copy_new, digest, safe_path, write_new

NAMES = ("institutional-review", "review-continuity")


def prepare_review_figures(root: Path, stage: Path) -> dict[str, str]:
    """Run the source-bound audit and verify its additive producer receipt before copying."""
    sources = tuple(
        safe_path(root, name)
        for name in (
            "research/institutional-review-cases.json",
            "research/cases.json",
            "tools/audit_institutional_review.py",
        )
    )
    before = tuple(digest(path) for path in sources)
    audit = stage / "review-audit"
    result = subprocess.run(  # noqa: S603 -- Fixed source-checkout tool and explicit argv.
        [
            sys.executable,
            str(sources[2]),
            "--cases",
            str(sources[0]),
            "--decisions",
            str(sources[1]),
            "--output",
            str(audit),
            "--figures",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    write_new(stage / "review-audit.log", result.stdout + result.stderr)
    result.check_returncode()
    if tuple(digest(path) for path in sources) != before:
        raise ResearchError("review_source_changed", "Review source changed during audit")
    _ = verify_review_producer_receipt(audit, sources[0], sources[1], sources[2], figures=True)
    for name in NAMES:
        for suffix in (".pdf", ".png"):
            source = safe_path(audit, "figures/" + name + suffix)
            copy_new(source, stage / "output/figures" / (name + suffix))
    return {name: name + ".png" for name in NAMES}
