# Copyright (c) 2026 Daniel Ari Friedman
"""Immutable, explicitly authored political readings of source-bound retrieval leads."""

import csv
import io
import json
from pathlib import Path
from typing import Final

from blake.methods.annotations import (
    ReviewQueueRow,
    count_decisions,
    csv_decisions,
    queue_row,
    validate_decision_membership,
)
from blake.methods.concordance import concordance_passages, query_fingerprint
from blake.methods.corpus import load_import
from blake.methods.models import EvidenceError
from blake.methods.producer import SourceBinding, source_binding_sha256
from blake.methods.runs import (
    digest,
    read_regular,
    require_run_pin,
    reserve,
    safe_directory,
    verify_artifacts,
    write_new,
)
from blake.studies import StudyHit
from pydantic import TypeAdapter

from .evidence_review_models import (
    CandidateSummary,
    EvidenceDecision,
    EvidenceReviewSummary,
    EvidenceRun,
    PoliticalReadingDecision,
    ReviewReceipt,
)
from .models import CorpusPin, Hit, Passage, QuerySpec

HITS: Final = TypeAdapter(tuple[StudyHit, ...])
LABELS: Final = tuple(choice.value for choice in PoliticalReadingDecision)


def producer_sha256() -> str:
    """Bind private policy and the transitive shared retrieval/review implementation."""
    return source_binding_sha256(
        (
            SourceBinding(
                "blakean_federalism",
                (
                    "__init__.py",
                    "models.py",
                    "evidence_review.py",
                    "evidence_review_models.py",
                    "cli_evidence_review.py",
                ),
            ),
            SourceBinding(
                "blake",
                (
                    "__init__.py",
                    "version.py",
                    "studies.py",
                    "text_search/__init__.py",
                    "text_search/models.py",
                    "text_search/normalize.py",
                    "text_search/index.py",
                    "text_search/vocabulary.py",
                    "methods/__init__.py",
                    "methods/models.py",
                    "methods/common.py",
                    "methods/projection_models.py",
                    "methods/bundle_models.py",
                    "methods/profiles.py",
                    "methods/concordance.py",
                    "methods/corpus.py",
                    "methods/storage.py",
                    "methods/annotations.py",
                    "methods/runs.py",
                    "methods/producer.py",
                ),
            ),
        )
    )


def private_output(output: Path, source: Path) -> None:
    """Keep full contexts private and prevent writing into the source custody tree."""
    safe_directory(output)
    target = output.resolve()
    private = (Path.cwd() / "analysis_output").resolve()
    origin = source.resolve()
    if target == private or not target.is_relative_to(private):
        raise EvidenceError("private_review_output", str(output))
    if target.is_relative_to(origin) or origin.is_relative_to(target):
        raise EvidenceError("overlapping_output", str(output))


