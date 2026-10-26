# Copyright (c) 2026 Daniel Ari Friedman
"""Analyze word retrieval with explicit copy, work and denominator sensitivity."""

import hashlib
import json
import re
from collections import Counter, defaultdict
from statistics import fmean

from ._corpus_statistics_core import associations, measure, stratify
from .corpus import query_fingerprint
from .corpus_statistics_models import (
    CorpusStatistics,
    DuplicateGroup,
    Omission,
    QuerySummary,
    SourceCensus,
    SourceUnit,
)
from .models import Passage, QuerySpec, ResearchError, Role


def _inventory(
    passages: tuple[Passage, ...],
    queries: tuple[QuerySpec, ...],
) -> tuple[SourceUnit, ...]:
    patterns = {
        q.query_id: re.compile(
            r"(?<!\w)(?:"
            + "|".join(re.escape(v) for v in sorted(set(q.variants), key=lambda v: (-len(v), v)))
            + r")(?!\w)",
            re.IGNORECASE,
        )
        for q in queries
    }
    return tuple(
        SourceUnit(
            passage_id=p.passage_id,
            work_id=p.work_id,
            title=p.title,
            edition_id=p.edition_id,
            copy_id=p.copy_id,
            text_sha256=hashlib.sha256(p.text.encode()).hexdigest(),
            tokens=len(re.findall(r"\w+", p.text)),
            occurrences={
                q: sum(1 for _ in pattern.finditer(p.text)) for q, pattern in patterns.items()
            },
        )
        for p in passages
        if p.text_role == Role.PRIMARY
    )


def _summarize(
    units: tuple[SourceUnit, ...],
    deduplicated: tuple[SourceUnit, ...],
    query_id: str,
) -> QuerySummary:
    work_ids = sorted({u.work_id for u in units})
    groups = {w: tuple(u for u in units if u.work_id == w) for w in work_ids}
    work_measures = [measure(group, query_id) for group in groups.values()]
    rates = [m.rate_per_10000_tokens for m in work_measures if m.rate_per_10000_tokens is not None]
    raw = measure(units, query_id)
    shares = [m.occurrences / raw.occurrences for m in work_measures] if raw.occurrences else []
    return QuerySummary(
        query_id=query_id,
        copy_retaining=raw,
        exact_text=measure(deduplicated, query_id),
        work_balanced_rate_per_10000_tokens=fmean(rates) if rates else None,
        rate_work_groups=len(rates),
        work_balanced_coverage_fraction=fmean(
            m.matched_units / m.source_units for m in work_measures
        ),
        maximum_work_occurrence_share=max(shares) if shares else None,
        work_occurrence_hhi=sum(v * v for v in shares) if shares else None,
        leave_one_work_out=tuple(
            Omission(
                omitted_work_id=w,
                remaining=measure(tuple(u for u in units if u.work_id != w), query_id),
            )
            for w in work_ids
        ),
    )


def analyze_corpus(
    passages: tuple[Passage, ...],
    queries: tuple[QuerySpec, ...],
) -> CorpusStatistics:
    """Compute descriptive statistics while preserving every supplied source identity.

    Input membership must be unique and queries nonempty. Primary-unit counts are
    computed afresh with the concordance's Unicode whole-word semantics. No stored
    concordance result, optional scientific library or random procedure is used.
    """
    if (
        not passages
        or len({p.passage_id for p in passages}) != len(passages)
        or any(
            not all(v.strip() for v in (p.passage_id, p.work_id, p.edition_id)) for p in passages
        )
        or any(p.copy_id is not None and not p.copy_id.strip() for p in passages)
    ):
        raise ResearchError("statistics_membership", "Provide nonempty, unique source identities")
    if (
        not queries
        or len({q.query_id for q in queries}) != len(queries)
        or any(not q.query_id.strip() for q in queries)
    ):
        raise ResearchError("statistics_queries", "Provide nonempty, unique query identifiers")
    if any(not v.strip() for q in queries for v in q.variants):
        raise ResearchError("empty_variant", "Whitespace cannot define a query")
    ordered = tuple(sorted(passages, key=lambda p: p.passage_id))
    ordered_queries = tuple(sorted(queries, key=lambda q: q.query_id))
    units = _inventory(ordered, ordered_queries)
    if not units:
        raise ResearchError("statistics_primary", "At least one primary reading unit is required")
    census = Counter((p.source_plane, p.text_role) for p in ordered)
    text_groups: defaultdict[str, list[SourceUnit]] = defaultdict(list)
    for unit in units:
        text_groups[unit.text_sha256].append(unit)
    deduplicated = tuple(sorted((g[0] for g in text_groups.values()), key=lambda u: u.passage_id))
    query_ids = tuple(q.query_id for q in ordered_queries)
    source_bytes = json.dumps(
        [p.model_dump(mode="json") for p in ordered],
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode()
    return CorpusStatistics(
        source_sha256=hashlib.sha256(source_bytes).hexdigest(),
        query_sha256=query_fingerprint(ordered_queries),
        total_source_units=len(ordered),
        primary_source_units=len(units),
        primary_work_groups=len({u.work_id for u in units}),
        primary_tokens=sum(u.tokens for u in units),
        source_census=tuple(
            SourceCensus(plane=plane, role=role, units=count)
            for (plane, role), count in sorted(census.items())
        ),
        query_specs=ordered_queries,
        units=units,
        deduplicated_passage_ids=tuple(u.passage_id for u in deduplicated),
        exact_duplicate_groups=tuple(
            DuplicateGroup(
                text_sha256=sha,
                passage_ids=tuple(u.passage_id for u in members),
            )
            for sha, members in sorted(text_groups.items())
            if len(members) > 1
        ),
        strata=stratify(units, query_ids),
        queries=tuple(_summarize(units, deduplicated, q) for q in query_ids),
        cooccurrences=(
            associations(units, query_ids, "copy_retaining")
            + associations(deduplicated, query_ids, "exact_text")
            + associations(units, query_ids, "work_presence")
        ),
    )
