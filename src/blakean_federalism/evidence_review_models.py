# Copyright (c) 2026 Daniel Ari Friedman
"""Private interpretive labels; reviewed retrieval is not institutional authority."""

from enum import StrEnum
from typing import Literal

from blake.methods.annotations import ReviewCounts
from blake.methods.models import Artifact, Digest, EvidenceError, FrozenModel
from pydantic import Field, model_validator

from .models import CorpusPin, QuerySpec


class PoliticalReadingDecision(StrEnum):
    TEXTUAL_SUPPORT = "textual_support"
    COUNTERREADING = "counterreading"
    NONPOLITICAL = "nonpolitical"
    UNCERTAIN = "uncertain"


class EvidenceDecision(FrozenModel):
    run_sha256: Digest
    hit_id: str
    decision: PoliticalReadingDecision
    reviewer: str
    rationale: str
    verification_locator: str = ""

    @model_validator(mode="after")
    def authored(self) -> "EvidenceDecision":
        if not self.reviewer.strip() or not self.rationale.strip():
            raise EvidenceError("review_authorship", self.hit_id)
        if (
            self.decision
            in (
                PoliticalReadingDecision.TEXTUAL_SUPPORT,
                PoliticalReadingDecision.COUNTERREADING,
            )
            and not self.verification_locator.strip()
        ):
            raise EvidenceError("review_locator", self.hit_id)
        return self


class CandidateSummary(FrozenModel):
    query_sha256: Digest
    candidate_hits: int = Field(ge=0)
    blake_primary_hits: int = Field(ge=0)
    exploratory_hits: int = Field(ge=0)
    scanned_source_units: int = Field(ge=0)


class EvidenceRun(FrozenModel):
    schema_version: Literal[1] = 1
    producer_epoch: Literal["political-evidence-review-v1"] = "political-evidence-review-v1"
    producer_sha256: Digest
    corpus_pin: CorpusPin
    queries: tuple[QuerySpec, ...]
    query_sha256: Digest
    files: tuple[Artifact, ...]


class EvidenceReviewSummary(FrozenModel):
    run_sha256: Digest
    candidate_producer_sha256: Digest
    decisions_sha256: Digest
    producer_sha256: Digest
    all_candidates: ReviewCounts
    blake_primary: ReviewCounts
    exploratory: ReviewCounts
    interpretation: Literal[
        "Authored readings; omissions are unreviewed; decisions confer no institutional authority."
    ] = "Authored readings; omissions are unreviewed; decisions confer no institutional authority."


class ReviewReceipt(FrozenModel):
    schema_version: Literal[1] = 1
    producer_epoch: Literal["political-evidence-review-v1"] = "political-evidence-review-v1"
    source_run_sha256: Digest
    candidate_producer_sha256: Digest
    decisions_sha256: Digest
    producer_sha256: Digest
    files: tuple[Artifact, ...]
