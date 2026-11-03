# Copyright (c) 2026 Daniel Ari Friedman
"""Add current producer custody without changing the archival review audit schema."""

from collections.abc import Mapping
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Literal

from blake.methods.producer import SourceBinding, source_hashes

from . import __version__
from .institutional_review_models import ReviewInput
from .method_provenance import shared_source_hashes
from .models import Digest, FileReceipt, ResearchError
from .review_inputs import ValidatedReviewAudit
from .storage import digest, safe_path, verify_file, write_new

SIDECAR_NAME = "review-producer-receipt.json"
_BASE_OUTPUTS = ("review-report.json", "review-receipt.json")
_FIGURE_OUTPUTS = tuple(
    "figures/" + name + suffix
    for name in ("institutional-review", "review-continuity")
    for suffix in (".pdf", ".png")
)


@dataclass(frozen=True, slots=True)
class ReviewAuditSources:
    cases: Path
    decisions: Path
    tool: Path


class ReviewProducerReceipt(ReviewInput):
    schema_version: Literal[1] = 1
    producer_version: str
    producer_state: Literal["artifacts_complete"] = "artifacts_complete"
    review_cases_sha256: Digest
    baseline_decisions_sha256: Digest
    producers: dict[str, Digest]
    outputs: tuple[FileReceipt, ...]
    scope: str = (
        "Additive source-bound stipulated audit; the original report and schema-1 receipt "
        "retain their bytes. Installed, native, scholarly and release acceptance are separate."
    )


def review_audit_producers(tool: Path, *, figures: bool) -> dict[str, str]:
    """Bind the actual caller, local evaluator and delegated public interval/storage methods."""
    local = (
        "__init__.py",
        "review_audit_provenance.py",
        "review_inputs.py",
        "institutional_review.py",
        "institutional_review_models.py",
        "institutions.py",
        "models.py",
        "storage.py",
        "method_provenance.py",
    )
    extra = (
        (
            "institutional_review_figure.py",
            "figure_style.py",
            "resources/fonts/Vera.ttf",
            "resources/fonts/bitstream-vera-license.txt",
        )
        if figures
        else ()
    )
    return {
        **source_hashes((SourceBinding("blakean_federalism", local + extra),)),
        **shared_source_hashes(),
        "caller/audit_institutional_review.py": digest(safe_path(tool.parent, tool.name)),
    }


def _output_names(*, figures: bool) -> tuple[str, ...]:
    return _BASE_OUTPUTS + (_FIGURE_OUTPUTS if figures else ())


def _check_inputs(cases: Path, decisions: Path, expected: tuple[str, str]) -> None:
    actual = tuple(digest(safe_path(path.parent, path.name)) for path in (cases, decisions))
    if actual != expected:
        raise ResearchError("review_input_changed", "Review input bytes changed during production")


def write_review_producer_receipt(
    output: Path,
    audit: ValidatedReviewAudit,
    producers: Mapping[str, str],
    sources: ReviewAuditSources,
    *,
    figures: bool,
) -> None:
    """Write the new completion marker last, after checking actual inputs and producers."""
    hashes = (
        sha256(audit.review_bytes).hexdigest(),
        sha256(audit.baseline_bytes).hexdigest(),
    )
    _check_inputs(sources.cases, sources.decisions, hashes)
    if dict(producers) != review_audit_producers(sources.tool, figures=figures):
        raise ResearchError("review_producer_changed", "Review producer bytes changed")
    receipt = ReviewProducerReceipt(
        producer_version=__version__,
        review_cases_sha256=hashes[0],
        baseline_decisions_sha256=hashes[1],
        producers=dict(producers),
        outputs=tuple(
            FileReceipt(
                path=name,
                size=safe_path(output, name).stat().st_size,
                sha256=digest(safe_path(output, name)),
            )
            for name in _output_names(figures=figures)
        ),
    )
    write_new(output / SIDECAR_NAME, receipt.model_dump_json(indent=2) + "\n")


def verify_review_producer_receipt(
    output: Path, cases: Path, decisions: Path, tool: Path, *, figures: bool
) -> ReviewProducerReceipt:
    """Refuse incomplete or changed new production before copying manuscript figures."""
    receipt = ReviewProducerReceipt.model_validate_json(
        safe_path(output, SIDECAR_NAME).read_bytes()
    )
    if receipt.producer_version != __version__:
        raise ResearchError("review_producer_changed", "Reported producer version differs")
    _check_inputs(
        cases, decisions, (receipt.review_cases_sha256, receipt.baseline_decisions_sha256)
    )
    if receipt.producers != review_audit_producers(tool, figures=figures):
        raise ResearchError("review_producer_changed", "Review producer bytes differ")
    expected = _output_names(figures=figures)
    if len(receipt.outputs) != len(expected) or {p.path for p in receipt.outputs} != set(expected):
        raise ResearchError(
            "review_output_membership", "Exact report/receipt/figure closure required"
        )
    actual = {
        p.relative_to(output).as_posix() for p in output.rglob("*") if p.is_file() or p.is_symlink()
    }
    if actual != set(expected) | {SIDECAR_NAME}:
        raise ResearchError("review_output_membership", "Unbound or missing audit output")
    for binding in receipt.outputs:
        _ = verify_file(output, binding.path, binding.size, binding.sha256)
    return receipt
