# Copyright (c) 2026 Daniel Ari Friedman
"""Real audit processes preserve schema-1 bytes and refuse broken producer/output custody."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from blakean_federalism.models import ResearchError
from blakean_federalism.review_audit_provenance import (
    SIDECAR_NAME,
    ReviewAuditSources,
    review_audit_producers,
    verify_review_producer_receipt,
    write_review_producer_receipt,
)
from blakean_federalism.review_inputs import validated_report
from blakean_federalism.storage import digest

ROOT = Path(__file__).parents[1]
ARCHIVAL_HASHES = {
    # Actual pre-integration schema-1 tool outputs for the unchanged fixed H study.
    "review-report.json": "bb9403142c8abe469d3f9045a02cbc33396982af3008c6123d599d6a0038a779",
    "review-receipt.json": "435f552c822b610bfc5d3eb59ee4b59b93036a058a1a8a3b76c4cc6331825420",
}


@pytest.fixture
def audited(tmp_path):
    cases, decisions, tool = (
        tmp_path / "review.json",
        tmp_path / "decisions.json",
        tmp_path / "audit.py",
    )
    for target, source in (
        (cases, ROOT / "research/institutional-review-cases.json"),
        (decisions, ROOT / "research/cases.json"),
        (tool, ROOT / "tools/audit_institutional_review.py"),
    ):
        target.write_bytes(source.read_bytes())
    output = tmp_path / "audit"
    result = subprocess.run(  # noqa: S603 -- Fixed Python and test-owned source/input paths.
        [
            sys.executable,
            str(tool),
            "--cases",
            str(cases),
            "--decisions",
            str(decisions),
            "--output",
            str(output),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return output, ReviewAuditSources(cases, decisions, tool)


def verify(audited):
    output, sources = audited
    return verify_review_producer_receipt(
        output, sources.cases, sources.decisions, sources.tool, figures=False
    )


def test_real_audit_preserves_old_report_and_receipt_bytes(audited):
    output, _ = audited
    assert {name: digest(output / name) for name in ARCHIVAL_HASHES} == ARCHIVAL_HASHES
    receipt = verify(audited)
    assert receipt.producer_state == "artifacts_complete"
    assert receipt.producer_version == "0.19.0"
    assert "blake/methods/intervals.py" in receipt.producers
    assert "caller/audit_institutional_review.py" in receipt.producers
    assert {p.path for p in receipt.outputs} == set(ARCHIVAL_HASHES)
    assert set(json.loads((output / "review-receipt.json").read_text())) == {
        "schema_version",
        "review_cases_sha256",
        "baseline_decisions_sha256",
        "review_report_sha256",
        "baseline_decision_count",
        "linked_baseline_assessments",
        "procedure_count",
        "claimant_count",
        "declared_conditions_hold_count",
        "unassessed_issue_count",
        "figures",
    }


def test_parent_finalization_reproduces_the_real_child_marker_exactly(audited):
    output, sources = audited
    expected = (output / SIDECAR_NAME).read_bytes()
    (output / SIDECAR_NAME).rename(output.with_name("retained-first-producer-receipt.json"))
    audit = validated_report(sources.cases, sources.decisions, output.with_name("not-created"))
    producers = review_audit_producers(sources.tool, figures=False)
    write_review_producer_receipt(output, audit, producers, sources, figures=False)
    assert (output / SIDECAR_NAME).read_bytes() == expected
    assert verify(audited).producers == producers


@pytest.mark.parametrize("source", ["cases", "decisions", "tool"])
def test_verifier_refuses_changed_actual_inputs_and_caller(audited, source):
    _, sources = audited
    path = getattr(sources, source)
    path.write_bytes(path.read_bytes() + b"\n")
    code = "review_producer_changed" if source == "tool" else "review_input_changed"
    with pytest.raises(ResearchError, match=code):
        verify(audited)


@pytest.mark.parametrize(
    "change", ["report", "missing-output", "duplicate", "subset", "producer", "extra"]
)
def test_verifier_refuses_corrupt_or_incomplete_output_closure(audited, change):
    output, _ = audited
    path = output / SIDECAR_NAME
    data = json.loads(path.read_text())
    match change:
        case "report":
            (output / "review-report.json").write_bytes(b"changed")
        case "missing-output":
            (output / "review-receipt.json").rename(output / "retained-old-receipt.json")
        case "duplicate":
            data["outputs"].append(data["outputs"][0])
        case "subset":
            data["outputs"] = data["outputs"][:1]
        case "producer":
            data["producers"].pop(next(iter(data["producers"])))
        case "extra":
            (output / "unbound.txt").write_bytes(b"retained but unbound")
    path.write_text(json.dumps(data))
    with pytest.raises(ResearchError):
        verify(audited)


def test_missing_sidecar_keeps_archival_bytes_but_refuses_current_acceptance(audited):
    output, _ = audited
    (output / SIDECAR_NAME).rename(output.with_name("preserved-producer-receipt.json"))
    with pytest.raises(ResearchError, match="missing_regular_file"):
        verify(audited)
    assert {name: digest(output / name) for name in ARCHIVAL_HASHES} == ARCHIVAL_HASHES


@pytest.mark.parametrize("change", ["input", "producer"])
def test_final_marker_is_not_written_after_input_or_producer_change(audited, change):
    output, sources = audited
    (output / SIDECAR_NAME).rename(output / "retained-first-producer-receipt.json")
    audit = validated_report(sources.cases, sources.decisions, output.with_name("not-created"))
    producers = review_audit_producers(sources.tool, figures=False)
    if change == "input":
        sources.cases.write_bytes(sources.cases.read_bytes() + b"\n")
    else:
        sources.tool.write_bytes(sources.tool.read_bytes() + b"\n")
    code = "review_input_changed" if change == "input" else "review_producer_changed"
    with pytest.raises(ResearchError, match=code):
        write_review_producer_receipt(output, audit, producers, sources, figures=False)
    assert not (output / SIDECAR_NAME).exists()
