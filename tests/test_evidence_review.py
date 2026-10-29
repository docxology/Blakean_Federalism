# Copyright (c) 2026 Daniel Ari Friedman
"""Real-file authored review controls over invented source passages."""

import csv
import io
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import typer
from blake.methods.concordance import concordance_passages
from blake.methods.corpus import load_import
from blake.methods.models import EvidenceError
from blake.methods.runs import digest
from pydantic import ValidationError
from typer.testing import CliRunner

from blakean_federalism import evidence_review
from blakean_federalism.cli_evidence_review import register_review_commands
from blakean_federalism.corpus import import_corpus
from blakean_federalism.evidence_review import (
    adapt_hit,
    load_review_run,
    prepare_review,
    review_evidence,
)
from blakean_federalism.models import QuerySpec


@pytest.fixture
def candidate(captured, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    source, _, pin, imported, _ = captured
    import_corpus(source, imported, pin)
    queries = (QuerySpec(query_id="test", variants=("state",), note="Synthetic fixture"),)
    run = tmp_path / "analysis_output/candidates"
    receipt = prepare_review(imported, pin, queries, run)
    run_pin = digest((run / "run.json").read_bytes())
    _, hits = load_review_run(run, run_pin)
    return run, run_pin, hits, receipt, imported, queries


def decision(run_pin, hit, label="textual_support"):
    return dict(
        run_sha256=run_pin,
        hit_id=hit.hit_id,
        decision=label,
        reviewer="Fixture reader",
        rationale="Synthetic contextual reading",
        verification_locator="Synthetic plate 32",
    )


def authored(tmp_path, rows):
    path = tmp_path / "authored.jsonl"
    path.write_text("".join(json.dumps(row) + "\n" for row in rows))
    return path


def test_review_preserves_authorship_source_and_unreviewed(candidate, tmp_path):
    run, run_pin, hits, _, _, _ = candidate
    path = authored(tmp_path, [decision(run_pin, hits[0])])
    output = tmp_path / "analysis_output/review"
    summary = review_evidence(run, run_pin, path, output)
    assert summary.all_candidates.reviewed_hits == 1
    assert summary.all_candidates.unreviewed_hits == len(hits) - 1
    assert summary.blake_primary.reviewed_hits == 1
    assert summary.exploratory.reviewed_hits == 0
    assert (output / "authored.jsonl").read_bytes() == path.read_bytes()
    assert (output / "run.json").is_file()
    assert any(h.text_role == "editorial" and not h.blake_primary for h in hits)


def test_csv_unchanged_candidates_and_blank_rows_remain_unreviewed(candidate, tmp_path):
    run, run_pin, hits, _, _, _ = candidate
    reader = csv.DictReader(io.StringIO((run / "review-queue.csv").read_text()))
    rows = list(reader)
    rows[0].update(decision="uncertain", reviewer="Fixture", rationale="Needs further reading")
    path = tmp_path / "authored.csv"
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    summary = review_evidence(run, run_pin, path, tmp_path / "analysis_output/csv-review")
    assert summary.all_candidates.decisions["uncertain"] == 1
    assert summary.all_candidates.unreviewed_hits == len(hits) - 1


@pytest.mark.parametrize(
    "change",
    [
        {"run_sha256": "0" * 64},
        {"hit_id": "0" * 64},
        {"reviewer": " "},
        {"rationale": " "},
        {"verification_locator": " "},
        {"decision": "imagined"},
    ],
)
def test_invalid_authored_decisions_fail_before_publication(candidate, tmp_path, change):
    run, run_pin, hits, _, _, _ = candidate
    path = authored(tmp_path, [decision(run_pin, hits[0]) | change])
    output = tmp_path / "analysis_output/rejected"
    with pytest.raises((EvidenceError, ValidationError)):
        review_evidence(run, run_pin, path, output)
    assert not output.exists()


def test_duplicate_decisions_and_wrong_completion_pin_are_rejected(candidate, tmp_path):
    run, run_pin, hits, _, _, _ = candidate
    path = authored(tmp_path, [decision(run_pin, hits[0])] * 2)
    with pytest.raises(EvidenceError, match="unknown_or_duplicate_hit"):
        review_evidence(run, run_pin, path, tmp_path / "analysis_output/duplicate")
    with pytest.raises(EvidenceError, match="review_run_pin"):
        review_evidence(run, "0" * 64, path, tmp_path / "analysis_output/wrong-pin")


@pytest.mark.parametrize("name", ["hits.jsonl", "summary.json", "review-queue.csv"])
def test_corrupt_run_artifacts_fail(candidate, tmp_path, name):
    run, run_pin, hits, _, _, _ = candidate
    with (run / name).open("ab") as stream:
        stream.write(b"corrupt")
    path = authored(tmp_path, [decision(run_pin, hits[0])])
    with pytest.raises(EvidenceError, match="artifact_checksum"):
        review_evidence(run, run_pin, path, tmp_path / "analysis_output/corrupt")


def test_csv_changed_context_is_rejected(candidate, tmp_path):
    run, run_pin, _, _, _, _ = candidate
    raw = (run / "review-queue.csv").read_text().replace("States change", "Altered evidence")
    path = tmp_path / "changed.csv"
    path.write_text(raw)
    with pytest.raises(EvidenceError, match="csv_candidate_changed"):
        review_evidence(run, run_pin, path, tmp_path / "analysis_output/changed")


def test_output_cannot_escape_private_root_or_overwrite(candidate, tmp_path):
    run, run_pin, _, receipt, imported, queries = candidate
    with pytest.raises(EvidenceError, match="private_review_output"):
        prepare_review(imported, receipt.corpus_pin, queries, tmp_path / "public")
    before = (run / "run.json").read_bytes()
    with pytest.raises(FileExistsError):
        prepare_review(imported, receipt.corpus_pin, queries, run)
    assert (run / "run.json").read_bytes() == before
    path = authored(tmp_path, [])
    output = tmp_path / "analysis_output/empty-review"
    review_evidence(run, run_pin, path, output)
    with pytest.raises(FileExistsError):
        review_evidence(run, run_pin, path, output)


def test_cli_prepares_and_reviews_real_files(candidate, tmp_path):
    _, _, _, receipt, imported, queries = candidate
    app = typer.Typer()
    register_review_commands(app)
    pin_path = tmp_path / "pin.json"
    pin_path.write_text(receipt.corpus_pin.model_dump_json())
    query_path = tmp_path / "queries.json"
    query_path.write_text(json.dumps([q.model_dump() for q in queries]))
    run = tmp_path / "analysis_output/cli-candidates"
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "prepare-evidence-review",
            "--corpus",
            str(imported),
            "--pin",
            str(pin_path),
            "--queries",
            str(query_path),
            "--output",
            str(run),
        ],
    )
    assert result.exit_code == 0, result.output
    run_pin = digest((run / "run.json").read_bytes())
    path = authored(tmp_path, [])
    output = tmp_path / "analysis_output/cli-review"
    result = runner.invoke(
        app,
        [
            "review-evidence",
            "--run",
            str(run),
            "--run-sha256",
            run_pin,
            "--decisions",
            str(path),
            "--output",
            str(output),
        ],
    )
    assert result.exit_code == 0, result.output
    assert json.loads((output / "summary.json").read_text())["all_candidates"]["reviewed_hits"] == 0


