# Copyright (c) 2026 Daniel Ari Friedman
"""Real source-run and policy controls for the thin private planning adapter."""

import csv
import io
import json
from dataclasses import dataclass
from pathlib import Path

import pytest
from blake.methods.models import EvidenceError
from blake.methods.review_batches import publish_review_batch
from blake.methods.review_planning_models import ReviewPlanSpec, ReviewSelection
from blake.methods.runs import digest
from blake.studies import StudyHit
from pydantic import ValidationError

from blakean_federalism.evidence_review_models import EvidenceDecision, PoliticalReadingDecision
from blakean_federalism.review_planning import (
    PinnedReviewBatch,
    PinnedReviewFile,
    ReviewPlanningRequest,
    ReviewScope,
    load_planning_input,
    publish_planning_request,
    scope_hits,
    verify_planning_request,
)

from .test_evidence_review import candidate as original_review_run

# Export the reused real pytest fixture for module-level discovery.
__all__ = ["original_review_run"]


@dataclass(frozen=True, slots=True)
class PlanningFixture:
    root: Path
    directory: Path
    sha256: str
    hits: tuple[StudyHit, ...]


@pytest.fixture
def planning(original_review_run, tmp_path, monkeypatch) -> PlanningFixture:
    # Given the existing real synthetic original-run workflow.
    monkeypatch.chdir(tmp_path)
    directory, pin, hits, _receipt, _imported, _queries = original_review_run
    # Then planning starts from verified original candidates, never a mocked loader.
    return PlanningFixture(tmp_path, directory, pin, hits)


def request_for(
    fixture: PlanningFixture,
    scope: ReviewScope = ReviewScope.BLAKE_PRIMARY_READING,
    decisions: PinnedReviewFile | None = None,
) -> ReviewPlanningRequest:
    return ReviewPlanningRequest(
        source_run=fixture.directory,
        source_run_sha256=fixture.sha256,
        decisions=decisions,
        scope=scope,
        selection=ReviewSelection(
            target_size=25,
            seed="synthetic-policy-v1",
            strata_fields=("term_id", "source_plane", "text_role"),
            unit_field="text_sha256",
            max_per_unit=1,
        ),
    )


def bind_request(fixture: PlanningFixture, request: ReviewPlanningRequest) -> PinnedReviewFile:
    path = fixture.root / "request.json"
    path.write_text(request.model_dump_json(indent=2) + "\n")
    return PinnedReviewFile(path=path, sha256=digest(path.read_bytes()))


def authored_file(fixture: PlanningFixture, hits: tuple[StudyHit, ...]) -> PinnedReviewFile:
    path = fixture.root / "decisions.jsonl"
    decisions = tuple(
        EvidenceDecision(
            run_sha256=fixture.sha256,
            hit_id=hit.hit_id,
            decision=PoliticalReadingDecision.UNCERTAIN,
            reviewer="Synthetic reader",
            rationale="Synthetic policy control, not a literary judgment",
        )
        for hit in hits
    )
    path.write_text("".join(item.model_dump_json() + "\n" for item in decisions))
    return PinnedReviewFile(path=path, sha256=digest(path.read_bytes()))


def test_plans_blank_queue_without_creating_authored_decisions(planning) -> None:
    # Given a pinned request over the original synthetic source run.
    source = bind_request(planning, request_for(planning))
    original = (planning.directory / "run.json").read_bytes()
    output = planning.root / "analysis_output/batch"
    # When the application delegates publication and full verification.
    receipt = publish_planning_request(source, output)
    verified = verify_planning_request(
        source,
        PinnedReviewBatch(
            directory=output, receipt_sha256=digest((output / "run.json").read_bytes())
        ),
    )
    # Then selection remains blank work and every original byte/producer remains intact.
    assert verified.receipt == receipt
    assert verified.plan.spec.source_context_sha256 == source.sha256
    assert verified.plan.shortfall == 25 - verified.plan.selected_hits
    assert (planning.directory / "run.json").read_bytes() == original
    with (output / "review-queue.csv").open(newline="") as stream:
        rows = tuple(csv.DictReader(stream))
    assert len(rows) == verified.plan.selected_hits
    assert all(
        row[key] == ""
        for row in rows
        for key in ("decision", "reviewer", "rationale", "verification_locator")
    )
    assert not (output / "decisions.jsonl").exists()


def test_global_decisions_are_validated_then_scoped(planning) -> None:
    # Given one primary and one explicitly exploratory authored fixture decision.
    primary = next(hit for hit in planning.hits if hit.text_role == "primary")
    editorial = next(hit for hit in planning.hits if hit.text_role == "editorial")
    decisions = authored_file(planning, (primary, editorial))
    source = bind_request(planning, request_for(planning, decisions=decisions))
    # When the application derives its source pool and exclusion policy.
    context = load_planning_input(source)
    # Then global and scoped review counts remain distinct.
    assert context.global_reviewed == 2
    assert context.scoped_reviewed == 1
    assert context.spec.excluded_hit_ids == (primary.hit_id,)
    assert editorial.hit_id not in {hit.hit_id for hit in context.hits}
    receipt = publish_planning_request(source, planning.root / "analysis_output/scoped-batch")
    assert receipt.candidate_hits == context.scoped_candidates


