# Copyright (c) 2026 Daniel Ari Friedman
"""Fixed primary-text proximity counts; aggregates never contain source contexts."""

from collections import Counter
from pathlib import Path
from typing import Annotated, Final, Literal

from pydantic import Field, FiniteFloat, model_validator

from .corpus import load_import
from .models import CorpusPin, FrozenModel, Passage, ResearchError, Role
from .search import matching_spans, search_passages
from .search_models import SearchFacet, SearchRequest
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
Count = Annotated[int, Field(ge=0, strict=True)]
Rate = Annotated[FiniteFloat, Field(ge=0, strict=True)]


class TermCount(FrozenModel):
    term: str
    occurrences: Count


class ProximityRow(FrozenModel):
    request: SearchRequest
    eligible_source_units: Count
    eligible_word_tokens: Count
    eligible_source_families: Count
    matched_source_units: Count
    matched_source_families: Count
    total_occurrences: Count
    occurrences_per_10000_tokens: Rate | None
    terms: tuple[TermCount, ...]
    facets: tuple[SearchFacet, ...]

    @model_validator(mode="after")
    def reconcile(self) -> "ProximityRow":
        facets = self.facets
        denominator = sum(f.word_tokens for f in facets)
        rate = self.total_occurrences * 10000 / denominator if denominator else None
        if (
            tuple(t.term for t in self.terms) != self.request.terms
            or len({(f.work_id, f.plane, f.role) for f in facets}) != len(facets)
            or any(f.role != Role.PRIMARY for f in facets)
            or sum(f.source_units for f in facets) != self.eligible_source_units
            or denominator != self.eligible_word_tokens
            or len({f.work_id for f in facets}) != self.eligible_source_families
            or sum(f.matched_units for f in facets) != self.matched_source_units
            or len({f.work_id for f in facets if f.matched_units}) != self.matched_source_families
            or sum(f.occurrences for f in facets) != self.total_occurrences
            or sum(t.occurrences for t in self.terms) != self.total_occurrences
            or any(t.occurrences < self.matched_source_units for t in self.terms)
            or self.occurrences_per_10000_tokens != rate
            or any(
                f.matched_units > f.source_units
                or f.occurrences < len(self.terms) * f.matched_units
                or bool(f.occurrences) != bool(f.matched_units)
                or f.occurrences_per_10000_tokens
                != (f.occurrences * 10000 / f.word_tokens if f.word_tokens else None)
                for f in facets
            )
        ):
            raise ResearchError("proximity_row", "Counts, labels, rates or denominators disagree")
        return self


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
        denominator = tuple(
            (f.work_id, f.plane, f.role, f.source_units, f.word_tokens) for f in self.rows[0].facets
        )
        for index, row in enumerate(self.rows):
            request = SearchRequest(
                terms=row.request.terms,
                mode="all",
                limit=1,
                context_chars=0,
                window_words=row.request.window_words,
            )
            if row.request != request or row.eligible_source_units > self.scanned_source_units:
                raise ResearchError("proximity_request", "Require fixed primary whole-word ALL")
            if (
                tuple(
                    (f.work_id, f.plane, f.role, f.source_units, f.word_tokens) for f in row.facets
                )
                != denominator
            ):
                raise ResearchError("proximity_denominator", "Every width uses identical strata")
            if index % len(BUDGETS):
                previous = self.rows[index - 1]
                if (
                    previous.matched_source_units > row.matched_source_units
                    or previous.matched_source_families > row.matched_source_families
                    or any(
                        a.occurrences > b.occurrences
                        for a, b in zip(previous.terms, row.terms, strict=True)
                    )
                    or any(
                        a.matched_units > b.matched_units or a.occurrences > b.occurrences
                        for a, b in zip(previous.facets, row.facets, strict=True)
                    )
                ):
                    raise ResearchError("proximity_monotonicity", "Widening cannot remove matches")
        return self


def build_proximity_study(passages: tuple[Passage, ...], pin: CorpusPin) -> ProximityStudy:
    """Build the fixed grid on supplied units, including small independent test corpora."""
    primary = tuple(p for p in passages if p.text_role == Role.PRIMARY)
    rows: list[ProximityRow] = []
    for pair in PAIRS:
        for budget in BUDGETS:
            request = SearchRequest(
                terms=pair, mode="all", window_words=budget, limit=1, context_chars=0
            )
            result = search_passages(passages, request)
            counts: Counter[str] = Counter()
            for passage in primary:
                counts.update(term for term, _, _ in matching_spans(passage.text, request))
            tokens = sum(f.word_tokens for f in result.facets)
            rows.append(
                ProximityRow(
                    request=request,
                    eligible_source_units=result.eligible_source_units,
                    eligible_word_tokens=tokens,
                    eligible_source_families=len({f.work_id for f in result.facets}),
                    matched_source_units=result.matched_source_units,
                    matched_source_families=len(
                        {f.work_id for f in result.facets if f.matched_units}
                    ),
                    total_occurrences=result.total_occurrences,
                    occurrences_per_10000_tokens=result.total_occurrences * 10000 / tokens
                    if tokens
                    else None,
                    terms=tuple(TermCount(term=term, occurrences=counts[term]) for term in pair),
                    facets=result.facets,
                )
            )
    return ProximityStudy(corpus_pin=pin, scanned_source_units=len(passages), rows=tuple(rows))


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
    names = ("proximity_study.py", "proximity_figure.py", "search.py", "search_models.py")
    return tuple((name, digest(Path(__file__).with_name(name))) for name in names)