def rebind(run, name, raw):
    """Supply a new external receipt pin to exercise semantic checks beyond hashes."""
    (run / name).write_bytes(raw)
    receipt = json.loads((run / "run.json").read_text())
    for entry in receipt["files"]:
        if entry["name"] == name:
            entry["size"] = len(raw)
            entry["sha256"] = digest(raw)
    (run / "run.json").write_text(json.dumps(receipt))
    return digest((run / "run.json").read_bytes())


def test_rebound_false_summary_is_rejected(candidate):
    run, _, _, _, _, _ = candidate
    data = json.loads((run / "summary.json").read_text())
    data["candidate_hits"] = 99
    pin = rebind(run, "summary.json", json.dumps(data).encode())
    with pytest.raises(EvidenceError, match="review_result_membership"):
        load_review_run(run, pin)


@pytest.mark.parametrize("boundary", ["require_run_pin", "verify_artifacts"])
def test_parse_checked_bytes_after_concurrent_receipt_or_payload_mutation(candidate, boundary):
    run, run_pin, hits, receipt, _, _ = candidate
    target = run / ("run.json" if boundary == "require_run_pin" else "summary.json")
    replacement = json.loads(target.read_text())
    if boundary == "require_run_pin":
        replacement["corpus_pin"]["upstream_commit"] = "different-corpus-identity"
    else:
        replacement["candidate_hits"] = 99
    changed = []

    def schedule(frame, event, _argument) -> None:
        if event == "return" and frame.f_code.co_name == boundary and not changed:
            target.write_text(json.dumps(replacement))
            changed.append(target)

    previous = sys.getprofile()
    sys.setprofile(schedule)
    try:
        actual_receipt, actual_hits = load_review_run(run, run_pin)
    finally:
        sys.setprofile(previous)
    assert changed == [target]
    assert actual_receipt == receipt
    assert actual_hits == hits
    with pytest.raises(EvidenceError):
        load_review_run(run, run_pin)


