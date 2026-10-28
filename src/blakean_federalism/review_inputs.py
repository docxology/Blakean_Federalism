# Copyright (c) 2026 Daniel Ari Friedman
"""One baseline-assessment boundary for review audits and procedural comparisons."""

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from pydantic import TypeAdapter

from .institutional_review import ReviewReport, audit_review
from .institutional_review_models import ReviewStudy
from .institutions import assess
from .models import Assessment, Decision, ResearchError
from .storage import safe_path


@dataclass(frozen=True, slots=True)
class ValidatedReviewAudit:
    """Parsed review inputs with their assessed baseline linkages."""

    report: ReviewReport
    review_bytes: bytes
    baseline_bytes: bytes
    assessments: tuple[Assessment, ...]
    baseline_decision_count: int


def linked_assessments(
    study: ReviewStudy, decisions: tuple[Decision, ...]
) -> tuple[Assessment, ...]:
    """Require unique existing baseline identities and admissible linked decisions."""
    indexed = {decision.decision_id: decision for decision in decisions}
    if len(indexed) != len(decisions):
        raise ResearchError("duplicate_baseline_decision", "baseline decision IDs must be unique")
    linked = sorted({procedure.baseline_decision_id for procedure in study.procedures})
    results: list[Assessment] = []
    for identifier in linked:
        if identifier not in indexed:
            raise ResearchError("missing_baseline_decision", identifier)
        result = assess(indexed[identifier])
        if not result.admissible_under_proposed_rules:
            raise ResearchError("inadmissible_baseline_decision", identifier)
        results.append(result)
    return tuple(results)


def validated_report(cases: Path, decisions: Path, output: Path) -> ValidatedReviewAudit:
    """Finish all input and destination checks before creating an output directory."""
    if output.exists() or output.is_symlink():
        raise ResearchError("occupied_output", str(output))
    destination = output.resolve()
    for source in (cases, decisions):
        resolved = source.resolve()
        if resolved == destination or destination in resolved.parents:
            raise ResearchError("input_inside_output", str(source))
    cases_bytes = safe_path(cases.parent, cases.name).read_bytes()
    baseline_bytes = safe_path(decisions.parent, decisions.name).read_bytes()
    study = ReviewStudy.model_validate_json(cases_bytes)
    if sha256(baseline_bytes).hexdigest() != study.baseline_decisions_sha256:
        raise ResearchError("baseline_hash_mismatch", "decision bytes differ from review study")
    parsed_decisions = TypeAdapter(tuple[Decision, ...]).validate_json(baseline_bytes)
    assessments = linked_assessments(study, parsed_decisions)
    return ValidatedReviewAudit(
        audit_review(study), cases_bytes, baseline_bytes, assessments, len(parsed_decisions)
    )
