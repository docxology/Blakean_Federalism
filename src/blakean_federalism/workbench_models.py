# Copyright (c) 2026 Daniel Ari Friedman
"""Typed portable evidence, separate from rendering and custody operations."""

from typing import Literal

from pydantic import model_validator

from .corpus_statistics_models import CorpusStatistics
from .institutional_experiment_models import InstitutionalExperiment
from .institutions import assess
from .manuscript import Asset, Quotation
from .models import (
    Assessment,
    CorpusPin,
    Decision,
    Digest,
    FileReceipt,
    FrozenModel,
    QuerySpec,
    ResearchError,
)
from .observations import CoverageCell


class ReadingNote(FrozenModel):
    source: str
    reading_status: str
    locator: str | None = None
    url: str | None = None
    sha256: Digest | None = None


class CaseTrace(FrozenModel):
    record: Decision
    assessment: Assessment
    poetic_label_ablation_invariant: bool

    @model_validator(mode="after")
    def require_current_trace(self) -> "CaseTrace":
        expected = assess(self.record)
        ablated = self.record.model_copy(
            update={"poetic_state_interpretation": None, "national_affiliations": ()}
        )
        if self.assessment != expected or self.poetic_label_ablation_invariant != (
            assess(ablated) == expected
        ):
            raise ResearchError("report_trace", self.record.decision_id)
        return self


class Workbench(FrozenModel):
    schema_version: Literal[1, 2] = 2
    producer_version: str
    corpus_statistics: CorpusStatistics | None = None
    institutional_experiments: InstitutionalExperiment | None = None
    corpus_pin: CorpusPin
    source_units: int
    query_groups: tuple[QuerySpec, ...]
    source_urls: dict[str, str]
    query_count: int
    stored_occurrences: int
    coverage: tuple[CoverageCell, ...]
    cases: tuple[CaseTrace, ...]
    quotations: tuple[Quotation, ...]
    images: tuple[Asset, ...]
    reading: tuple[ReadingNote, ...]
    inputs: tuple[FileReceipt, ...]
    producer_sources: dict[str, Digest]
    limits: tuple[str, ...] = (
        "Corpus units retain copies, pages and source roles; coverage keeps its own denominator.",
        "Token and source-family denominators accompany each lexical association.",
        "Synthetic cases expose safeguards, fixed material context and intervention fields.",
        "Each quotation, image and reading has its own source, locator and rights record.",
    )
