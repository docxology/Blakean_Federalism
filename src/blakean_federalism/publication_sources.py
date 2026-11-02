# Copyright (c) 2026 Daniel Ari Friedman
"""Private manuscript source policy, independent of template execution."""

from collections.abc import Mapping
from pathlib import Path

from . import __version__
from .method_provenance import shared_source_hashes
from .models import ResearchError
from .review_timing_inputs import INPUT_NAMES

SOURCE_NAMES = (
    "docs/manuscript/states-change.md",
    "docs/manuscript/references-and-rights.md",
    "docs/manuscript/references.bib",
    "docs/manuscript/config.yaml",
    "docs/manuscript/preamble.md",
    "research/manuscript-inputs.json",
    "research/template-rendering.json",
    "research/citation-catalog.json",
    "research/search-study-0.8.0.json",
    "docs/manuscript/notation.md",
    "research/proximity-study-0.10.0.json",
    "docs/style-guide.md",
    "research/procedural-comparison-reading-20261028.json",
    "research/review-pressure-20261029.json",
    "research/textual-collation-20261029.json",
    "research/pressure-reading-20261029.json",
    "docs/research/review-pressure-20261029.md",
    "pyproject.toml",
    "uv.lock",
)

REVIEW_SOURCE_NAMES = (
    "src/blakean_federalism/institutional_review_models.py",
    "src/blakean_federalism/institutional_review.py",
    "src/blakean_federalism/institutional_review_figure.py",
    "tools/audit_institutional_review.py",
    "tests/test_institutional_review.py",
    "tests/test_institutional_review_tool.py",
    "research/institutional-review-cases.json",
    "docs/research/institutional-review.md",
    "docs/manuscript/institutional-review-supplement.md",
    "docs/manuscript/institutional-review-insertion.md",
    "research/cases.json",
    "src/blakean_federalism/review_inputs.py",
    "src/blakean_federalism/review_comparison.py",
    "src/blakean_federalism/review_comparison_run.py",
    "src/blakean_federalism/review_comparison_figure.py",
    "docs/research/procedural-comparison.md",
)


def publication_source_names(root: Path, article: str) -> tuple[str, ...]:
    """Bind all local producers and the conditional domain inputs before preparation."""
    producers = tuple(
        sorted(
            p.relative_to(root).as_posix()
            for p in (root / "src/blakean_federalism").rglob("*")
            if p.is_file() and p.suffix in (".py", ".css", ".js", ".html", ".ttf", ".txt")
        )
    )
    review = REVIEW_SOURCE_NAMES if "#fig:review-matrix" in article else ()
    timing = INPUT_NAMES if "#fig:review-timing-" in article else ()
    return SOURCE_NAMES + review + timing + producers + ("tools/template_render.py",)


def verify_delegated_producers(version: str, producers: Mapping[str, str]) -> None:
    """Retain old absent bindings; current production must bind the actual shared SDK."""
    if (producers or version == __version__) and dict(producers) != shared_source_hashes():
        raise ResearchError("publication_producer_changed", "Delegated SDK sources differ")
