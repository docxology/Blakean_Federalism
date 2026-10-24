# Copyright (c) 2026 Daniel Ari Friedman
"""Reconcile retrieval observations without promoting source units to unique works."""

import hashlib
import re
from collections import Counter, defaultdict

from pydantic import Field, model_validator

from .corpus import query_fingerprint
from .models import (
    Concordance,
    CorpusPin,
    FrozenModel,
    Passage,
    Plane,
    QuerySpec,
    ResearchError,
    Role,
)


class CoverageCell(FrozenModel):
    query_id: str
    plane: Plane
    role: Role
    occurrences: int = Field(ge=0)
    matched_source_documents: int = Field(ge=0)
    source_units: int = Field(ge=0)
    coverage_fraction: float | None = Field(ge=0, le=1)

    @model_validator(mode="after")
    def preserve_denominator(self) -> "CoverageCell":
        expected = self.matched_source_documents / self.source_units if self.source_units else None
        if (
            self.matched_source_documents > self.source_units
            or self.occurrences < self.matched_source_documents
            or (not self.source_units and self.occurrences)
            or self.coverage_fraction != expected
        ):
            raise ResearchError("coverage_denominator", self.query_id)
        return self


def reconcile_coverage(
    result: Concordance,
    passages: tuple[Passage, ...],
    queries: tuple[QuerySpec, ...],
    pin: CorpusPin,
) -> tuple[CoverageCell, ...]:
    """Check every stored span and aggregate; zero-source cells have undefined coverage.

    This reconciles the supplied run. It does not independently prove that the
    producer found every possible occurrence, literary meaning or whole-oeuvre absence.
    """
    by_id = {p.passage_id: p for p in passages}
    query_map = {q.query_id: q for q in queries}
    if (
        not passages
        or len(by_id) != len(passages)
        or len(passages) != result.scanned_source_documents
        or not queries
        or len(query_map) != len(queries)
        or any(not q.query_id.strip() for q in queries)
        or result.pin != pin
    ):
        raise ResearchError(
            "coverage_membership", "Run, source units and query identities disagree"
        )
    if result.query_sha256 != query_fingerprint(queries):
        raise ResearchError("coverage_query", "Query specification differs from the run")
    source_counts = Counter((p.source_plane, p.text_role) for p in passages)
    hashes = {p.passage_id: hashlib.sha256(p.text.encode()).hexdigest() for p in passages}
    occurrences: Counter[tuple[str, Plane, Role]] = Counter()
    documents: defaultdict[tuple[str, Plane, Role], set[str]] = defaultdict(set)
    seen: set[tuple[str, str, int, int]] = set()
    for hit in result.hits:
        identity = (hit.query_id, hit.passage_id, hit.start, hit.end)
        passage = by_id.get(hit.passage_id)
        query = query_map.get(hit.query_id)
        if passage is None or query is None or identity in seen:
            raise ResearchError("coverage_hit_membership", hit.passage_id)
        seen.add(identity)
        if (
            not 0 <= hit.start < hit.end <= len(passage.text)
            or hit.text_sha256 != hashes[hit.passage_id]
            or hit.expression != passage.text[hit.start : hit.end]
            or hit.context != passage.text[max(0, hit.start - 100) : hit.end + 100]
            or hit.plane != passage.source_plane
            or hit.role != passage.text_role
            or hit.work_id != passage.work_id
            or hit.title != passage.title
            or hit.edition_id != passage.edition_id
            or hit.locator != passage.locator
            or hit.source_url != passage.source_url
            or not any(
                re.fullmatch(re.escape(v), hit.expression, re.IGNORECASE) for v in query.variants
            )
            or (hit.start > 0 and re.match(r"\w", passage.text[hit.start - 1]))
            or (hit.end < len(passage.text) and re.match(r"\w", passage.text[hit.end]))
        ):
            raise ResearchError("coverage_hit_binding", hit.passage_id)
        key = (hit.query_id, hit.plane, hit.role)
        occurrences[key] += 1
        documents[key].add(hit.passage_id)
    expected = {(q.query_id, plane, role) for q in queries for plane in Plane for role in Role}
    keys = [(r.query_id, r.plane, r.role) for r in result.rows]
    if len(keys) != len(set(keys)) or set(keys) != expected:
        raise ResearchError(
            "coverage_cells", "The query/plane/role grid must be complete and unique"
        )
    cells: list[CoverageCell] = []
    for row in result.rows:
        key = (row.query_id, row.plane, row.role)
        total = source_counts[(row.plane, row.role)]
        matched = len(documents[key])
        if row.occurrences != occurrences[key] or row.matched_source_documents != matched:
            raise ResearchError("coverage_aggregate", row.query_id)
        cells.append(
            CoverageCell(
                query_id=row.query_id,
                plane=row.plane,
                role=row.role,
                occurrences=row.occurrences,
                matched_source_documents=matched,
                source_units=total,
                coverage_fraction=matched / total if total else None,
            )
        )
    return tuple(cells)