def adapt_hit(hit: Hit, passage: Passage, query_sha256: str) -> StudyHit:
    """Preserve original source metadata; never promote editorial or XML candidates."""
    identity = digest(
        json.dumps(
            [query_sha256, hit.query_id, hit.passage_id, hit.text_sha256, hit.start, hit.end],
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode()
    )
    return StudyHit.model_validate(
        {
            "hit_id": identity,
            "term_id": hit.query_id,
            "group": "political_reading",
            "passage_id": hit.passage_id,
            "work_id": hit.work_id,
            "title": hit.title,
            "edition_id": hit.edition_id,
            "copy_id": passage.copy_id,
            "locator": hit.locator,
            "source_url": hit.source_url,
            "rights": passage.rights,
            "author_id": passage.author_id,
            "text_role": hit.role.value,
            "source_plane": hit.plane.value,
            "source_sha256": passage.source_sha256,
            "text_sha256": hit.text_sha256,
            "start": hit.start,
            "end": hit.end,
            "expression": hit.expression,
            "context": hit.context,
            "blake_primary": (
                passage.author_id == "william-blake-1757-1827"
                and hit.role.value == "primary"
                and hit.plane.value == "reading"
            ),
        }
    )


def _queue_bytes(hits: tuple[StudyHit, ...]) -> bytes:
    queue = io.StringIO(newline="")
    writer = csv.DictWriter(queue, fieldnames=list(ReviewQueueRow.__annotations__))
    writer.writeheader()
    writer.writerows(queue_row(hit) for hit in hits)
    return queue.getvalue().encode()


def prepare_review(
    corpus: Path,
    pin: CorpusPin,
    queries: tuple[QuerySpec, ...],
    output: Path,
) -> EvidenceRun:
    """Verify source bytes, retrieve candidates and publish a completion receipt last."""
    private_output(output, corpus)
    _, passages = load_import(corpus, pin)
    result = concordance_passages(
        passages, queries, pin, "Retrieval leads awaiting authored review."
    )
    by_id = {p.passage_id: p for p in passages}
    hits = tuple(adapt_hit(h, by_id[h.passage_id], result.query_sha256) for h in result.hits)
    summary = CandidateSummary(
        query_sha256=result.query_sha256,
        candidate_hits=len(hits),
        blake_primary_hits=sum(h.blake_primary for h in hits),
        exploratory_hits=sum(not h.blake_primary for h in hits),
        scanned_source_units=len(passages),
    )
    # Reverify consumed source immediately before publishing private candidate contexts.
    _, checked = load_import(corpus, pin)
    if checked != passages:
        raise EvidenceError("review_source_changed", str(corpus))
    producer = producer_sha256()
    reserve(output)
    artifacts = (
        write_new(
            output / "hits.jsonl", "".join(h.model_dump_json() + "\n" for h in hits).encode()
        ),
        write_new(output / "summary.json", (summary.model_dump_json(indent=2) + "\n").encode()),
        write_new(output / "review-queue.csv", _queue_bytes(hits)),
    )
    receipt = EvidenceRun(
        producer_sha256=producer,
        corpus_pin=pin,
        queries=queries,
        query_sha256=result.query_sha256,
        files=artifacts,
    )
    _ = write_new(output / "run.json", (receipt.model_dump_json(indent=2) + "\n").encode())
    return receipt


def load_review_run(run: Path, run_sha256: str) -> tuple[EvidenceRun, tuple[StudyHit, ...]]:
    """Verify exact historical run bytes, artifact membership and candidate totals."""
    receipt = EvidenceRun.model_validate_json(require_run_pin(run, run_sha256))
    payloads = verify_artifacts(
        run, receipt.files, {"hits.jsonl", "summary.json", "review-queue.csv"}
    )
    hits = HITS.validate_python(
        [json.loads(line) for line in payloads["hits.jsonl"].splitlines() if line.strip()]
    )
    summary = CandidateSummary.model_validate_json(payloads["summary.json"])
    expected_queries = {q.query_id for q in receipt.queries}
    if (
        receipt.query_sha256 != query_fingerprint(receipt.queries)
        or summary.query_sha256 != receipt.query_sha256
        or summary.candidate_hits != len(hits)
        or summary.blake_primary_hits != sum(h.blake_primary for h in hits)
        or summary.exploratory_hits != sum(not h.blake_primary for h in hits)
        or len({h.hit_id for h in hits}) != len(hits)
        or any(h.term_id not in expected_queries for h in hits)
    ):
        raise EvidenceError("review_result_membership", str(run))
    if payloads["review-queue.csv"] != _queue_bytes(hits):
        raise EvidenceError("review_queue_changed", str(run))
    return receipt, hits


def review_evidence(
    run: Path,
    run_sha256: str,
    decisions: Path,
    output: Path,
) -> EvidenceReviewSummary:
    """Retain authored bytes and complete decisions; omissions stay explicitly unreviewed."""
    private_output(output, run)
    candidate_run, hits = load_review_run(run, run_sha256)
    raw = read_regular(decisions, "decisions")
    if decisions.suffix.casefold() == ".csv":
        parsed = tuple(
            EvidenceDecision.model_validate(d.model_dump())
            for d in csv_decisions(raw, hits, run_sha256)
        )
    elif decisions.suffix.casefold() == ".jsonl":
        parsed = tuple(
            EvidenceDecision.model_validate_json(line) for line in raw.splitlines() if line.strip()
        )
    else:
        raise EvidenceError("decision_format", "Use authored CSV or JSONL")
    validate_decision_membership(parsed, hits, run_sha256)
    by_id = {h.hit_id: h for h in hits}
    primary = tuple(d for d in parsed if by_id[d.hit_id].blake_primary)
    exploratory = tuple(d for d in parsed if not by_id[d.hit_id].blake_primary)
    summary = EvidenceReviewSummary(
        run_sha256=run_sha256,
        candidate_producer_sha256=candidate_run.producer_sha256,
        decisions_sha256=digest(raw),
        producer_sha256=producer_sha256(),
        all_candidates=count_decisions(parsed, len(hits), LABELS),
        blake_primary=count_decisions(primary, sum(h.blake_primary for h in hits), LABELS),
        exploratory=count_decisions(exploratory, sum(not h.blake_primary for h in hits), LABELS),
    )
    reserve(output)
    artifacts = (
        write_new(output / ("authored" + decisions.suffix.casefold()), raw),
        write_new(
            output / "decisions.jsonl", "".join(d.model_dump_json() + "\n" for d in parsed).encode()
        ),
        write_new(output / "summary.json", (summary.model_dump_json(indent=2) + "\n").encode()),
    )
    receipt = ReviewReceipt(
        source_run_sha256=run_sha256,
        candidate_producer_sha256=candidate_run.producer_sha256,
        decisions_sha256=digest(raw),
        producer_sha256=summary.producer_sha256,
        files=artifacts,
    )
    _ = write_new(output / "run.json", (receipt.model_dump_json(indent=2) + "\n").encode())
    return summary
