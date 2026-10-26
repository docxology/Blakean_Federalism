# Copyright (c) 2026 Daniel Ari Friedman
"""Real CLI commands use real files rather than mocked collaborators."""

import csv
import json
from contextlib import chdir
from pathlib import Path

import pytest
from pydantic import TypeAdapter
from typer.testing import CliRunner

from blakean_federalism.cli import app, require_ignored
from blakean_federalism.corpus import concordance, import_corpus
from blakean_federalism.models import Concordance, Decision, QuerySpec, ResearchError

from .test_institutions import CASES


def test_cli_import_and_analysis(captured):
    source, _, pin, _, _ = captured
    workspace = source.parent
    (workspace / "research").mkdir()
    (workspace / "research/corpus-pin.json").write_text(pin.model_dump_json())
    (workspace / "research/queries.json").write_text(
        '[{"query_id":"state","variants":["state","states"],"note":"Explicit"}]',
    )
    runner = CliRunner()
    # When real import and analysis commands run, then files contain the known counts.
    with chdir(workspace):
        imported = runner.invoke(
            app,
            [
                "import-corpus",
                "--source",
                str(source),
                "--destination",
                "local_data/corpus",
            ],
        )
        analyzed = runner.invoke(
            app,
            [
                "analyze",
                "--corpus",
                "local_data/corpus",
                "--output",
                "analysis_output/result.json",
            ],
        )
    assert imported.exit_code == 0, imported.output
    assert analyzed.exit_code == 0, analyzed.output
    result = Concordance.model_validate_json(
        (workspace / "analysis_output/result.json").read_bytes()
    )
    assert len(result.hits) == 4


def test_cli_rejects_unignored_payload_output(captured):
    workspace = captured[0].parent
    # When a full concordance targets a tracked path, then it is refused before reading sources.
    with chdir(workspace):
        result = CliRunner().invoke(
            app,
            [
                "analyze",
                "--corpus",
                "absent",
                "--output",
                "research/leak.json",
            ],
        )
    assert result.exit_code != 0
    assert isinstance(result.exception, ResearchError)
    assert not (workspace / "research/leak.json").exists()


def test_cli_empty_cases_are_explicit(tmp_path):
    path = tmp_path / "cases.json"
    path.write_text("[]")
    # When no cases are supplied, then the typed result is empty, with no invented pass.
    with chdir(tmp_path):
        result = CliRunner().invoke(
            app,
            [
                "assess-cases",
                "--cases",
                str(path),
                "--output",
                "analysis_output/empty.json",
            ],
        )
    assert result.exit_code == 0, result.output
    assert json.loads((tmp_path / "analysis_output/empty.json").read_text()) == []


def test_cli_schema_retains_distinct_categories(tmp_path):
    path = tmp_path / "decision.json"
    # When exported, then the schema retains separate subject, role, authority and consequence.
    result = CliRunner().invoke(app, ["export-schemas", "--output", str(path)])
    assert result.exit_code == 0, result.output
    schema = json.loads(path.read_text())
    assert {"subject", "assigned_legal_role", "asserting_authority", "consequence"} <= schema[
        "properties"
    ].keys()


def test_cli_duplicate_case_ids_are_refused(tmp_path):
    path = tmp_path / "cases.json"
    path.write_bytes(TypeAdapter(tuple[Decision, ...]).dump_json((CASES[0], CASES[0])))
    # When decision identities collide, then fail before publishing any result.
    with chdir(tmp_path):
        result = CliRunner().invoke(
            app,
            [
                "assess-cases",
                "--cases",
                str(path),
                "--output",
                "analysis_output/duplicate.json",
            ],
        )
    assert result.exit_code != 0
    assert not (tmp_path / "analysis_output/duplicate.json").exists()


def test_private_output_rejects_normalized_traversal(tmp_path):

    with chdir(tmp_path), pytest.raises(ResearchError, match="private_output"):
        require_ignored(Path("analysis_output/../tracked.json"), "analysis_output")


def test_aggregate_export_excludes_source_payload_fields(captured):
    source, _, pin, dest, _ = captured
    import_corpus(source, dest, pin)
    result = concordance(
        dest, (QuerySpec(query_id="state", variants=("state", "states"), note="Test"),), pin
    )
    payload = source.parent / "private.json"
    payload.write_text(result.model_dump_json())
    output = source.parent / "aggregate.csv"
    invoked = CliRunner().invoke(
        app, ["export-summary", "--concordance-file", str(payload), "--output", str(output)]
    )
    assert invoked.exit_code == 0, invoked.output
    with output.open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert set(rows[0]) == {"query_id", "plane", "role", "occurrences", "matched_source_documents"}
    assert sum(int(row["occurrences"]) for row in rows) == 4


def test_new_statistics_cli_preserves_denominators_and_refuses_overwrite(captured):
    source, _, pin, _, _ = captured
    workspace = source.parent
    (workspace / "research").mkdir()
    (workspace / "research/corpus-pin.json").write_text(pin.model_dump_json())
    (workspace / "research/queries.json").write_text(
        '[{"query_id":"states","variants":["state","states"],"note":"fixture"}]'
    )
    import_corpus(source, workspace / "local_data/corpus", pin)
    with chdir(workspace):
        first = CliRunner().invoke(
            app,
            [
                "corpus-statistics",
                "--corpus",
                "local_data/corpus",
                "--output",
                "analysis_output/stats.json",
            ],
        )
        assert first.exit_code == 0, first.output
        original = (workspace / "analysis_output/stats.json").read_bytes()
        result = json.loads(original)
        assert result["primary_source_units"] == 1
        assert result["queries"][0]["copy_retaining"]["occurrences"] == 3
        repeated = CliRunner().invoke(
            app,
            [
                "corpus-statistics",
                "--corpus",
                "local_data/corpus",
                "--output",
                "analysis_output/stats.json",
            ],
        )
    assert repeated.exit_code != 0
    assert (workspace / "analysis_output/stats.json").read_bytes() == original


def test_new_experiment_cli_reports_declared_and_distinct_counts(tmp_path):
    records = CASES
    cases = tmp_path / "cases.json"
    cases.write_text(TypeAdapter(tuple[Decision, ...]).dump_json(records[:1]).decode())
    with chdir(tmp_path):
        result = CliRunner().invoke(
            app,
            [
                "experiment-cases",
                "--cases",
                str(cases),
                "--output",
                "analysis_output/experiment.json",
            ],
        )
        assert result.exit_code == 0, result.output
        payload = json.loads((tmp_path / "analysis_output/experiment.json").read_text())
        assert payload["total_subsets"] == 4096
        assert payload["total_distinct_states"] == 1
        assert payload["decisions"][0]["minimal_bundles"] == [[]]
        refused = CliRunner().invoke(
            app, ["experiment-cases", "--cases", str(cases), "--output", "research/leak.json"]
        )
    assert refused.exit_code != 0
    assert not (tmp_path / "research/leak.json").exists()
