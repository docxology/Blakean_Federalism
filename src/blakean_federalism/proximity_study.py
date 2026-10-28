# Copyright (c) 2026 Daniel Ari Friedman
"""Fixed primary-text proximity counts; aggregates never contain source contexts."""

from pathlib import Path
from typing import Final, Literal

from blake.methods.proximity import (
    Count,
    ProximityGrid,
    ProximityRow,
    TermCount,
)
from blake.methods.proximity import (
    ProximityStudy as SharedProximityStudy,
)
from blake.methods.proximity import (
    build_proximity_study as shared_proximity_study,
)
from pydantic import model_validator

from .corpus import load_import
from .method_provenance import shared_source_hashes
from .models import CorpusPin, FrozenModel, Passage, ResearchError, Role
from .search_models import SearchRequest
from .search_study import SearchStudy
from .storage import digest

PAIRS: Final = (
    ("state", "individual"),
    ("states", "individuals"),
    ("nation", "liberty"),
    ("nations", "imagination"),
    ("system", "imagination"),
    ("labour", "misery"),
)
BUDGETS: Final = (8, 16, 32, 64, None)
PRIMARY_DENOMINATORS: Final = (199, 33, 644245)
CORPUS_UNITS: Final = 2067


class ProximityStudy(FrozenModel):
    schema_version: Literal[1] = 1
    corpus_pin: CorpusPin
    scanned_source_units: Count
    rows: tuple[ProximityRow, ...]
    method: Literal[
        "primary literal ALL; original Unicode word-token envelopes; stored copies retained"
    ] = "primary literal ALL; original Unicode word-token envelopes; stored copies retained"

    @model_validator(mode="after")
    def reconcile(self) -> "ProximityStudy":
        expected = tuple((pair, budget) for pair in PAIRS for budget in BUDGETS)
        if tuple((r.request.terms, r.request.window_words) for r in self.rows) != expected:
            raise ResearchError(
                "proximity_grid", "Require six fixed pairs and five ordered budgets"
            )
        for row in self.rows:
            request = SearchRequest(
                terms=row.request.terms,
                mode="all",
                limit=1,
                context_chars=0,
                window_words=row.request.window_words,
            )
            if row.request != request or row.eligible_source_units > self.scanned_source_units:
                raise ResearchError("proximity_request", "Require fixed primary whole-word ALL")
        _ = SharedProximityStudy(
            corpus_pin=self.corpus_pin,
            scanned_source_units=self.scanned_source_units,
            grid=ProximityGrid(requests=tuple(row.request for row in self.rows)),
            rows=self.rows,
        )
        return self


def build_proximity_study(passages: tuple[Passage, ...], pin: CorpusPin) -> ProximityStudy:
    """Build the fixed grid on supplied units, including small independent test corpora."""
    grid = ProximityGrid(
        requests=tuple(
            SearchRequest(terms=pair, mode="all", window_words=budget, limit=1, context_chars=0)
            for pair in PAIRS
            for budget in BUDGETS
        )
    )
    shared = shared_proximity_study(passages, pin, grid)
    return ProximityStudy(
        corpus_pin=shared.corpus_pin,
        scanned_source_units=shared.scanned_source_units,
        rows=shared.rows,
    )


def produce_proximity_study(
    directory: Path, pin: CorpusPin, retained: SearchStudy
) -> ProximityStudy:
    """Verify import and retained primary denominators before producing the real-corpus grid."""
    _, passages = load_import(directory, pin)
    if retained.corpus_pin != pin or retained.source_units != CORPUS_UNITS:
        raise ResearchError("proximity_pin", "Retained study must bind the same 2067-unit corpus")
    for query in retained.queries:
        primary = tuple(f for f in query.facets if f.role == Role.PRIMARY)
        observed = (
            sum(f.source_units for f in primary),
            len({f.work_id for f in primary}),
            sum(f.word_tokens for f in primary),
        )
        if observed != PRIMARY_DENOMINATORS:
            raise ResearchError("proximity_retained", "Retained primary denominators disagree")
    study = build_proximity_study(passages, pin)
    first = study.rows[0]
    actual = (
        first.eligible_source_units,
        first.eligible_source_families,
        first.eligible_word_tokens,
    )
    if len(passages) != CORPUS_UNITS or actual != PRIMARY_DENOMINATORS:
        raise ResearchError("proximity_corpus", "Require 2067 total; primary 199 / 33 / 644245")
    actual_strata = tuple(
        (f.work_id, f.plane, f.role, f.source_units, f.word_tokens) for f in first.facets
    )
    for query in retained.queries:
        retained_strata = tuple(
            (f.work_id, f.plane, f.role, f.source_units, f.word_tokens)
            for f in query.facets
            if f.role == Role.PRIMARY
        )
        if actual_strata != retained_strata:
            raise ResearchError("proximity_strata", "Retained primary family strata disagree")
    return study


def proximity_producer_hashes() -> tuple[tuple[str, str], ...]:
    """Bind producer files separately from the aggregate's scientific measurements."""
    names = (
        "proximity_study.py",
        "proximity_figure.py",
        "search.py",
        "search_models.py",
        "method_provenance.py",
    )
    private = tuple((name, digest(Path(__file__).with_name(name))) for name in names)
    return private + tuple(sorted(shared_source_hashes().items()))


__all__ = [
    "ProximityRow",
    "ProximityStudy",
    "TermCount",
    "build_proximity_study",
    "produce_proximity_study",
    "proximity_producer_hashes",
]