def test_rebound_truncated_queue_is_rejected(candidate):
    run, _, _, _, _, _ = candidate
    raw = (run / "review-queue.csv").read_bytes().splitlines(keepends=True)[0]
    pin = rebind(run, "review-queue.csv", raw)
    with pytest.raises(EvidenceError, match="review_queue_changed"):
        load_review_run(run, pin)


@pytest.mark.parametrize("label", ["counterreading", "nonpolitical", "uncertain"])
def test_private_decision_labels_do_not_promote_exploratory_hits(candidate, tmp_path, label):
    run, run_pin, hits, _, _, _ = candidate
    hit = next(h for h in hits if not h.blake_primary)
    path = authored(tmp_path, [decision(run_pin, hit, label)])
    summary = review_evidence(run, run_pin, path, tmp_path / "analysis_output/label")
    assert summary.exploratory.decisions[label] == 1
    assert summary.blake_primary.reviewed_hits == 0


def test_unknown_format_symlink_and_overlapping_output_are_rejected(candidate, tmp_path):
    run, run_pin, _, _, _, _ = candidate
    unknown = tmp_path / "input.txt"
    unknown.write_text("")
    with pytest.raises(EvidenceError, match="decision_format"):
        review_evidence(run, run_pin, unknown, tmp_path / "analysis_output/unknown")
    link = tmp_path / "input.jsonl"
    link.symlink_to(unknown)
    with pytest.raises(EvidenceError, match="symlink_decisions"):
        review_evidence(run, run_pin, link, tmp_path / "analysis_output/link")
    with pytest.raises(EvidenceError, match="overlapping_output"):
        review_evidence(run, run_pin, unknown, run / "nested")


def test_zero_candidate_run_is_explicit(candidate, tmp_path):
    _, _, _, receipt, imported, _ = candidate
    empty = (QuerySpec(query_id="absent", variants=("zzzxqv",), note="Negative control"),)
    run = tmp_path / "analysis_output/no-hits"
    prepare_review(imported, receipt.corpus_pin, empty, run)
    pin = digest((run / "run.json").read_bytes())
    path = authored(tmp_path, [])
    summary = review_evidence(run, pin, path, tmp_path / "analysis_output/no-hits-review")
    assert summary.all_candidates.candidate_hits == 0
    assert summary.all_candidates.unreviewed_hits == 0


def test_adapter_retains_source_hash_without_promoting_other_author(candidate):

    _, _, _, receipt, imported, queries = candidate
    _, passages = load_import(imported, receipt.corpus_pin)
    passage = passages[0].model_copy(
        update={"author_id": "another-author", "source_sha256": "3" * 64}
    )
    result = concordance_passages((passage,), queries, receipt.corpus_pin, "Synthetic")
    hit = adapt_hit(result.hits[0], passage, result.query_sha256)
    assert hit.source_sha256 == "3" * 64
    assert hit.text_role == "primary"
    assert not hit.blake_primary
    assert adapt_hit(result.hits[0], passage, "0" * 64).hit_id != hit.hit_id


def test_historical_queue_survives_a_real_producer_version_change(candidate, tmp_path):
    run, run_pin, _, receipt, _, _ = candidate
    source = tmp_path / "replay-source"
    package = source / "blakean_federalism"
    shutil.copytree(Path(evidence_review.__file__).parent, package)
    with (package / "__init__.py").open("a") as stream:
        stream.write('\n__version__ += ".historical-control"\n')
    decisions = authored(tmp_path, [])
    output = tmp_path / "analysis_output/historical-review"
    script = (
        "from pathlib import Path; import sys; "
        "from blakean_federalism.evidence_review import review_evidence; "
        "s=review_evidence(Path(sys.argv[1]),sys.argv[2],Path(sys.argv[3]),Path(sys.argv[4])); "
        "print(s.model_dump_json())"
    )
    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(source) + os.pathsep + environment.get("PYTHONPATH", "")
    result = subprocess.run(  # noqa: S603 -- Fixed code and explicitly owned fixture argv; no shell.
        [sys.executable, "-B", "-c", script, str(run), run_pin, str(decisions), str(output)],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    summary = json.loads(result.stdout)
    assert summary["candidate_producer_sha256"] == receipt.producer_sha256
    assert summary["producer_sha256"] != receipt.producer_sha256
    assert summary["all_candidates"]["reviewed_hits"] == 0
    assert digest((run / "run.json").read_bytes()) == run_pin