def test_all_source_request_retains_global_roles_and_decisions(planning) -> None:
    # Given a pinned editorial decision and explicitly declared all-source scope.
    editorial = next(hit for hit in planning.hits if hit.text_role == "editorial")
    decisions = authored_file(planning, (editorial,))
    source = bind_request(planning, request_for(planning, ReviewScope.ALL_SOURCES, decisions))
    # When the request is admitted.
    context = load_planning_input(source)
    # Then all original facets and global exclusions remain in the scoped pool.
    assert context.hits == planning.hits
    assert context.global_reviewed == context.scoped_reviewed == 1
    assert context.spec.excluded_hit_ids == (editorial.hit_id,)


@pytest.mark.parametrize("failure", ["unknown", "duplicate", "wrong-run", "rationale", "locator"])
def test_invalid_out_of_scope_decision_cannot_be_hidden(planning, failure) -> None:
    # Given a malformed authored decision on an editorial, out-of-scope candidate.
    editorial = next(hit for hit in planning.hits if hit.text_role == "editorial")
    source = authored_file(planning, (editorial,))
    rows = [json.loads(line) for line in source.path.read_text().splitlines()]
    match failure:
        case "unknown":
            rows[0]["hit_id"] = "0" * 64
        case "duplicate":
            rows.append(rows[0])
        case "wrong-run":
            rows[0]["run_sha256"] = "0" * 64
        case "rationale":
            rows[0]["rationale"] = " "
        case "locator":
            rows[0]["decision"] = "textual_support"
            rows[0]["verification_locator"] = ""
    source.path.write_text("".join(json.dumps(row) + "\n" for row in rows))
    pinned = PinnedReviewFile(path=source.path, sha256=digest(source.path.read_bytes()))
    request = bind_request(planning, request_for(planning, decisions=pinned))
    output = planning.root / "analysis_output/rejected"
    # When planning admits the complete original decisions before filtering.
    with pytest.raises((EvidenceError, ValidationError)):
        publish_planning_request(request, output)
    # Then scope cannot launder a globally invalid authored record.
    assert not output.exists()


@pytest.mark.parametrize(
    ("field", "value", "expected"),
    [
        ("blake_primary", False, True),
        ("author_id", "another-author", False),
        ("text_role", "editorial", False),
        ("source_plane", "xml", False),
    ],
)
def test_primary_policy_uses_all_source_facets_not_boolean(
    planning, field, value, expected
) -> None:
    # Given an ordinarily validated single witness with an isolated flag/source contrast.
    original = next(hit for hit in planning.hits if hit.text_role == "primary")
    data = original.model_dump(mode="json")
    data[field] = value
    hit = StudyHit.model_validate(data)
    # When primary reading eligibility is selected.
    selected = scope_hits((hit,), ReviewScope.BLAKE_PRIMARY_READING)
    # Then the three source facets decide eligibility without repairing the flag.
    assert bool(selected) is expected
    assert scope_hits((hit,), ReviewScope.ALL_SOURCES) == (hit,)


def test_pinned_csv_preserves_blank_and_global_decisions(planning) -> None:
    # Given the original full blank queue with one editorial authored disposition.
    rows = list(csv.DictReader(io.StringIO((planning.directory / "review-queue.csv").read_text())))
    editorial = next(hit for hit in planning.hits if hit.text_role == "editorial")
    for row in rows:
        if row["hit_id"] == editorial.hit_id:
            row.update(decision="uncertain", reviewer="Synthetic reader", rationale="Synthetic")
    path = planning.root / "authored.csv"
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    pin = PinnedReviewFile(path=path, sha256=digest(path.read_bytes()))
    request = bind_request(planning, request_for(planning, decisions=pin))
    # When the private CSV policy validates the complete authored input.
    context = load_planning_input(request)
    # Then omitted records stay unreviewed and out-of-scope decisions stay visible globally.
    assert context.global_reviewed == 1
    assert context.scoped_reviewed == 0


@pytest.mark.parametrize("change", ["selection", "exclusions", "source-run"])
def test_valid_batch_cannot_forge_a_request_policy(planning, change) -> None:
    # Given a legitimate core batch carrying the same context hash but another valid spec.
    source = bind_request(planning, request_for(planning))
    context = load_planning_input(source)
    data = context.spec.model_dump(mode="json")
    match change:
        case "selection":
            data["selection"]["seed"] = "different-valid-seed"
        case "exclusions":
            data["excluded_hit_ids"] = [context.hits[0].hit_id]
        case "source-run":
            data["source_run_sha256"] = "0" * 64
    spec = ReviewPlanSpec.model_validate_json(json.dumps(data))
    output = planning.root / "analysis_output/forged-policy"
    publish_review_batch(context.hits, spec, output)
    batch = PinnedReviewBatch(
        directory=output, receipt_sha256=digest((output / "run.json").read_bytes())
    )
    # When the application independently rederives the complete expected spec.
    with pytest.raises(EvidenceError, match="review_planning_request_mismatch"):
        verify_planning_request(source, batch)
    # Then matching a stored context string alone cannot authorize another policy.


@pytest.mark.parametrize("location", ["outside", "overlap", "occupied"])
def test_private_output_cannot_escape_or_replace_source(planning, location) -> None:
    # Given one valid independently pinned source request.
    source = bind_request(planning, request_for(planning))
    output = planning.root / "analysis_output/batch"
    match location:
        case "outside":
            output = planning.root / "public"
        case "overlap":
            output = planning.directory / "child"
        case "occupied":
            publish_planning_request(source, output)
    before = (planning.directory / "run.json").read_bytes()
    # When the private publication boundary is violated.
    with pytest.raises((EvidenceError, FileExistsError)):
        publish_planning_request(source, output)
    # Then the source completion marker is unchanged.
    assert (planning.directory / "run.json").read_bytes() == before
