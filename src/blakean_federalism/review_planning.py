# Copyright (c) 2026 Daniel Ari Friedman
"""Private scope and decision policy for shared deterministic review planning."""

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Literal, assert_never

from blake.methods.annotations import csv_decisions, validate_decision_membership
from blake.methods.models import Digest, EvidenceError, FrozenModel
from blake.methods.review_batches import publish_review_batch, verify_review_batch
from blake.methods.review_planning_models import (
    ReviewBatchReceipt,
    ReviewPlanSpec,
    ReviewSelection,
    VerifiedReviewBatch,
)
from blake.methods.runs import digest, read_regular
from blake.studies import BLAKE_AUTHOR, StudyHit

from .evidence_review import load_review_run, private_output
from .evidence_review_models import EvidenceDecision


class ReviewScope(StrEnum):
    """Keep primary reading eligibility distinct from the complete retained run."""

    BLAKE_PRIMARY_READING = "blake_primary_reading"
    ALL_SOURCES = "all_sources"


class PinnedReviewFile(FrozenModel):
    """A caller-held pin applies to these exact bytes, independently of a batch."""

    path: Path
    sha256: Digest


class PinnedReviewBatch(FrozenModel):
    """The independently retained hash identifies the batch completion receipt."""

    directory: Path
    receipt_sha256: Digest


class ReviewPlanningRequest(FrozenModel):
    """Application policy; ranking, caps and serialization belong to Blake."""

    schema_version: Literal[1] = 1
    source_run: Path
    source_run_sha256: Digest
    decisions: PinnedReviewFile | None
    scope: ReviewScope
    selection: ReviewSelection


@dataclass(frozen=True, slots=True)
class ScopedReviewInput:
    """One admitted pool and explicit global versus in-scope review counts."""

    request: ReviewPlanningRequest
    hits: tuple[StudyHit, ...]
    spec: ReviewPlanSpec
    global_candidates: int
    global_reviewed: int
    scoped_candidates: int
    scoped_reviewed: int


def pinned_review_bytes(source: PinnedReviewFile) -> bytes:
    """Read regular bytes once and refuse a caller-pin mismatch."""
    raw = read_regular(source.path, "review planning input")
    if digest(raw) != source.sha256:
        raise EvidenceError("review_planning_input_pin", str(source.path))
    return raw


def reviewed_ids(
    source: PinnedReviewFile | None, hits: tuple[StudyHit, ...], run_sha256: str
) -> tuple[str, ...]:
    """Validate every authored record globally before any eligibility filtering."""
    if source is None:
        return ()
    raw = pinned_review_bytes(source)
    match source.path.suffix.casefold():
        case ".csv":
            parsed = tuple(
                EvidenceDecision.model_validate(item.model_dump())
                for item in csv_decisions(raw, hits, run_sha256)
            )
        case ".jsonl":
            parsed = tuple(
                EvidenceDecision.model_validate_json(line)
                for line in raw.splitlines()
                if line.strip()
            )
        case _:
            raise EvidenceError("decision_format", "Use authored CSV or JSONL")
    validate_decision_membership(parsed, hits, run_sha256)
    return tuple(item.hit_id for item in parsed)


def scope_hits(hits: tuple[StudyHit, ...], scope: ReviewScope) -> tuple[StudyHit, ...]:
    """Derive eligibility from all three source facets without repairing a flag."""
    match scope:
        case ReviewScope.BLAKE_PRIMARY_READING:
            return tuple(
                hit
                for hit in hits
                if hit.author_id == BLAKE_AUTHOR
                and hit.text_role == "primary"
                and hit.source_plane == "reading"
            )
        case ReviewScope.ALL_SOURCES:
            return hits
    assert_never(scope)


def load_planning_input(source: PinnedReviewFile) -> ScopedReviewInput:
    """Derive the full spec from the pinned request and admitted original evidence."""
    request = ReviewPlanningRequest.model_validate_json(pinned_review_bytes(source))
    _receipt, hits = load_review_run(request.source_run, request.source_run_sha256)
    reviewed = reviewed_ids(request.decisions, hits, request.source_run_sha256)
    scoped = scope_hits(hits, request.scope)
    scoped_ids = {hit.hit_id for hit in scoped}
    excluded = tuple(sorted(hit_id for hit_id in reviewed if hit_id in scoped_ids))
    spec = ReviewPlanSpec(
        source_run_sha256=request.source_run_sha256,
        source_context_sha256=source.sha256,
        selection=request.selection,
        excluded_hit_ids=excluded,
    )
    return ScopedReviewInput(
        request=request,
        hits=scoped,
        spec=spec,
        global_candidates=len(hits),
        global_reviewed=len(reviewed),
        scoped_candidates=len(scoped),
        scoped_reviewed=len(excluded),
    )


def publish_planning_request(source: PinnedReviewFile, output: Path) -> ReviewBatchReceipt:
    """Confine provider contexts before delegating the complete batch transaction."""
    context = load_planning_input(source)
    for origin in (source.path, context.request.source_run):
        private_output(output, origin)
    if context.request.decisions is not None:
        private_output(output, context.request.decisions.path)
    return publish_review_batch(context.hits, context.spec, output)


def verify_planning_request(
    source: PinnedReviewFile, batch: PinnedReviewBatch
) -> VerifiedReviewBatch:
    """Verify the batch and independently match its full request-derived policy."""
    context = load_planning_input(source)
    verified = verify_review_batch(batch.directory, batch.receipt_sha256, context.hits)
    if verified.plan.spec != context.spec:
        raise EvidenceError("review_planning_request_mismatch", str(batch.directory))
    return verified
